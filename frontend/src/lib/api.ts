import { AnalysisResults, ChatMessage, ExportFormat } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class APIError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Add cache for analysis results
const analysisCache = new Map<string, Partial<AnalysisResults>>();

export async function getTranscript(videoUrl: string) {
  console.log('Calling getTranscript API...', videoUrl);
  const response = await fetch(`${API_BASE_URL}/transcript`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ video_url: videoUrl }),
  });

  console.log('Transcript API response status:', response.status);
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Transcript API error:', error);
    throw new Error(error.detail || 'Failed to fetch transcript');
  }

  const data = await response.json();
  console.log('Transcript API response data:', data);
  return data;
}

export async function analyzeVideo(
  videoUrl: string,
  onProgress?: (progress: number) => void,
  onPartialResults?: (results: Partial<AnalysisResults>) => void
): Promise<AnalysisResults> {
  console.log('Calling analyzeVideo API...', videoUrl);

  // Check cache first
  const cachedResult = analysisCache.get(videoUrl);
  if (cachedResult && Object.keys(cachedResult).length > 3) {
    console.log('Returning cached analysis results');
    return cachedResult as AnalysisResults;
  }

  try {
    // Start with quick analysis
    const quickResponse = await fetch(`${API_BASE_URL}/analyze/quick`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_url: videoUrl }),
    });

    if (!quickResponse.ok) {
      throw new APIError('QUICK_ANALYSIS_FAILED', 'Failed to get quick analysis');
    }

    const quickData = await quickResponse.json();
    onProgress?.(30);
    onPartialResults?.(quickData);

    // Start detailed analysis in parallel
    const [sentimentPromise, keyPointsPromise] = await Promise.all([
      fetch(`${API_BASE_URL}/analyze/sentiment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl }),
      }),
      fetch(`${API_BASE_URL}/analyze/keypoints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl }),
      })
    ]);

    onProgress?.(60);

    const [sentimentData, keyPointsData] = await Promise.all([
      sentimentPromise.json(),
      keyPointsPromise.json()
    ]);

    onProgress?.(90);

    const finalResults = {
      ...quickData,
      ...sentimentData,
      ...keyPointsData,
    };

    // Cache the results
    analysisCache.set(videoUrl, finalResults);
    onProgress?.(100);

    return finalResults;
  } catch (error) {
    onProgress?.(0);
    throw error;
  }
}

export async function chatWithVideo(
  videoId: string,
  message: string,
  history: ChatMessage[]
): Promise<string> {
  console.log('Calling chatWithVideo API...', videoId, message);
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

    console.log('Chat API response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('Chat API error:', error);
      throw new APIError(error.code || 'UNKNOWN_ERROR', error.message || 'Failed to get chat response');
    }

    const data = await response.json();
    console.log('Chat API response data:', data);
    return data.response;
  } catch (error) {
    console.error('Chat API catch block error:', error);
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
  console.log('Calling exportAnalysis API...', videoId, format);
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

    console.log('Export API response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('Export API error:', error);
      throw new APIError(error.code || 'UNKNOWN_ERROR', error.message || 'Failed to export analysis');
    }

    const data = await response.blob();
    console.log('Export API response data:', data);
    return data;
  } catch (error) {
    console.error('Export API catch block error:', error);
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('NETWORK_ERROR', 'Failed to connect to export service');
  }
}
