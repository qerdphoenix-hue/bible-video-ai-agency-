# 📖 Bible Video AI Agency

An intelligent AI-powered system that automatically generates engaging videos from Bible text and distributes them across multiple social media platforms (YouTube, TikTok, Instagram, etc.).

## 🎯 Features

- **📚 Bible Text Processing** - Automatic parsing and segmentation of Bible passages
- **🎬 AI Video Generation** - Generate professional videos with AI-generated voiceovers and visual effects
- **📱 Multi-Platform Distribution** - Automatically post to YouTube, TikTok, Instagram, Twitter/X, and more
- **🤖 Intelligent Content Enhancement** - NLP-powered passage selection, commentary, and optimization
- **⏰ Automated Scheduling** - Schedule video generation and posting at optimal times
- **📊 Analytics Dashboard** - Track video performance, engagement, and reach across platforms
- **🔄 Continuous Generation** - Auto-generate new content on a schedule
- **🎨 Customizable Templates** - Choose from multiple video styles and templates

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- API Keys for:
  - OpenAI (GPT-4 for NLP processing)
  - ElevenLabs or Google TTS (for voiceovers)
  - D-ID or Synthesia (for video generation)
  - Social media platforms (YouTube, TikTok, Instagram, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/qerdphoenix-hue/bible-video-ai-agency.git
cd bible-video-ai-agency

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📋 Project Structure

```
bible-video-ai-agency/
├── src/
│   ├── bible_processor/          # Bible text parsing & processing
│   │   ├── __init__.py
│   │   ├── parser.py            # Parse Bible text
│   │   ├── segmenter.py         # Break text into video segments
│   │   └── validator.py         # Validate Bible references
│   ├── video_generator/         # AI video generation
│   │   ├── __init__.py
│   │   ├── generator.py         # Main video generation logic
│   │   ├── voiceover.py         # TTS voiceover generation
│   │   ├── templates.py         # Video templates
│   │   └── effects.py           # Visual effects & transitions
│   ├── social_media/            # Multi-platform posting
│   │   ├── __init__.py
│   │   ├── base.py              # Base social media interface
│   │   ├── youtube.py           # YouTube API integration
│   │   ├── tiktok.py            # TikTok API integration
│   │   ├── instagram.py         # Instagram API integration
│   │   ├── twitter.py           # Twitter/X API integration
│   │   └── scheduler.py         # Post scheduling
│   ├── nlp_engine/              # NLP processing
│   │   ├── __init__.py
│   │   ├── enhancer.py          # Content enhancement
│   │   ├── summarizer.py        # Passage summarization
│   │   └── tagger.py            # Tagging & categorization
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging setup
│   │   └── helpers.py           # Helper functions
│   └── api/                     # FastAPI application
│       ├── __init__.py
│       ├── main.py              # API entry point
│       ├── routes.py            # API endpoints
│       └── models.py            # Pydantic models
├── config/
│   ├── default.yaml             # Default configuration
│   ├── templates/               # Video templates
│   └── styles/                  # Visual styles
├── data/
│   ├── bible_texts/             # Bible text files
│   ├── generated_videos/        # Output videos
│   └── metadata/                # Video metadata
├── tests/
│   ├── __init__.py
│   ├── test_bible_processor.py
│   ├── test_video_generator.py
│   ├── test_social_media.py
│   └── conftest.py
├── docs/
│   ├── setup.md
│   ├── api.md
│   ├── deployment.md
│   └── configuration.md
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Docker compose configuration
├── Dockerfile                   # Docker image definition
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── main.py                      # CLI entry point
```

## 🔧 Configuration

Create a `.env` file based on `.env.example`:

```env
# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4

# Text-to-Speech
TTS_PROVIDER=elevenlabs  # or google, azure
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=default

# Video Generation
VIDEO_PROVIDER=did  # or synthesia, runway
DID_API_KEY=your_api_key_here

# Social Media
YOUTUBE_API_KEY=your_api_key_here
TIKTOK_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_ACCESS_TOKEN=your_access_token_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bible_ai

# Redis
REDIS_URL=redis://localhost:6379

# Scheduling
SCHEDULER_INTERVAL_HOURS=24
```

## 📚 Usage

### Command Line Interface

```bash
# Generate a video from a Bible passage
python main.py generate --book "John" --chapter 3 --verses "16-18"

# Generate and post to all platforms
python main.py generate-and-post --book "Psalm" --chapter 23 --platforms youtube,tiktok,instagram

# Schedule daily video generation
python main.py schedule --frequency daily --time "09:00"

# View analytics
python main.py analytics --period last_week
```

### API Endpoints

```bash
# Generate a video
POST /api/v1/videos/generate
{
  "book": "John",
  "chapter": 3,
  "verses": "16-18",
  "language": "en",
  "voice_id": "default"
}

# Post to social media
POST /api/v1/videos/{video_id}/post
{
  "platforms": ["youtube", "tiktok", "instagram"],
  "scheduled_time": "2024-01-15T09:00:00Z"
}

# Get analytics
GET /api/v1/analytics?period=last_week
```

## 🛠️ Development

### Running Tests

```bash
pytest
pytest --cov=src  # With coverage
pytest -v         # Verbose output
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## 🚀 Deployment

### Docker Deployment

```bash
docker-compose up -d
docker-compose logs -f
```

### Kubernetes

See [deployment.md](docs/deployment.md) for Kubernetes setup.

### Cloud Platforms

- **AWS**: Lambda + S3 + API Gateway
- **Google Cloud**: Cloud Run + Cloud Storage
- **Azure**: Container Instances + Blob Storage

## 📊 Architecture

```
┌─────────────────┐
│  Bible Text     │
│   Database      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Bible          │
│  Processor      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Engine     │
│  (Enhancement)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Video          │
│  Generator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Social Media   │─────▶│  YouTube     │
│  Distributor    │      ├──────────────┤
└────────┬────────┘      │  TikTok      │
         │               ├──────────────┤
         │               │  Instagram   │
         │               ├──────────────┤
         │               │  Twitter/X   │
         │               └──────────────┘
         │
         ▼
┌─────────────────┐
│  Analytics      │
│  Dashboard      │
└─────────────────┘
```

## 🔐 Security

- All API keys stored in environment variables
- OAuth2 authentication for social media APIs
- HTTPS encryption for all API calls
- Rate limiting on endpoints
- Input validation on all user inputs

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Support

For support, email support@biblevideoai.com or open an issue on GitHub.

## 🎉 Acknowledgments

- Bible text from public domain sources
- AI models powered by OpenAI
- Voice generation by ElevenLabs
- Video generation by D-ID

---

**Made with ❤️ for faith-based content creation**