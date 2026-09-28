import type { HealthClient } from './healthClient'
import {
  type HealthCheckStatus,
  useHealthCheck,
} from './useHealthCheck'
import styles from './SystemStatus.module.css'

type SystemStatusProps = {
  healthClient: HealthClient
}

const statusLabels: Record<HealthCheckStatus, string> = {
  checking: 'Dienst wird geprüft',
  available: 'Lokaler Dienst bereit',
  unavailable: 'Lokaler Dienst offline',
}

export function SystemStatus({
  healthClient,
}: SystemStatusProps) {
  const status = useHealthCheck(healthClient)

  const dotClassNames: Record<HealthCheckStatus, string> = {
    checking: styles.dotChecking,
    available: styles.dotAvailable,
    unavailable: styles.dotUnavailable,
  }

  return (
    <p
      className={styles.status}
      role="status"
      aria-live="polite"
    >
      <span
        className={`${styles.dot} ${dotClassNames[status]}`}
        aria-hidden="true"
      />
      <span>{statusLabels[status]}</span>
    </p>
  )
}
