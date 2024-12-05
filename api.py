from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
from src.main import VideoAnalyzer
from src.export_service import ExportService
from datetime import datetime

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

class VideoRequest(BaseModel):
    video_url: str

class ChatRequest(BaseModel):
    video_id: str
    message: str
    history: List[dict]

class ExportRequest(BaseModel):
    video_id: str
    format: str

@app.post("/analyze")
async def analyze_video(request: VideoRequest):
    try:
        results = analyzer.analyze_video(request.video_url)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = analyzer.chat_with_video(
            request.video_id,
            request.message,
            request.history
        )
        return {"response": response}
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
