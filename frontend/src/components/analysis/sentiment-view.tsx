import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface SentimentViewProps {
  sentimentData?: {
    positive: number
    negative: number
    neutral: number
    segments: Array<{
      text: string
      sentiment: string
      timestamp: string
    }>
  }
  loading?: boolean
}

export function SentimentView({ sentimentData, loading }: SentimentViewProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Analysis</CardTitle>
        </CardHeader>
        <CardContent>Loading sentiment analysis...</CardContent>
      </Card>
    )
  }

  if (!sentimentData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No sentiment data available
          </div>
        </CardContent>
      </Card>
    )
  }

  const { positive, negative, neutral, segments } = sentimentData
  const total = positive + negative + neutral

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiment Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Overall Sentiment</span>
            <span className="text-sm text-muted-foreground">
              {Math.round((positive / total) * 100)}% Positive
            </span>
          </div>
          <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500"
              style={{ width: `${(positive / total) * 100}%` }}
            />
          </div>
        </div>
        <ScrollArea className="h-[300px] w-full rounded-md border p-4">
          {segments.map((segment, index) => (
            <div
              key={index}
              className="mb-4 last:mb-0"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">
                  {segment.timestamp}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    segment.sentiment === "positive"
                      ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                      : segment.sentiment === "negative"
                      ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                      : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                  }`}
                >
                  {segment.sentiment}
                </span>
              </div>
              <p className="text-sm">{segment.text}</p>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
