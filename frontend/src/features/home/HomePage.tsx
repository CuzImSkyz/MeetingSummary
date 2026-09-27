import { Mic, Upload } from 'lucide-react'
import styles from './HomePage.module.css'

type HomePageProps = {
    onStartMeeting: () => void
}

export function HomePage({ onStartMeeting }: HomePageProps) {
    return (
        <section className={styles.page}>
            <header className={styles.header}>
                <p className={styles.kicker}>Meeting Assistant</p>
                <h1 className={styles.title}>Bereit für ein unvergessliches Meeting?</h1>
                <p className={styles.description}>
                    Meetings lokal aufnehmen, transkribieren und strukturiert zusammenfassen.
                </p>
            </header>

            <div className={styles.actions}>
                <button 
                    className={styles.primaryAction} 
                    type="button"
                    onClick={onStartMeeting}
                    >
                    <Mic aria-hidden="true" size={28} />
                    <span>
                        <strong>Starte Meeting</strong>
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
