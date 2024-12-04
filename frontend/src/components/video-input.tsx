import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Download } from "lucide-react"
import { AnalysisTabs } from "./analysis/analysis-tabs"
import { analyzeVideo, exportAnalysis } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import type { AnalysisResults, ExportFormat } from "@/lib/types"

export function VideoInput() {
  const { toast } = useToast()
  const [url, setUrl] = useState("")
  const [loading, setLoading] = useState(false)
  const [videoId, setVideoId] = useState<string>("")
  const [analysisData, setAnalysisData] = useState<AnalysisResults | undefined>()
  const [exporting, setExporting] = useState(false)

  const extractVideoId = (url: string) => {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
    const match = url.match(regex)
    return match ? match[1] : null
  }

  const handleAnalyze = async () => {
    if (!url) return
    const id = extractVideoId(url)
    if (!id) {
      toast({
        variant: "destructive",
        title: "Invalid URL",
        description: "Please enter a valid YouTube video URL",
      })
      return
    }

    setLoading(true)
    setVideoId(id)

    try {
      const results = await analyzeVideo(url)
      setAnalysisData(results)
      toast({
        title: "Analysis Complete",
        description: "Video analysis has been completed successfully.",
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Failed to analyze video",
      })
      setAnalysisData(undefined)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: ExportFormat) => {
    if (!videoId) return

    setExporting(true)
    try {
      const blob = await exportAnalysis(videoId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = format.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: "Export Complete",
        description: `Analysis has been exported as ${format.type.toUpperCase()}`,
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Export Failed",
        description: error instanceof Error ? error.message : "Failed to export analysis",
      })
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="w-full space-y-8">
      <Card className="w-full max-w-3xl mx-auto">
        <CardContent className="pt-6">
          <div className="flex flex-col space-y-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Enter YouTube video URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleAnalyze} disabled={!url || loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing
                  </>
                ) : (
                  "Analyze"
                )}
              </Button>
            </div>
            {videoId && (
              <div className="aspect-video w-full rounded-lg overflow-hidden">
                <iframe
                  width="100%"
                  height="100%"
                  src={`https://www.youtube.com/embed/${videoId}`}
                  title="YouTube video player"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {analysisData && videoId && (
        <>
          <div className="flex justify-end space-x-2 max-w-4xl mx-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport({ type: "pdf", filename: `analysis_${videoId}.pdf` })}
              disabled={exporting}
            >
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport({ type: "txt", filename: `analysis_${videoId}.txt` })}
              disabled={exporting}
            >
              <Download className="mr-2 h-4 w-4" />
              Export TXT
            </Button>
          </div>
          <AnalysisTabs videoId={videoId} analysisData={analysisData} />
        </>
      )}
    </div>
  )
}
