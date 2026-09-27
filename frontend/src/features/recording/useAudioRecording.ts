import { useCallback, useState } from 'react'
import {
  AudioRecorderError,
  type AudioRecorder,
} from './audioRecorder'

export type AudioRecordingStatus =
  | 'idle'
  | 'starting'
  | 'recording'
  | 'stopping'
  | 'failed'

export function useAudioRecording(recorder: AudioRecorder) {
  const [status, setStatus] =
    useState<AudioRecordingStatus>('idle')

  const [error, setError] =
    useState<AudioRecorderError | null>(null)

  const start = useCallback(async (): Promise<boolean> => {
    setStatus('starting')
    setError(null)

    try {
      await recorder.start()
      setStatus('recording')
      return true
    } catch (cause) {
      setError(normalizeError(cause))
      setStatus('failed')
      return false
    }
  }, [recorder])

  const stop = useCallback(async (): Promise<Blob | null> => {
    setStatus('stopping')
    setError(null)

    try {
      const blob = await recorder.stop()
      setStatus('idle')
      return blob
    } catch (cause) {
      setError(normalizeError(cause))
      setStatus('failed')
      return null
    }
  }, [recorder])

  return {
    status,
    error,
    start,
    stop,
  }
}

function normalizeError(cause: unknown): AudioRecorderError {
  if (cause instanceof AudioRecorderError) {
    return cause
  }

  return new AudioRecorderError(
    'capture-failed',
    'Die Audioaufnahme ist unerwartet fehlgeschlagen.',
    { cause },
  )
}
