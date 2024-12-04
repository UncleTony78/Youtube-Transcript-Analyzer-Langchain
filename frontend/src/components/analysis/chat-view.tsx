import { useState } from "react"
import { Send } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/use-toast"
import { chatWithVideo } from "@/lib/api"
import type { ChatMessage } from "@/lib/types"

interface ChatViewProps {
  videoId: string
}

export function ChatView({ videoId }: ChatViewProps) {
  const { toast } = useToast()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await chatWithVideo(videoId, input, messages)
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Chat Failed",
        description: error instanceof Error ? error.message : "Failed to get response",
      })
      // Remove the user message if we couldn't get a response
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chat about the Video</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col h-[400px]">
          <ScrollArea className="flex-1 w-full rounded-md border p-4 mb-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                Start a conversation about the video content
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 last:mb-0 ${
                  message.role === "assistant"
                    ? "ml-4"
                    : "mr-4"
                }`}
              >
                <div
                  className={`flex flex-col ${
                    message.role === "assistant"
                      ? "items-start"
                      : "items-end"
                  }`}
                >
                  <div
                    className={`rounded-lg px-4 py-2 max-w-[80%] ${
                      message.role === "assistant"
                        ? "bg-muted"
                        : "bg-primary text-primary-foreground"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center space-x-2 text-muted-foreground">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce delay-100">●</div>
                <div className="animate-bounce delay-200">●</div>
              </div>
            )}
          </ScrollArea>
          <div className="flex space-x-2">
            <Input
              placeholder="Ask anything about the video..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              disabled={loading}
            />
            <Button
              size="icon"
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
