// @vitest-environment jsdom

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { AudioRecorder } from '../features/recording/audioRecorder'
import type { HealthClient } from '../features/system/healthClient'
import { App } from './App'

describe('App recording flow', () => {
  it('startet und beendet eine Aufnahme über die UI', async () => {
    const audioBlob = new Blob(['audio-data'])

    const recorder: AudioRecorder = {
      start: vi.fn().mockResolvedValue(undefined),
      stop: vi.fn().mockResolvedValue(audioBlob),
    }

    const healthClient: HealthClient = {
      check: vi.fn().mockResolvedValue(undefined),
    }

    const user = userEvent.setup()

    render(
      <App
        audioRecorder={recorder}
        healthClient={healthClient}
      />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /starte meeting/i,
      }),
    )

    expect(recorder.start).toHaveBeenCalledOnce()

    expect(
      await screen.findByRole('heading', {
        name: 'Meeting wird aufgenommen',
      }),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('button', {
        name: /aufnahme beenden/i,
      }),
    )

    expect(recorder.stop).toHaveBeenCalledOnce()
    expect(
      screen.getByText(
        'Die Aufnahme ist bereit für die Verarbeitung.',
      ),
    ).toBeInTheDocument()
  })
})
