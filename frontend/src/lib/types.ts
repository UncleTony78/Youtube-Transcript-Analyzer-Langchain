export interface AnalysisResults {
  transcript: string[];
  keyPoints: string[];
  sentiment: {
    positive: number;
    negative: number;
    neutral: number;
    segments: Array<{
      text: string;
      sentiment: string;
      timestamp: string;
    }>;
  };
  summary: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ExportFormat {
  type: "pdf" | "txt" | "json";
  filename: string;
}

export type AnalysisError = {
  message: string;
  code: string;
}
