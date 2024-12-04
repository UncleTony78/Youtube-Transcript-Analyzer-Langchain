import { useState } from 'react'
import { ThemeProvider } from "@/components/theme-provider"
import { MainNav } from "@/components/layout/main-nav"
import { VideoInput } from "@/components/video-input"
import { Toaster } from "@/components/ui/toaster"
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <ThemeProvider defaultTheme="system" storageKey="yt-insight-theme">
      <div className="min-h-screen bg-background font-sans antialiased">
        <MainNav />
        <main className="container py-6 md:py-12">
          <div className="flex flex-col items-center space-y-8 text-center">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold sm:text-4xl md:text-5xl">
                YouTube Transcript Analysis
              </h1>
              <p className="text-muted-foreground">
                Extract deep insights from any YouTube video using AI
              </p>
            </div>
            <VideoInput />
          </div>
        </main>
      </div>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
