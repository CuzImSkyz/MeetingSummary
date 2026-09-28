import { useEffect, useState } from 'react'

import type { HealthClient } from './healthClient'

export type HealthCheckStatus =
  | 'checking'
  | 'available'
  | 'unavailable'

export function useHealthCheck(
  healthClient: HealthClient,
): HealthCheckStatus {
  const [status, setStatus] =
    useState<HealthCheckStatus>('checking')

  useEffect(() => {
    let isCurrent = true

    async function checkHealth(): Promise<void> {
      try {
        await healthClient.check()

        if (isCurrent) {
          setStatus('available')
        }
      } catch {
        if (isCurrent) {
          setStatus('unavailable')
        }
      }
    }

    void checkHealth()

    return () => {
      isCurrent = false
    }
  }, [healthClient])

  return status
}
