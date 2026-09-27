import { Mic, Upload } from 'lucide-react'
import styles from './HomePage.module.css'

type HomePageProps = {
  onStartMeeting: () => Promise<void>
  isStarting: boolean
  errorMessage: string | null
  hasPendingRecording: boolean
}

export function HomePage({
  onStartMeeting,
  isStarting,
  errorMessage,
  hasPendingRecording,
}: HomePageProps) {
  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <p className={styles.kicker}>Meeting Assistant</p>
        <h1 className={styles.title}>Bereit für ein unvergessliches Meeting?</h1>
        <p className={styles.description}>
          Meetings lokal aufnehmen, transkribieren und strukturiert zusammenfassen.
        </p>
      </header>

      {errorMessage !== null && (
        <p className={styles.error} role="alert">
          {errorMessage}
        </p>
      )}

      {hasPendingRecording && (
        <p className={styles.pendingRecording} role="status">
          Die Aufnahme ist bereit für die Verarbeitung.
        </p>
      )}

      <div className={styles.actions}>
        <button
          className={styles.primaryAction}
          type="button"
          onClick={onStartMeeting}
          disabled={isStarting}
          aria-busy={isStarting}
        >
          <Mic aria-hidden="true" size={28} />
          <span>
            <strong>
              {isStarting ? 'Mikrofon wird vorbereitet …' : 'Starte Meeting'}
            </strong>
            <small>Aufnahme direkt beginnen</small>
          </span>
        </button>

        <label className={styles.uploadAction}>
          <input
            className={styles.fileInput}
            type="file"
            accept="audio/*"
          />

          <Upload aria-hidden="true" size={24} />

          <span>
            <strong>Aufgenommenes Meeting zusammenfassen</strong>
            <small>Audiodatei auswählen oder später hier ablegen</small>
          </span>
        </label>
      </div>
    </section>
  )
}
