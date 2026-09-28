// @vitest-environment jsdom

import { renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { HealthClient } from './healthClient'
import { useHealthCheck } from './useHealthCheck'

describe('useHealthCheck', () => {
  it('wechselt bei erfolgreicher Prüfung auf available', async () => {
    const healthClient: HealthClient = {
      check: vi.fn().mockResolvedValue(undefined),
    }

    const { result } = renderHook(() =>
      useHealthCheck(healthClient),
    )

    expect(result.current).toBe('checking')

    await waitFor(() => {
      expect(result.current).toBe('available')
    })

    expect(healthClient.check).toHaveBeenCalledOnce()
  })

  it('wechselt bei einem Fehler auf unavailable', async () => {
    const healthClient: HealthClient = {
      check: vi.fn().mockRejectedValue(new Error('Dienst nicht erreichbar')),
    }

    const { result } = renderHook(() =>
      useHealthCheck(healthClient),
    )

    await waitFor(() => {
      expect(result.current).toBe('unavailable')
    })
  })
})
