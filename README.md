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
- **Multi-Format Export**: Export results in CSV, JSON, and PDF formats
- **Email Integration**: Automatically send results via email with attachments
- **Automated Reports**: Generate professional PDF reports with insights

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
   - Email configuration (for sending results)

### Email Configuration

To enable email functionality:

1. Copy `.env.example` to `.env`
2. Configure your email settings in `.env`:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_specific_password
   SENDER_EMAIL=your_email@gmail.com
   RECIPIENT_EMAIL=recipient@example.com
   ```

3. If using Gmail:
   - Enable 2-Step Verification in your Google Account
   - Generate an App Password: Google Account → Security → 2-Step Verification → App Passwords
   - Use the generated App Password in your `.env` file

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

## 🛠️ Component Setup Guide

### LangChain Setup

1. **Install LangChain**
   ```bash
   pip install langchain langchain-google-genai
   ```

2. **Configure LangChain**
   ```python
   from langchain_google_genai import ChatGoogleGenerativeAI
   from dotenv import load_dotenv
   import os

   # Load environment variables
   load_dotenv()

   # Initialize LLM
   llm = ChatGoogleGenerativeAI(
       model="gemini-pro",
       temperature=0.7,
       convert_system_message_to_human=True
   )
   ```

### LangSmith Integration

1. **Sign Up for LangSmith**
   - Visit [LangSmith](https://smith.langchain.com/)
   - Create an account and get your API key
   - Add API key to your `.env` file

2. **Enable Tracing**
   ```python
   import os
   from langsmith.run_helpers import traceable

   # Configure LangSmith
   os.environ["LANGCHAIN_TRACING_V2"] = "true"
   os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
   os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
   os.environ["LANGCHAIN_PROJECT"] = os.getenv('LANGCHAIN_PROJECT')

   # Use the @traceable decorator for function tracking
   @traceable(name="my_function")
   def my_function():
       pass
   ```

3. **View Traces**
   - Go to your LangSmith dashboard
   - Select your project
   - View traces, debugging info, and performance metrics

### Vector Embeddings Setup

1. **Install Required Packages**
   ```bash
   pip install sentence-transformers
   ```

2. **Initialize Embeddings**
   ```python
   from langchain.embeddings import HuggingFaceEmbeddings

   # Initialize embeddings (using a model with 1024 dimensions)
   embeddings = HuggingFaceEmbeddings(
       model_name="BAAI/bge-large-en-v1.5"
   )
   ```

3. **Generate Embeddings**
   ```python
   # Generate embeddings for a text
   text = "Your text here"
   embedding = embeddings.embed_query(text)

   # Generate embeddings for documents
   documents = ["Doc 1", "Doc 2"]
   doc_embeddings = embeddings.embed_documents(documents)
   ```

### Pinecone Setup

1. **Create Pinecone Account**
   - Visit [Pinecone](https://www.pinecone.io/)
   - Sign up for an account
   - Create a new project
   - Get your API key and environment

2. **Install Pinecone**
   ```bash
   pip install pinecone-client
   ```

3. **Create Index**
   - Go to Pinecone dashboard
   - Click "Create Index"
   - Set dimensions to 1024 (matching your embedding model)
   - Choose metric: "cosine"
   - Select cloud provider and region

4. **Initialize Pinecone**
   ```python
   from pinecone import Pinecone

   # Initialize client
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

   # Connect to index
   index = pc.Index(os.getenv('PINECONE_INDEX'))
   ```

5. **Store and Query Vectors**
   ```python
   # Store vectors
   index.upsert(
       vectors=[{
           "id": "vec1",
           "values": embedding,
           "metadata": {"text": "Original text"}
       }],
       namespace="my_namespace"
   )

   # Query vectors
   results = index.query(
       vector=query_embedding,
       top_k=3,
       include_values=True,
       include_metadata=True,
       namespace="my_namespace"
   )
   ```

### Integration Example

```python
from langchain.vectorstores import Pinecone as LangChainPinecone
from langchain.chains import ConversationalRetrievalChain

# Create vector store
vectorstore = LangChainPinecone(
    index,
    embeddings,
    "text"  # text key field in metadata
)

# Create retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Create chat chain
chat_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
)

# Use the chain
response = chat_chain({
    "question": "What insights can you share about this video?"
})
```

### Troubleshooting Tips

1. **Embedding Issues**
   - Ensure text is properly preprocessed
   - Check embedding dimensions match Pinecone index
   - Monitor token limits and batch sizes

2. **Pinecone Connection**
   - Verify API key and environment
   - Check index name and namespace
   - Monitor rate limits and quotas

3. **LangChain Integration**
   - Enable debug logging
   - Check chain input/output formats
   - Monitor memory usage

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

We love your input! We want to make contributing as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

#### Development Process

1. Fork the repo and create your branch:
   ```bash
   # Clone your fork
   git clone https://github.com/<your-username>/Youtube-Transcript-Analyzer-Langchain.git
   
   # Create a feature branch
   git checkout -b feature/my-awesome-feature
   # or for bugfixes
   git checkout -b fix/issue-description
   ```

2. Set up development environment:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. Make your changes:
   - Follow our coding style (Black + isort)
   - Add or update tests as needed
   - Update documentation to reflect your changes
   - Add your changes to CHANGELOG.md under [Unreleased]

4. Test your changes:
   ```bash
   # Run tests
   pytest
   
   # Run linters
   black .
   isort .
   flake8
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add awesome new feature"
   git push origin feature/my-awesome-feature
   ```

6. Open a Pull Request:
   - Fill in the provided PR template
   - Link any relevant issues
   - Provide clear description of your changes
   - Request review from maintainers

#### Code Style Guidelines

- Use [Black](https://github.com/psf/black) for code formatting
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Write meaningful commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
- Document your code using Google-style docstrings

## Error Handling

Our error handling system is designed to provide robust, informative, and recoverable error management across all operations.

### API & Network Layer

#### Request Management
- Automatic retry with exponential backoff for transient failures
- Rate limit handling with smart throttling
- Connection pooling and timeout management
- Detailed error reporting with request/response context

#### Authentication & Authorization
- Graceful handling of expired/invalid credentials
- Automatic token refresh mechanisms
- Clear error messages for permission issues
- Fallback mechanisms for API unavailability

### Data Processing Layer

#### Input Validation
- Comprehensive URL format validation
- Content type and size verification
- Language support checking
- Metadata completeness validation

#### Content Processing
- Transcript availability checks
- Language detection and translation fallbacks
- Chunk size optimization
- Memory usage monitoring and management

#### Vector Operations
- Index existence verification
- Embedding dimension validation
- Query format validation
- Results post-processing and filtering

### Runtime Management

#### Resource Optimization
- Memory usage monitoring
- Garbage collection optimization
- Connection pool management
- Cache invalidation strategies

#### Concurrent Operations
- Thread safety mechanisms
- Deadlock prevention
- Resource contention handling
- Queue management for parallel processing

#### System Integration
- Clean process termination
- Resource cleanup on shutdown
- State persistence
- Recovery from partial failures

#### User Interface
- Informative error messages
- Progress indication
- Operation cancellation support
- Session management

### Error Recovery Strategies

1. **Automatic Recovery**
   - Retry mechanisms for transient failures
   - Fallback options for critical operations
   - State restoration capabilities
   - Alternative service routing

2. **Manual Intervention**
   - Clear error documentation
   - Troubleshooting guides
   - Support contact information
   - Debug log access

3. **Monitoring & Logging**
   - Structured error logging
   - Performance metrics tracking
   - Usage statistics
   - Health checks and alerts

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
