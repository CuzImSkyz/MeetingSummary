import { useState } from 'react'
import { HomePage } from "../features/home/HomePage"
import { RecordingPage } from '../features/recording/RecordingPage'
import { AppShell  } from "./AppShell"

type AppScreen = 'home' | 'recording'

export function App() {
  const [screen, setScreen] = useState<AppScreen>('home')
  
  return (
    <AppShell>
      {screen === 'home' ? (
        <HomePage onStartMeeting={() => setScreen('recording')} />
      ) : (
        <RecordingPage onStop={() => setScreen('home')} />
      )}
    </AppShell>
  )
}
