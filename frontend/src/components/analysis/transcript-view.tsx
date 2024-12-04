import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface TranscriptViewProps {
  transcript?: string[]
}

export function TranscriptView({ transcript }: TranscriptViewProps) {
  if (!transcript) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Transcript</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No transcript available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transcript</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border p-4">
          {transcript.map((line, index) => (
            <div
              key={index}
              className="mb-4 last:mb-0"
            >
              <p className="text-sm">{line}</p>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
