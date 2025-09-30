---
title: Magenta RT API
emoji: 🎵
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
app_file: main.py
pinned: false
app_port: 7860
hardware: l4x1
---

# 🎵 Magenta RT API

A production-ready REST API for music generation using Google's [Magenta RealTime](https://github.com/magenta/magenta-realtime) model. Generate high-quality music from text descriptions or audio style references.

## 🚀 Quick Start

### Interactive Documentation

Once the Space is running, visit:
- **Swagger UI**: `/docs` - Interactive API testing
- **ReDoc**: `/redoc` - Clean API documentation

### Example: Generate Music from Text

```bash
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/text" \
  -F "prompt=funky jazz groove with syncopated bass" \
  -F "duration=10" \
  --output generated.mp3
```

### Example: Style Transfer from Audio

```bash
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/audio" \
  -F "audio_file=@reference.mp3" \
  -F "duration=15" \
  -F "prompt=add electronic elements" \
  --output styled.mp3
```

### Example: Blend Multiple Styles

```bash
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/blend" \
  -F "text_prompts=funk,ambient,jazz" \
  -F "text_weights=2.0,1.5,1.0" \
  -F "duration=20" \
  --output blended.mp3
```

## 📋 Features

- 🎼 **Text-to-Music Generation** - Create music from natural language descriptions
- 🎧 **Audio Style Transfer** - Use existing audio as a style reference
- 🎛️ **Multi-Prompt Blending** - Combine multiple text and audio prompts with custom weights
- 🔌 **REST API** - Easy integration with any programming language
- ⚡ **GPU Accelerated** - Fast generation on NVIDIA A100 GPUs
- 📊 **Built-in Monitoring** - Prometheus metrics endpoint
- 🔒 **Security Features** - Optional API key authentication and rate limiting

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/text` | POST | Generate music from text prompt |
| `/generate/audio` | POST | Generate music from audio file reference |
| `/generate/blend` | POST | Blend multiple text/audio prompts |
| `/embed/text` | POST | Get MusicCoCa embedding for text |
| `/embed/audio` | POST | Get MusicCoCa embedding for audio |
| `/health` | GET | Health check endpoint |
| `/metrics` | GET | Prometheus metrics |

## 💻 Usage Examples

### Python

```python
import requests

def generate_music(prompt: str, duration: int = 10):
    url = "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/text"
    
    response = requests.post(
        url,
        data={
            "prompt": prompt,
            "duration": duration
        }
    )
    
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Music generated successfully!")
    else:
        print(f"❌ Error: {response.status_code}")

# Generate music
generate_music("epic orchestral cinematic soundtrack", duration=15)
```

### JavaScript

```javascript
async function generateMusic(prompt, duration = 10) {
  const formData = new FormData();
  formData.append('prompt', prompt);
  formData.append('duration', duration);
  
  const response = await fetch(
    'https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/text',
    {
      method: 'POST',
      body: formData
    }
  );
  
  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Play audio
    const audio = new Audio(url);
    audio.play();
    
    // Or download
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated.mp3';
    a.click();
  }
}

// Usage
generateMusic('dreamy ambient soundscape');
```

### cURL with Audio File

```bash
# Generate music styled after an audio reference
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/audio" \
  -F "audio_file=@my_favorite_song.mp3" \
  -F "duration=20" \
  -F "prompt=more energetic and upbeat" \
  -H "X-API-Key: your-api-key-if-enabled" \
  --output new_version.mp3
```

## 🎨 Prompt Examples

### Text Prompts

Great prompts are descriptive and combine multiple elements:

- `"funky jazz with syncopated bass and smooth saxophone"`
- `"ambient electronic soundscape with ethereal pads"`
- `"upbeat dance music with driving four-on-the-floor beat"`
- `"classical piano composition in the style of Chopin"`
- `"heavy metal with distorted guitars and double bass drums"`
- `"lo-fi hip hop beats with vinyl crackle and jazz samples"`
- `"epic orchestral cinematic soundtrack with strings and brass"`
- `"tropical house with steel drums and marimba"`
- `"psychedelic rock with reverb-drenched guitars"`
- `"90s eurodance with synth leads and energetic vocals"`

### Blending Prompts

Combine different styles with custom weights:

```bash
# 60% funk, 30% ambient, 10% jazz
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/blend" \
  -F "text_prompts=funk groove,ambient soundscape,smooth jazz" \
  -F "text_weights=3.0,1.5,0.5" \
  -F "duration=15"
```

## ⚙️ Configuration

### Environment Variables

Configure the API by setting environment variables in your Space settings:

```bash
# Authentication (optional)
ENABLE_AUTH=true
API_KEYS=key1,key2,key3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# Generation Limits
MAX_DURATION=120
MAX_FILE_SIZE_MB=50

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

### Using API Keys

If authentication is enabled, include your API key in requests:

```bash
curl -X POST "https://YOUR_USERNAME-magenta-rt-api.hf.space/generate/text" \
  -H "X-API-Key: your-api-key" \
  -F "prompt=ambient music" \
  -F "duration=10"
```

