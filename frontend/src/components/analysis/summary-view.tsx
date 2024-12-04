import { Copy } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/components/ui/use-toast"

interface SummaryViewProps {
  summary?: string
}

export function SummaryView({ summary }: SummaryViewProps) {
  const { toast } = useToast()

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary)
      toast({
        title: "Copied to clipboard",
        description: "The summary has been copied to your clipboard.",
      })
    }
  }

  if (!summary) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No summary available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Summary</CardTitle>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleCopy}
          className="h-8 w-8"
        >
          <Copy className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border p-4">
          <p className="text-sm leading-7 [&:not(:first-child)]:mt-6">
            {summary}
          </p>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
