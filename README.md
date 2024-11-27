# YouTube Transcript Analysis Tool

A powerful Python package for extracting and analyzing insights from YouTube video transcripts using advanced language processing techniques.

## Features

- Context-aware transcript analysis
- Sentiment analysis for video segments
- Key points extraction
- Comprehensive summary generation
- Multi-language support with automatic translation
- Integration with Google's Generative AI (Gemini)
- LangSmith monitoring and tracing

## Installation

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_API_KEY=your_google_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

## Usage

```python
from transcript_service import YouTubeService
from langchain_processor import TranscriptProcessor

# Initialize services
youtube_service = YouTubeService()
processor = TranscriptProcessor()

# Analyze a video
video_url = "https://www.youtube.com/watch?v=your_video_id"
results = processor.process_transcript(youtube_service.get_video_data(video_url))

# Access analysis results
print(results['context_analysis'])
print(results['final_summary'])
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── transcript_service.py
│   ├── langchain_processor.py
│   └── utils.py
└── tests/
    ├── __init__.py
    └── test_analysis.py
```

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run tests: `python -m pytest tests/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
