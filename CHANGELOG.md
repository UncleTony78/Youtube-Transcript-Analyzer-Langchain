# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Modified golden nuggets extraction to be more flexible (removed fixed 3-nugget limit)

## [0.1.0] - 2024-01-09

### Added
- Initial project setup with core functionality
- VideoInsightEngine implementation
  - AI-powered video content analysis
  - Vector database integration
  - Sentiment and context-aware processing
  - Golden nugget extraction
  - Comprehensive summary generation
  - Fact-checking capabilities
  - Interactive chat interface
- Analysis utilities
  - Transcript chunking
  - Sentiment analysis
  - Key phrase extraction
  - Timestamp formatting
  - Insight deduplication
- Integration with external services
  - Google's Generative AI (Gemini Pro)
  - Pinecone vector database
  - LangChain for processing
  - LangSmith for tracing

### Dependencies
- google-generativeai>=0.3.0
- langchain>=0.1.0
- pinecone-client>=2.2.4
- youtube-transcript-api>=0.6.1
- textblob>=0.17.1

[Unreleased]: https://github.com/UncleTony78/Youtube-Transcript-Analyzer-Langchain/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/UncleTony78/Youtube-Transcript-Analyzer-Langchain/releases/tag/v0.1.0
