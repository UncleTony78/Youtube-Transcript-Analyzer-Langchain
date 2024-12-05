import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import type { KeyPoint } from "@/lib/types"

interface KeyPointsViewProps {
  keyPoints?: KeyPoint[]
  loading?: boolean
}

export function KeyPointsView({ keyPoints, loading }: KeyPointsViewProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Key Points</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] w-full rounded-md border p-4">
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <div className="mt-1">
                    <Skeleton className="h-2 w-2 rounded-full" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-[90%]" />
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    )
  }

  if (!keyPoints?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Key Points</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No key points available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Key Points</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border p-4">
          <ul className="list-disc list-inside space-y-4">
            {keyPoints.map((point, index) => (
              <li key={index} className="text-sm">
                {point.text}
                <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                  point.importance === 'high' 
                    ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                    : point.importance === 'medium'
                    ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                    : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                }`}>
                  {point.importance}
                </span>
                {point.category && (
                  <span className="ml-2 text-xs text-muted-foreground">
                    {point.category}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
