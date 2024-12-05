import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TranscriptView } from "./transcript-view"
import { KeyPointsView } from "./key-points-view"
import { SentimentView } from "./sentiment-view"
import { SummaryView } from "./summary-view"
import { ChatView } from "./chat-view"
import type { AnalysisResults } from "@/lib/types"

interface AnalysisTabsProps {
  videoId: string
  loading?: boolean
  analysisData?: AnalysisResults
}

export function AnalysisTabs({ videoId, loading, analysisData }: AnalysisTabsProps) {
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
          <TranscriptView transcript={analysisData?.transcript} loading={loading} />
        </TabsContent>
        <TabsContent value="keypoints">
          <KeyPointsView keyPoints={analysisData?.keyPoints} loading={loading} />
        </TabsContent>
        <TabsContent value="sentiment">
          <SentimentView sentimentData={analysisData?.sentiment} loading={loading} />
        </TabsContent>
        <TabsContent value="summary">
          <SummaryView summary={analysisData?.summary} loading={loading} />
        </TabsContent>
        <TabsContent value="chat">
          <ChatView videoId={videoId} />
        </TabsContent>
      </div>
    </Tabs>
  )
}