## 📊 Performance

### Generation Speed (on A100 40GB)

| Duration | Generation Time | Ratio to Realtime |
|----------|----------------|-------------------|
| 2s | ~5s | 2.5x |
| 10s | ~15s | 1.5x |
| 30s | ~40s | 1.3x |
| 60s | ~75s | 1.25x |

**Note**: First request includes model loading time (~30-60 seconds)

### Resource Usage

- **GPU Memory**: 12-15GB during inference
- **Model Size**: ~8GB on disk
- **Recommended Hardware**: A100 40GB or larger

## 🔧 Troubleshooting

### Space is Starting

First startup takes **10-15 minutes** to:
1. Build Docker container (~5 min)
2. Download Magenta RT models (~5-10 min)
3. Initialize models (~2-3 min)

Check the Space logs to monitor progress.

### Generation is Slow

- **First request**: Includes model loading (~30-60s)
- **Subsequent requests**: ~1.5x realtime
- **Solution**: Keep the Space active or use Persistent Storage

### Out of Memory Error

- Upgrade to **A100 80GB** hardware
- Reduce `MAX_DURATION` limit
- Process requests sequentially

### Connection Timeout

Increase your client timeout for long generations:

```python
response = requests.post(url, data=data, timeout=300)  # 5 minutes
```

## 🛡️ Rate Limits & Quotas

Default limits (configurable):

- **10 requests per minute** per IP address
- **100 requests per hour** per IP address
- **Maximum duration**: 120 seconds per generation
- **Maximum file size**: 50MB for audio uploads

## 📚 Technical Details

### Model Information

- **Base Model**: Magenta RealTime (Google Research)
- **Architecture**: Transformer-based audio generation
- **Audio Codec**: SpectroStream (discrete codec, 48kHz stereo)
- **Style Encoder**: MusicCoCa (joint text-audio embeddings)
- **Context Length**: 10 seconds
- **Chunk Size**: 2 seconds (with crossfading)

### Supported Audio Formats

**Input** (for audio style transfer):
- MP3, WAV, OGG, FLAC, M4A

**Output**:
- MP3 (high-quality, stereo, 48kHz)

## 🔗 Resources

- **Magenta RT GitHub**: https://github.com/magenta/magenta-realtime
- **Research Paper**: https://arxiv.org/abs/2508.04651
- **Blog Post**: https://g.co/magenta/rt
- **Model Card**: https://github.com/magenta/magenta-realtime/blob/main/MODEL.md

## 🤝 Contributing

Found a bug or want to contribute? 

- Report issues on the [GitHub repository](https://github.com/magenta/magenta-realtime/issues)
- Submit pull requests with improvements
- Share your generated music and prompts!

## 📄 License

This API service is built on Magenta RealTime:

- **API Code**: Apache 2.0 License
- **Magenta RT Code**: Apache 2.0 License
- **Model Weights**: Creative Commons Attribution 4.0 International (CC-BY 4.0)

### Usage Terms

Copyright 2025 Google LLC

**You must**:
- Use responsibly and ethically
- Not generate content that infringes on others' rights
- Not generate copyrighted content without permission

**Google claims no rights** in outputs you generate using this API. You and your users are solely responsible for outputs and their subsequent uses.

See the [full license](https://github.com/magenta/magenta-realtime/blob/main/LICENSE) for details.

## 🎓 Citation

If you use this API in research, please cite:

```bibtex
@article{gdmlyria2025live,
  title={Live Music Models},
  author={Caillon, Antoine and McWilliams, Brian and Tarakajian, Cassie and Simon, Ian and Manco, Ilaria and Engel, Jesse and Constant, Noah and Li, Pen and Denk, Timo I. and Lalama, Alberto and Agostinelli, Andrea and Huang, Anna and Manilow, Ethan and Brower, George and Erdogan, Hakan and Lei, Heidi and Rolnick, Itai and Grishchenko, Ivan and Orsini, Manu and Kastelic, Matej and Zuluaga, Mauricio and Verzetti, Mauro and Dooley, Michael and Skopek, Ondrej and Ferrer, Rafael and Borsos, Zalán and van den Oord, Aäron and Eck, Douglas and Collins, Eli and Baldridge, Jason and Hume, Tom and Donahue, Chris and Han, Kehang and Roberts, Adam},
  journal={arXiv:2508.04651},
  year={2025}
}
```

## 💬 Support

For questions and support:

- 📖 Check the `/docs` endpoint for detailed API documentation
- 🐛 Report bugs on [GitHub Issues](https://github.com/magenta/magenta-realtime/issues)
- 💡 Join discussions in the HuggingFace community
- 📧 Contact the Space owner for deployment-specific questions

## 🎉 Acknowledgments

Built with:
- [Magenta RealTime](https://github.com/magenta/magenta-realtime) by Google Research
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [HuggingFace Spaces](https://huggingface.co/spaces) for hosting

---

**Ready to create amazing music?** 🎵 Visit `/docs` to get started!
