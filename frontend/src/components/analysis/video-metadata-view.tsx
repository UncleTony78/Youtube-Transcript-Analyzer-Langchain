import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import type { VideoMetadata } from "@/lib/types"

interface VideoMetadataViewProps {
  metadata?: VideoMetadata
  loading?: boolean
}

export function VideoMetadataView({ metadata, loading }: VideoMetadataViewProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-[250px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-[70px]" />
              <Skeleton className="h-4 w-[100px]" />
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-[90px]" />
              <Skeleton className="h-4 w-[80px]" />
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-[60px]" />
              <Skeleton className="h-4 w-[120px]" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!metadata) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Video Information</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Loading video information...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{metadata.title || 'Untitled Video'}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {metadata.duration && (
            <div className="flex items-center gap-2">
              <span className="font-medium min-w-[90px]">Duration:</span>
              <span>{metadata.duration}</span>
            </div>
          )}
          {metadata.resolution && (
            <div className="flex items-center gap-2">
              <span className="font-medium min-w-[90px]">Resolution:</span>
              <span>{metadata.resolution}</span>
            </div>
          )}
          {metadata.format && (
            <div className="flex items-center gap-2">
              <span className="font-medium min-w-[90px]">Format:</span>
              <span>{metadata.format}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
