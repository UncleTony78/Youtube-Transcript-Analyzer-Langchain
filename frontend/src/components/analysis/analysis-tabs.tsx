import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TranscriptView } from "./transcript-view"
import { KeyPointsView } from "./key-points-view"
import { SentimentView } from "./sentiment-view"
import { SummaryView } from "./summary-view"
import { ChatView } from "./chat-view"

interface AnalysisTabsProps {
  videoId: string
  analysisData?: {
    transcript?: string[]
    keyPoints?: string[]
    sentiment?: {
      positive: number
      negative: number
      neutral: number
      segments: Array<{ text: string; sentiment: string; timestamp: string }>
    }
    summary?: string
  }
}

export function AnalysisTabs({ videoId, analysisData }: AnalysisTabsProps) {
  return (
    <Tabs defaultValue="transcript" className="w-full max-w-4xl mx-auto">
      <TabsList className="grid w-full grid-cols-5">
        <TabsTrigger value="transcript">Transcript</TabsTrigger>
        <TabsTrigger value="keypoints">Key Points</TabsTrigger>
        <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
        <TabsTrigger value="summary">Summary</TabsTrigger>
        <TabsTrigger value="chat">Chat</TabsTrigger>
      </TabsList>
      <div className="mt-6">
        <TabsContent value="transcript">
          <TranscriptView transcript={analysisData?.transcript} />
        </TabsContent>
        <TabsContent value="keypoints">
          <KeyPointsView keyPoints={analysisData?.keyPoints} />
        </TabsContent>
        <TabsContent value="sentiment">
          <SentimentView sentimentData={analysisData?.sentiment} />
        </TabsContent>
        <TabsContent value="summary">
          <SummaryView summary={analysisData?.summary} />
        </TabsContent>
        <TabsContent value="chat">
          <ChatView videoId={videoId} />
        </TabsContent>
      </div>
    </Tabs>
  )
}
