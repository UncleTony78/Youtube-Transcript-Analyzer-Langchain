import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface VideoMetadata {
  title?: string;
  duration?: string;
  resolution?: string;
  format?: string;
}

interface VideoPlayerProps {
  videoUrl: string;
  metadata?: VideoMetadata;
}

export function VideoPlayer({ videoUrl, metadata }: VideoPlayerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{metadata?.title || 'Video Player'}</CardTitle>
        {metadata && (
          <div className="flex gap-2 text-sm text-muted-foreground">
            {metadata.duration && <span>{metadata.duration}</span>}
            {metadata.resolution && <span>{metadata.resolution}</span>}
            {metadata.format && <span>{metadata.format}</span>}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="relative aspect-video w-full overflow-hidden rounded-lg">
          <video
            src={videoUrl}
            controls
            className="h-full w-full"
          />
        </div>
      </CardContent>
    </Card>
  );
}
