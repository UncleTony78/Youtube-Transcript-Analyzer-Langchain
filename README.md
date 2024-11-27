# 🎥 YouTube Transcript Analysis Tool

> A powerful Python package leveraging AI to extract deep insights from YouTube video transcripts.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🧠 **Context-Aware Analysis**: Understands video context for better insights
- 📊 **Sentiment Analysis**: Track emotional tone throughout the video
- 🎯 **Key Points Extraction**: Automatically identify crucial moments
- 📝 **Smart Summarization**: Generate comprehensive, context-aware summaries
- 🌍 **Multi-Language Support**: Auto-translation to English
- 🤖 **Google's Generative AI**: Powered by Gemini Pro
- 📈 **LangSmith Integration**: Advanced monitoring and tracing

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/UncleTony78/Youtube-Transcript-Analyzer-Langchain.git
cd Youtube-Transcript-Analyzer-Langchain

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Environment Setup

Create a `.env` file in the root directory:

```env
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_API_KEY=your_google_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=soomi-ai
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

## 📖 Usage

```python
from src.transcript_service import YouTubeService
from src.langchain_processor import TranscriptProcessor

# Initialize services
youtube_service = YouTubeService()
processor = TranscriptProcessor()

# Analyze a video
video_url = "https://www.youtube.com/watch?v=your_video_id"
results = processor.process_transcript(youtube_service.get_video_data(video_url))

# Access results
print(results['context_analysis'])  # Initial context analysis
print(results['final_summary'])     # Comprehensive summary
```

## 🏗️ Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── transcript_service.py    # YouTube API integration
│   └── langchain_processor.py   # AI processing logic
├── tests/
│   ├── __init__.py
│   └── test_analysis.py        # Test suite
├── README.md                   # This file
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
└── .env                       # Environment variables
```

## 🧪 Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run tests: `python -m pytest tests/`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🛡️ Error Handling

The package includes robust error handling for:
- Missing/invalid API keys
- Failed transcript retrieval
- Language processing errors
- Network connectivity issues
- Rate limiting

## 🔒 Security

- All API keys are managed via environment variables
- No sensitive data is logged or stored
- Secure error messages that don't expose system details

## 📈 Performance

- Efficient chunk-based processing
- Smart caching of API responses
- Optimized for production use
- Scalable architecture

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ using Python and AI
</div>
