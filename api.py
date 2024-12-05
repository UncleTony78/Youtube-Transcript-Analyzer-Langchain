from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from src.main import VideoAnalyzer
from src.export_service import ExportService
from datetime import datetime
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import asyncio
from functools import lru_cache
import openai

# Configure SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Suppress only the single InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

app = FastAPI(title="YouTube Transcript Analysis API")

# Configure CORS for our Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use our existing services
analyzer = VideoAnalyzer()
export_service = ExportService()

# Cache for analysis results
analysis_cache = {}

class VideoRequest(BaseModel):
    video_url: str

class ChatRequest(BaseModel):
    video_id: str
    message: str
    history: List[dict]

class ExportRequest(BaseModel):
    video_id: str
    format: str

class AnalysisResponse(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    transcript: Optional[List[Dict[str, Any]]] = None
    keyPoints: Optional[List[str]] = None
    sentiment: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None

class RateLimitException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=429,
            detail=detail
        )

def handle_openai_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except openai.error.RateLimitError as e:
            raise RateLimitException(detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper

@app.post("/transcript")
async def get_transcript(request: VideoRequest):
    try:
        results = analyzer.get_transcript(request.video_url)
        return results
    except Exception as e:
        error_msg = str(e)
        if "EOF occurred in violation of protocol" in error_msg:
            error_msg = "Connection error while fetching video data. Please try again."
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/analyze/quick")
async def quick_analysis(request: VideoRequest) -> AnalysisResponse:
    """Quick initial analysis returning transcript and metadata."""
    try:
        # Check cache first
        if request.video_url in analysis_cache:
            cached_data = analysis_cache[request.video_url]
            return AnalysisResponse(
                metadata=cached_data.get('metadata'),
                transcript=cached_data.get('transcript')
            )

        # Get fresh data
        result = analyzer.get_transcript(request.video_url)
        
        # Cache the result
        if request.video_url not in analysis_cache:
            analysis_cache[request.video_url] = {}
        analysis_cache[request.video_url].update({
            'metadata': result['metadata'],
            'transcript': result['transcript']
        })
        
        return AnalysisResponse(
            metadata=result['metadata'],
            transcript=result['transcript']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment")
@handle_openai_error
async def analyze_sentiment(request: VideoRequest) -> AnalysisResponse:
    """Analyze sentiment separately."""
    try:
        # Check cache first
        if request.video_url in analysis_cache and 'sentiment' in analysis_cache[request.video_url]:
            return AnalysisResponse(sentiment=analysis_cache[request.video_url]['sentiment'])

        # Get sentiment analysis
        sentiment = await asyncio.to_thread(analyzer.analyze_sentiment, request.video_url)
        
        # Cache the result
        if request.video_url not in analysis_cache:
            analysis_cache[request.video_url] = {}
        analysis_cache[request.video_url]['sentiment'] = sentiment
        
        return AnalysisResponse(sentiment=sentiment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/keypoints")
@handle_openai_error
async def analyze_keypoints(request: VideoRequest) -> AnalysisResponse:
    """Analyze key points separately."""
    try:
        # Check cache first
        if request.video_url in analysis_cache and 'keyPoints' in analysis_cache[request.video_url]:
            return AnalysisResponse(keyPoints=analysis_cache[request.video_url]['keyPoints'])

        # Get key points analysis
        key_points = await asyncio.to_thread(analyzer.extract_key_points, request.video_url)
        
        # Cache the result
        if request.video_url not in analysis_cache:
            analysis_cache[request.video_url] = {}
        analysis_cache[request.video_url]['keyPoints'] = key_points
        
        return AnalysisResponse(keyPoints=key_points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep the original analyze endpoint for compatibility
@app.post("/analyze")
async def analyze_video(request: VideoRequest) -> AnalysisResponse:
    """Full analysis endpoint that coordinates all analysis tasks."""
    try:
        # Check complete cache first
        if request.video_url in analysis_cache and len(analysis_cache[request.video_url].keys()) >= 4:
            return AnalysisResponse(**analysis_cache[request.video_url])

        # Run all analyses in parallel
        quick_result = await quick_analysis(request)
        sentiment_task = asyncio.create_task(analyze_sentiment(request))
        keypoints_task = asyncio.create_task(analyze_keypoints(request))
        
        # Wait for all tasks to complete
        sentiment_result, keypoints_result = await asyncio.gather(
            sentiment_task,
            keypoints_task
        )
        
        # Combine all results
        final_result = {
            'metadata': quick_result.metadata,
            'transcript': quick_result.transcript,
            'sentiment': sentiment_result.sentiment,
            'keyPoints': keypoints_result.keyPoints
        }
        
        # Cache the complete result
        analysis_cache[request.video_url] = final_result
        
        return AnalysisResponse(**final_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
@handle_openai_error
async def chat(request: ChatRequest):
    try:
        response = analyzer.chat_with_video(
            request.video_id,
            request.message,
            request.history
        )
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_analysis(request: ExportRequest):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{request.video_id}_{timestamp}"
        
        if request.format == "pdf":
            file_path = export_service.export_to_pdf(filename)
        elif request.format == "txt":
            file_path = export_service.export_to_text(filename)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
        return {"file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    try:
        # Ensure the file path is within our exports directory
        full_path = os.path.join("exports", file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=full_path,
            filename=os.path.basename(file_path),
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
