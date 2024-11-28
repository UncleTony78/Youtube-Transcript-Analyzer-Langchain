# YouTube Transcript Analysis Tool

> A powerful Python package leveraging AI to extract deep insights from YouTube video transcripts.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Context-Aware Analysis**: Understands video context for better insights
- **Sentiment Analysis**: Track emotional tone throughout the video
- **Key Points Extraction**: Automatically identify crucial moments
- **Smart Summarization**: Generate comprehensive, context-aware summaries
- **Vector Search**: Find relevant content using semantic search
- **Interactive Chat**: Engage in context-aware conversations about the video
- **Multi-Language Support**: Auto-translation to English
- **Google's Generative AI**: Powered by Gemini Pro
- **LangSmith Integration**: Advanced monitoring and tracing

## Getting Started

### Prerequisites

1. **Python Environment**
   - Python 3.8 or higher
   - pip (Python package installer)
   - virtualenv or conda (recommended)

2. **API Keys**
   - YouTube Data API key
   - Google API key (for Gemini Pro)
   - LangChain API key
   - Pinecone API key

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/UncleTony78/Youtube-Transcript-Analyzer-Langchain.git
   cd Youtube-Transcript-Analyzer-Langchain
   ```

2. **Create Virtual Environment**
   ```bash
   # Using virtualenv
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Unix or MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory with the following variables:

   ```env
   # Required API Keys (Never commit these to version control!)
   YOUTUBE_API_KEY=your_youtube_api_key
   GOOGLE_API_KEY=your_google_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key

   # LangChain Configuration
   LANGCHAIN_PROJECT=your_project_name
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

   # Pinecone Configuration
   PINECONE_INDEX=youtube-video-analysis  # or your custom index name
   PINECONE_ENVIRONMENT=your_environment  # e.g., "gcp-starter"

   # Optional: Development Settings
   DEBUG=false
   LOG_LEVEL=INFO
   ```

   ⚠️ **Security Note**: 
   - Never commit the `.env` file to version control
   - Keep your API keys secure and rotate them regularly
   - Use different API keys for development and production

### Quick Test

1. **Run the Test Pipeline**
   ```bash
   python src/test_pipeline.py
   ```
   This will analyze a sample video and demonstrate the tool's capabilities.

## Usage Guide

### Basic Usage

```python
from src.insight_engine import VideoInsightEngine
from src.transcript_service import YouTubeService

# Initialize services
youtube_service = YouTubeService()
insight_engine = VideoInsightEngine()

# Analyze a video
video_url = "https://www.youtube.com/watch?v=your_video_id"

# Get video data
video_id = youtube_service.extract_video_id(video_url)
metadata = youtube_service.get_video_metadata(video_id)
transcript = youtube_service.get_transcript(video_id)

# Process and analyze
analysis = insight_engine.analyze_transcript(transcript, metadata)
```

### Advanced Features

#### Vector Search
```python
# Search for specific content
results = insight_engine.query_video_insights(
    "What are the main points about...?",
    video_id=video_id
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Timestamp: {result['timestamp']}s")
    print(f"Relevance: {result['score']:.2f}")
```

#### Interactive Chat
```python
# Create chat interface
chat_chain = insight_engine.create_chat_interface()

# Ask questions about the video
response = chat_chain({
    "question": "Can you explain the key concepts discussed in the video?"
})
print(response['answer'])
```

## Project Structure

```
.
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── transcript_service.py      # YouTube API and transcript handling
│   ├── insight_engine.py         # Core analysis engine
│   ├── analysis_utils.py         # Helper functions and utilities
│   ├── langchain_processor.py    # LangChain integration
│   └── main.py                   # Main application logic
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_transcript_service.py # Service unit tests
├── analyze_video.py             # Video analysis script
├── run_analysis.py             # Analysis execution script
├── test_pipeline.py            # Integration test pipeline
├── setup.py                    # Package setup and metadata
├── requirements.txt            # Project dependencies
├── .env                        # Environment configuration
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
└── CHANGELOG.md               # Version history
```

## Development

### Setting Up Development Environment

1. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

3. **Run Tests**
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run with coverage
   python -m pytest --cov=src tests/
   ```

4. **Code Formatting**
   ```bash
   # Format code
   black src/ tests/
   
   # Check style
   flake8 src/ tests/
   ```

### Contributing Guidelines

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Follow the code style guidelines
4. Write tests for new features
5. Update documentation as needed
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Error Handling

The package includes comprehensive error handling for:

### API and Network
- Missing/invalid API keys
- Network connectivity issues
- Rate limiting
- Failed API requests

### Data Processing
- Invalid video URLs
- Missing transcripts
- Language processing errors
- Vector database operations

### Runtime
- Memory management
- Concurrent operations
- Resource cleanup
- Chat interface errors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google's Generative AI team for Gemini Pro
- LangChain for the excellent framework
- Pinecone for vector database services
- YouTube Data API team

---

<div align="center">
Made with ❤️ using Python and AI
</div>
