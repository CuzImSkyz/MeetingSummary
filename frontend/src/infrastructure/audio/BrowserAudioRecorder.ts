import {
    AudioRecorderError,
    type AudioRecorder,
} from '../../features/recording/audioRecorder'

export class BrowserAudioRecorder implements AudioRecorder {
    private recorder: MediaRecorder | null = null
    private stream: MediaStream | null = null
    private chunks: Blob[] = []

    async start(): Promise<void> {
        if (this.recorder !== null) {
            throw new AudioRecorderError(
                'already-recording',
                'Es läuft bereits eine Aufnahme.',
            )
        }

        if (
            navigator.mediaDevices?.getUserMedia === undefined ||
            typeof MediaRecorder === 'undefined'
        ) {
            throw new AudioRecorderError(
                'not-supported',
                'Audioaufnahmen werden von diesem Browser nicht unterstützt.',
            )
        }

        let stream: MediaStream | null = null
        
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true})

            const recorder = new MediaRecorder(stream)

            this.chunks = []
            this.stream = stream
            this.recorder = recorder

            recorder.addEventListener('dataavailable', (event) => {
                if (event.data.size > 0) {
                    this.chunks.push(event.data)
                }
            })

            recorder.start()
        } catch (cause) {
            stream?.getTracks().forEach((track) => track.stop())
            this.reset()

            throw translateBrowserError(cause)
        }
    }

    stop(): Promise<Blob> {
        const recorder = this.recorder

        if (recorder === null || recorder.state === 'inactive') {
            return Promise.reject(
                new AudioRecorderError(
                    'not-recording',
                    'Es läuft keine Aufnahme.',
                ),
            )
        }

        return new Promise((resolve, reject) => {
            const removeListeners = () => {
                recorder.removeEventListener('stop', handleStop)
                recorder.removeEventListener('error', handleError)
            }

            const handleStop = () => {
                removeListeners()

                const blob =
                    recorder.mimeType.length > 0
                        ? new Blob(this.chunks, { type: recorder.mimeType })
                        : new Blob(this.chunks)

                this.reset()
                resolve(blob)
            }

            const handleError = (event: ErrorEvent) => {
                removeListeners()
                this.reset()

                reject(
                    new AudioRecorderError(
                        'capture-failed',
                        'Die Audioaufnahme ist fehlgeschlagen.',
                        { cause: event.error ?? event },
                    ),
                )
            }

            recorder.addEventListener('stop', handleStop, { once: true })
            recorder.addEventListener('error', handleError, { once: true })

            try {
                recorder.stop()
            } catch (cause) {
                removeListeners()
                this.reset()
                reject(translateBrowserError(cause))
            }
        })
    }

    private reset(): void {
        this.stream?.getTracks().forEach((track) => track.stop())
        
        this.recorder = null
        this.stream = null
        this.chunks = []
    }
}

function translateBrowserError(cause: unknown): AudioRecorderError {
    if (cause instanceof AudioRecorderError) {
        return cause
    }

    if (cause instanceof DOMException) {
        if (cause.name === 'NotAllowedError') {
            return new AudioRecorderError(
                'permission-denied',
                'Der Mikrofonzugriff wurde nicht erlaubt.',
                { cause },
            )
        }
    

        if (cause.name === 'NotFoundError') {
            return new AudioRecorderError(
                'device-not-found',
                'Es wurde kein Mikrofon gefunden.',
                { cause },
            )
        }

        if (cause.name === 'NotSupportedError') {
            return new AudioRecorderError(
                'not-supported',
                'Audioaufnahmen werden nicht unterstützt.',
                { cause },
            )
        }

        if (cause.name === 'InvalidStateError') {
            return new AudioRecorderError(
                'not-recording',
                'Die Aufnahme befindet sich nicht im erwarteten Zustand.',
                { cause },
            )
        }
    }

    return new AudioRecorderError(
    'capture-failed',
    'Die Audioaufnahme konnte nicht ausgeführt werden.',
    { cause },
  )
}

