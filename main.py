"""
Magenta RT API Service
A FastAPI service for audio generation using Magenta RealTime model
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import tempfile
import os
import numpy as np
from pathlib import Path
import logging
import uvicorn

# Import Magenta RT components
from magenta_rt import audio, system, musiccoca

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Magenta RT API",
    description="API for music generation using Magenta RealTime",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances (loaded once at startup)
mrt_model = None
style_model = None

class GenerationRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Text prompt for style conditioning")
    duration: int = Field(10, ge=2, le=120, description="Duration in seconds (2-120)")
    audio_weight: float = Field(1.0, ge=0.0, le=10.0, description="Weight for audio prompt")
    text_weight: float = Field(1.0, ge=0.0, le=10.0, description="Weight for text prompt")

class BlendRequest(BaseModel):
    prompts: List[dict] = Field(..., description="List of {weight, prompt/type} dicts")
    duration: int = Field(10, ge=2, le=120)

@app.on_event("startup")
async def load_models():
    """Load models on startup"""
    global mrt_model, style_model
    try:
        logger.info("Loading Magenta RT models...")
        mrt_model = system.MagentaRT()
        style_model = musiccoca.MusicCoCa()
        logger.info("Models loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model": "Magenta RealTime",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check with model status"""
    return {
        "status": "healthy",
        "models_loaded": mrt_model is not None and style_model is not None
    }

