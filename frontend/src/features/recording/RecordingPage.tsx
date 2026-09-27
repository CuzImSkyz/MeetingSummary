import { Square } from 'lucide-react'
import styles from './RecordingPage.module.css'
import {
    formatElapsedTime,
    useElapsedTime,
} from './useElapsedTime'

type RecordingPageProps = {
    onStop: () => void
}

export function RecordingPage({ onStop }: RecordingPageProps){
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

            <button className={styles.stopButton} type="button" onClick={onStop}>
                <Square aria-hidden="true" size={18} fill="currentColor" />
                Aufnahme beenden
            </button>
        </section>
    )
}