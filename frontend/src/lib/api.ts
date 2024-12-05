import { AnalysisResults, ChatMessage, ExportFormat } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class APIError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

export async function analyzeVideo(videoUrl: string): Promise<AnalysisResults> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_url: videoUrl }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new APIError(error.code || 'UNKNOWN_ERROR', error.message || 'Failed to analyze video');
    }

    const data = await response.json();
    return {
      ...data,
      keyPoints: data.keyPoints?.map((kp: { text: string }) => kp.text),
    };
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('NETWORK_ERROR', 'Failed to connect to analysis service');
  }
}

export async function chatWithVideo(
  videoId: string,
  message: string,
  history: ChatMessage[]
): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        message,
        history: history.map(msg => ({
          role: msg.role,
          content: msg.content,
        })),
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new APIError(error.code || 'UNKNOWN_ERROR', error.message || 'Failed to get chat response');
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('NETWORK_ERROR', 'Failed to connect to chat service');
  }
}

export async function exportAnalysis(
  videoId: string,
  format: ExportFormat
): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        format: format.type,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new APIError(error.code || 'UNKNOWN_ERROR', error.message || 'Failed to export analysis');
    }

    return await response.blob();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('NETWORK_ERROR', 'Failed to connect to export service');
  }
}