@app.post("/generate/text")
async def generate_from_text(
    prompt: str = Form(..., description="Text prompt (e.g., 'funk', 'ambient synth')"),
    duration: int = Form(10, ge=2, le=120)
):
    """
    Generate music from a text prompt
    
    Args:
        prompt: Text description of desired music style
        duration: Length of generation in seconds
    
    Returns:
        Audio file (MP3)
    """
    try:
        logger.info(f"Generating {duration}s audio from text: {prompt}")
        
        # Embed text prompt
        style = system.embed_style(prompt)
        
        # Generate audio chunks
        chunks = []
        state = None
        num_chunks = round(duration / mrt_model.config.chunk_length)
        
        for i in range(num_chunks):
            state, chunk = mrt_model.generate_chunk(state=state, style=style)
            chunks.append(chunk)
            logger.info(f"Generated chunk {i+1}/{num_chunks}")
        
        # Concatenate with crossfading
        generated = audio.concatenate(chunks, crossfade_time=mrt_model.crossfade_length)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            generated.to_file(tmp.name)
            output_path = tmp.name
        
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"magenta_rt_{prompt.replace(' ', '_')[:30]}.mp3",
            background=None
        )
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/audio")
async def generate_from_audio(
    audio_file: UploadFile = File(..., description="Audio file for style reference"),
    duration: int = Form(10, ge=2, le=120),
    prompt: Optional[str] = Form(None, description="Optional text prompt to blend with audio")
):
    """
    Generate music from an audio file prompt (with optional text blending)
    
    Args:
        audio_file: Input audio file for style conditioning
        duration: Length of generation in seconds
        prompt: Optional text prompt to blend with audio style
    
    Returns:
        Audio file (MP3)
    """
    try:
        logger.info(f"Generating {duration}s audio from uploaded file")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load audio
        input_audio = audio.Waveform.from_file(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Embed audio style
        if prompt:
            # Blend audio and text
            weighted_styles = [
                (1.0, input_audio),
                (1.0, prompt)
            ]
            weights = np.array([w for w, _ in weighted_styles])
            styles = style_model.embed([s for _, s in weighted_styles])
            weights_norm = weights / weights.sum()
            style = (weights_norm[:, np.newaxis] * styles).mean(axis=0)
            logger.info(f"Blending audio with text: {prompt}")
        else:
            style = style_model.embed([input_audio])[0]
        
        # Generate audio chunks
        chunks = []
        state = None
        num_chunks = round(duration / mrt_model.config.chunk_length)
        
        for i in range(num_chunks):
            state, chunk = mrt_model.generate_chunk(state=state, style=style)
            chunks.append(chunk)
            logger.info(f"Generated chunk {i+1}/{num_chunks}")
        
        # Concatenate with crossfading
        generated = audio.concatenate(chunks, crossfade_time=mrt_model.crossfade_length)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            generated.to_file(tmp.name)
            output_path = tmp.name
        
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"magenta_rt_audio_styled.mp3",
            background=None
        )
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/blend")
async def generate_blended(
    duration: int = Form(10, ge=2, le=120),
    text_prompts: Optional[str] = Form(None, description="Comma-separated text prompts"),
    text_weights: Optional[str] = Form(None, description="Comma-separated weights for text"),
    audio_files: Optional[List[UploadFile]] = File(None, description="Audio files for blending"),
    audio_weights: Optional[str] = Form(None, description="Comma-separated weights for audio")
):
    """
    Generate music by blending multiple text and/or audio prompts with custom weights
    
    Args:
        duration: Length of generation in seconds
        text_prompts: Comma-separated text prompts (e.g., "funk,ambient")
        text_weights: Comma-separated weights (e.g., "2.0,1.0")
        audio_files: List of audio files
        audio_weights: Comma-separated weights for audio files
    
    Returns:
        Audio file (MP3)
    """
    try:
        weighted_styles = []
        
        # Process text prompts
        if text_prompts:
            prompts = [p.strip() for p in text_prompts.split(',')]
            weights = [float(w.strip()) for w in text_weights.split(',')] if text_weights else [1.0] * len(prompts)
            
            if len(prompts) != len(weights):
                raise HTTPException(400, "Number of text prompts must match number of weights")
            
            for weight, prompt in zip(weights, prompts):
                weighted_styles.append((weight, prompt))
                logger.info(f"Added text prompt: {prompt} (weight: {weight})")
        
        # Process audio files
        if audio_files:
            audio_weight_list = [float(w.strip()) for w in audio_weights.split(',')] if audio_weights else [1.0] * len(audio_files)
            
            if len(audio_files) != len(audio_weight_list):
                raise HTTPException(400, "Number of audio files must match number of weights")
            
            for weight, audio_file in zip(audio_weight_list, audio_files):
                # Save and load audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp:
                    content = await audio_file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                input_audio = audio.Waveform.from_file(tmp_path)
                os.unlink(tmp_path)
                
                weighted_styles.append((weight, input_audio))
                logger.info(f"Added audio file: {audio_file.filename} (weight: {weight})")
        
        if not weighted_styles:
            raise HTTPException(400, "Must provide at least one text prompt or audio file")
        
        # Blend styles
        weights = np.array([w for w, _ in weighted_styles])
        styles = style_model.embed([s for _, s in weighted_styles])
        weights_norm = weights / weights.sum()
        blended_style = (weights_norm[:, np.newaxis] * styles).mean(axis=0)
        
        logger.info(f"Generating with {len(weighted_styles)} blended styles")
        
        # Generate audio chunks
        chunks = []
        state = None
        num_chunks = round(duration / mrt_model.config.chunk_length)
        
        for i in range(num_chunks):
            state, chunk = mrt_model.generate_chunk(state=state, style=blended_style)
            chunks.append(chunk)
            logger.info(f"Generated chunk {i+1}/{num_chunks}")
        
        # Concatenate with crossfading
        generated = audio.concatenate(chunks, crossfade_time=mrt_model.crossfade_length)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            generated.to_file(tmp.name)
            output_path = tmp.name
        
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"magenta_rt_blended.mp3",
            background=None
        )
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed/text")
async def embed_text(prompt: str = Form(...)):
    """
    Get the MusicCoCa embedding for a text prompt
    
    Returns:
        JSON with embedding array
    """
    try:
        style = system.embed_style(prompt)
        return JSONResponse({
            "prompt": prompt,
            "embedding": style.tolist(),
            "shape": list(style.shape)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed/audio")
async def embed_audio(audio_file: UploadFile = File(...)):
    """
    Get the MusicCoCa embedding for an audio file
    
    Returns:
        JSON with embedding array
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load and embed
        input_audio = audio.Waveform.from_file(tmp_path)
        os.unlink(tmp_path)
        
        embedding = style_model.embed([input_audio])[0]
        
        return JSONResponse({
            "filename": audio_file.filename,
            "embedding": embedding.tolist(),
            "shape": list(embedding.shape)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,  # HuggingFace Spaces default port
        reload=False
    )