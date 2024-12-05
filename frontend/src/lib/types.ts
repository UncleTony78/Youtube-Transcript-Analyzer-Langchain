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

export interface AnalysisResults {
  transcript?: TranscriptSegment[]
  keyPoints?: string[]
  sentiment?: SentimentData
  summary?: string
}

export interface ExportFormat {
  type: "pdf" | "txt"
  filename: string
}

export interface AnalysisError {
  code: string
  message: string
}
