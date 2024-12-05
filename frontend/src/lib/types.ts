export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export interface TranscriptSegment {
  text: string
  timestamp: string
}

export interface KeyPoint {
  text: string
  category: string
  importance: 'high' | 'medium' | 'low'
}

export interface SentimentSegment {
  text: string
  sentiment: string
  timestamp: string
}

export interface SentimentData {
  positive: number
  negative: number
  neutral: number
  segments: SentimentSegment[]
}

export interface VideoMetadata {
  title?: string;
  duration?: string;
  resolution?: string;
  format?: string;
  videoId?: string;
}

export interface AnalysisResults {
  metadata?: VideoMetadata;
  transcript?: TranscriptSegment[]
  keyPoints?: KeyPoint[]
  sentiment?: SentimentData
  summary?: string
  insights?: any[]; 
}

export interface ExportFormat {
  type: "pdf" | "txt"
  filename: string
}

export interface AnalysisError {
  code: string
  message: string
}
