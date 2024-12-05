import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Download } from "lucide-react"
import { AnalysisTabs } from "./analysis/analysis-tabs"
import { analyzeVideo, exportAnalysis, getTranscript } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import type { AnalysisResults, ExportFormat } from "@/lib/types"

export function VideoInput() {
  const { toast } = useToast()
  const [isLoadingTranscript, setIsLoadingTranscript] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [exporting, setExporting] = useState(false)

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoadingTranscript(true);
    setAnalysisProgress(0);

    try {
      // Get transcript first
      console.log('Fetching transcript...');
      const transcriptData = await getTranscript(videoUrl);
      console.log('Transcript response:', transcriptData);
      
      if (!transcriptData) {
        throw new Error('No transcript data received');
      }

      // Set initial state with transcript data
      const initialResults = {
        metadata: transcriptData.metadata,
        transcript: transcriptData.transcript,
        insights: [],
        keyPoints: [],
        sentiment: undefined,
        summary: '',
      };
      
      setAnalysisResults(initialResults);
      
      // Then start the analysis
      setIsAnalyzing(true);
      setAnalysisProgress(0);
      console.log('Starting analysis...');
      
      await analyzeVideo(
        videoUrl,
        (progress) => {
          setAnalysisProgress(progress);
        },
        (partialResults) => {
          setAnalysisResults(prev => ({
            ...prev,
            ...partialResults,
          }));
        }
      );

    } catch (err) {
      console.error('Error during analysis:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: err instanceof Error ? err.message : "Failed to analyze video",
      })
    } finally {
      setIsLoadingTranscript(false);
      setIsAnalyzing(false);
    }
  };

  const handleExport = async (format: ExportFormat) => {
    if (!analysisResults?.metadata?.videoId) return

    setExporting(true)
    try {
      const blob = await exportAnalysis(analysisResults.metadata.videoId, format)
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
      
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
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="Enter YouTube video URL"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={isLoadingTranscript || isAnalyzing}>
                {isLoadingTranscript ? 'Loading Transcript...' : isAnalyzing ? 'Analyzing...' : 'Analyze'}
              </Button>
            </div>
            {error && (
              <div className="text-red-500">{error}</div>
            )}
          </form>

          {(videoUrl || analysisResults || isLoadingTranscript || isAnalyzing) && (
            <div className="mt-8">
              <AnalysisTabs 
                videoId={videoUrl} 
                loading={isLoadingTranscript || isAnalyzing}
                analysisData={analysisResults ?? undefined}
              />
              {isAnalyzing && (
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Analyzing video...</span>
                    <span>{analysisProgress}%</span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-500 ease-out rounded-full"
                      style={{ width: `${analysisProgress}%` }}
                    />
                  </div>
                </div>
              )}
              {analysisResults && (
                <div className="flex justify-end space-x-2 max-w-4xl mx-auto mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport({ type: "pdf", filename: `analysis_${videoUrl}.pdf` })}
                    disabled={exporting}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport({ type: "txt", filename: `analysis_${videoUrl}.txt` })}
                    disabled={exporting}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export TXT
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
