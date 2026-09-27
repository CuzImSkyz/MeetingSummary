// @vitest-environment jsdom

import { act, renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { useAudioRecording } from './useAudioRecording'
import {
  AudioRecorderError,
  type AudioRecorder,
} from './audioRecorder'

describe('useAudioRecording', () => {
  it('wechselt nach erfolgreichem Start in recording', async () => {
    const recorder: AudioRecorder = {
      start: vi.fn().mockResolvedValue(undefined),
      stop: vi.fn().mockResolvedValue(new Blob()),
    }

    const { result } = renderHook(() =>
      useAudioRecording(recorder),
    )

    expect(result.current.status).toBe('idle')

    await act(async () => {
      await result.current.start()
    })

    expect(result.current.status).toBe('recording')
    expect(recorder.start).toHaveBeenCalledOnce()
  })

  it('stellt einen Recorderfehler im Zustand bereit', async () => {
    const expectedError = new AudioRecorderError(
      'permission-denied',
      'Der Mikrofonzugriff wurde verweigert.',
    )

    const recorder: AudioRecorder = {
      start: vi.fn().mockRejectedValue(expectedError),
      stop: vi.fn().mockResolvedValue(new Blob()),
    }

    const { result } = renderHook(() =>
      useAudioRecording(recorder),
    )

    await act(async () => {
      await result.current.start()
    })

    expect(result.current.status).toBe('failed')
    expect(result.current.error).toBe(expectedError)
  })

  it('liefert den Audioblob und wechselt nach dem Stoppen in idle', async () => {
    const expectedBlob = new Blob(['audio-data'])
    const recorder: AudioRecorder = {
      start: vi.fn().mockResolvedValue(undefined),
      stop: vi.fn().mockResolvedValue(expectedBlob),
    }

    const { result } = renderHook(() =>
      useAudioRecording(recorder),
    )

    await act(async () => {
      await result.current.start()
    })

    let recordedBlob: Blob | null = null

    await act(async () => {
      recordedBlob = await result.current.stop()
    })

    expect(recordedBlob).toBe(expectedBlob)
    expect(result.current.status).toBe('idle')
    expect(recorder.stop).toHaveBeenCalledOnce()
  })
})
