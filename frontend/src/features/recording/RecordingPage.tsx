import { Square } from 'lucide-react'
import styles from './RecordingPage.module.css'
import {
  formatElapsedTime,
  useElapsedTime,
} from './useElapsedTime'

type RecordingPageProps = {
  onStop: () => Promise<void>
  isStopping: boolean
  errorMessage: string | null
}

export function RecordingPage({
  onStop,
  isStopping,
  errorMessage,
}: RecordingPageProps) {
  const elapsedSeconds = useElapsedTime()

  return (
    <section className={styles.page}>
      <div className={styles.status}>
        <span className={styles.statusIndicator} aria-hidden="true" />
        Aufnahme läuft
      </div>

      <p className={styles.timer}>
        {formatElapsedTime(elapsedSeconds)}
      </p>
      <h1 className={styles.title}>Meeting wird aufgenommen</h1>

      {errorMessage !== null && (
        <p className={styles.error} role="alert">
          {errorMessage}
        </p>
      )}

      <button
        className={styles.stopButton}
        type="button"
        onClick={onStop}
        disabled={isStopping}
        aria-busy={isStopping}
      >
        <Square aria-hidden="true" size={18} fill="currentColor" />
        {isStopping ? 'Aufnahme wird beendet …' : 'Aufnahme beenden'}
      </button>
    </section>
  )
}
