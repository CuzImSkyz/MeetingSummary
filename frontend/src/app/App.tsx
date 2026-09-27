import { useState } from 'react'
import { HomePage } from '../features/home/HomePage'
import { RecordingPage } from '../features/recording/RecordingPage'
import type { AudioRecorder } from '../features/recording/audioRecorder'
import { useAudioRecording } from '../features/recording/useAudioRecording'
import { AppShell } from './AppShell'

type AppScreen = 'home' | 'recording'

type AppProps = {
  audioRecorder: AudioRecorder
}

export function App({ audioRecorder }: AppProps) {
  const [screen, setScreen] = useState<AppScreen>('home')
  const [pendingRecording, setPendingRecording] =
    useState<Blob | null>(null)

  const {
    status,
    error,
    start,
    stop,
  } = useAudioRecording(audioRecorder)

  async function handleStartMeeting(): Promise<void> {
    const didStart = await start()

    if (didStart) {
      setPendingRecording(null)
      setScreen('recording')
    }
  }

  async function handleStopMeeting(): Promise<void> {
    const blob = await stop()

    if (blob === null) {
      return
    }

    setPendingRecording(blob)
    setScreen('home')
  }

  return (
    <AppShell>
      {screen === 'home' ? (
        <HomePage
          onStartMeeting={handleStartMeeting}
          isStarting={status === 'starting'}
          errorMessage={error?.message ?? null}
          hasPendingRecording={pendingRecording !== null}
        />
      ) : (
        <RecordingPage
          onStop={handleStopMeeting}
          isStopping={status === 'stopping'}
          errorMessage={error?.message ?? null}
        />
      )}
    </AppShell>
  )
}
