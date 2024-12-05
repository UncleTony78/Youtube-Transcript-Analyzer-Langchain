import { AnalysisResults, ChatMessage, ExportFormat } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class APIError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = 'APIError';
  }

  static isRateLimitError(error: any): boolean {
    return (
      error.message?.toLowerCase().includes('rate limit exceeded') ||
      error.code === '429' ||
      error.status === 429
    );
  }
}

// Add cache for analysis results
const analysisCache = new Map<string, Partial<AnalysisResults>>();

// Utility function for delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Generic fetch with retry logic
async function fetchWithRetry<T>(
  url: string,
  options: RequestInit,
  maxRetries: number = 3
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const error = await response.json();
        if (error.message?.toLowerCase().includes('rate limit exceeded')) {
          throw new APIError('RATE_LIMIT', error.message || 'Rate limit exceeded');
        }
        throw new APIError(response.status.toString(), error.detail || 'API request failed');
      }
      return await response.json();
    } catch (err: any) {
      lastError = err;
      if (err instanceof APIError && err.code === 'RATE_LIMIT') {
        // For rate limit errors, wait longer
        const waitTime = Math.min(1000 * Math.pow(2, attempt), 60000); // Max 1 minute
        console.log(`Rate limit hit, waiting ${waitTime}ms before retry...`);
        await delay(waitTime);
      } else {
        // For other errors, use shorter delays
        await delay(1000 * Math.pow(2, attempt));
      }
    }
  }
  
  throw lastError || new Error('Request failed after retries');
}

export async function getTranscript(videoUrl: string) {
  console.log('Calling getTranscript API...', videoUrl);
  const response = await fetchWithRetry(`${API_BASE_URL}/transcript`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ video_url: videoUrl }),
  });

  console.log('Transcript API response data:', response);
  return response;
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
    const quickResponse = await fetchWithRetry(`${API_BASE_URL}/analyze/quick`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_url: videoUrl }),
    });

    onProgress?.(30);
    onPartialResults?.(quickResponse);

    // Start detailed analysis in parallel
    const [sentimentPromise, keyPointsPromise] = await Promise.all([
      fetchWithRetry(`${API_BASE_URL}/analyze/sentiment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl }),
      }),
      fetchWithRetry(`${API_BASE_URL}/analyze/keypoints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl }),
      })
    ]);

    onProgress?.(60);

    const [sentimentData, keyPointsData] = await Promise.all([
      sentimentPromise,
      keyPointsPromise
    ]);

    onProgress?.(90);

    const finalResults = {
      ...quickResponse,
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
    const response = await fetchWithRetry(`${API_BASE_URL}/chat`, {
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

    console.log('Chat API response data:', response);
    return response.response;
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
    const response = await fetchWithRetry(`${API_BASE_URL}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        format: format.type,
      }),
    }, 1); // Set max retries to 1 for export API

    console.log('Export API response data:', response);
    return response;
  } catch (error) {
    console.error('Export API catch block error:', error);
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('NETWORK_ERROR', 'Failed to connect to export service');
  }
}
