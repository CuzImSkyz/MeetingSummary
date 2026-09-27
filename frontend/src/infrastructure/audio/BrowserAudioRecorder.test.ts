import { afterEach, describe, expect, it, vi } from 'vitest'
import { BrowserAudioRecorder } from './BrowserAudioRecorder'

describe('BrowserAudioRecorder', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
    })

    it('meldet einen Fehler, wenn keine Aufnahme läuft', async () => {
        const recorder = new BrowserAudioRecorder()

        await expect(recorder.stop()).rejects.toMatchObject({
            name: 'AudioRecorderError',
            code: 'not-recording',
        })
    })

    it('startet die Aufnahme und liefert beim Stoppen den Audioblob', async () => {
        const start = vi.fn()
        const stopTrack = vi.fn()

        const stream = {
            getTracks: () => [{ stop: stopTrack }],
        } as unknown as MediaStream

        const getUserMedia = vi.fn().mockResolvedValue(stream)
        const audioChunk = new Blob(['audio-data'], {
            type: 'audio/webm',
        })

        class FakeMediaRecorder extends EventTarget {
            state: RecordingState = 'inactive'
            readonly mimeType = 'audio/webm'

            start(): void {
                this.state = 'recording'
                start()
            }

            stop(): void {
                this.state = 'inactive'

                queueMicrotask(() => {
                    const dataEvent = Object.assign(
                        new Event('dataavailable'),
                        { data: audioChunk },
                    )

                    this.dispatchEvent(dataEvent)
                    this.dispatchEvent(new Event('stop'))
                })
            }
        }

        vi.stubGlobal('navigator', {
            mediaDevices: {
                getUserMedia,
            },
        })

        vi.stubGlobal('MediaRecorder', FakeMediaRecorder)

        const recorder = new BrowserAudioRecorder()

        await recorder.start()

        expect(getUserMedia).toHaveBeenCalledWith({ audio: true })
        expect(start).toHaveBeenCalledOnce()

        const blob = await recorder.stop()

        expect(blob.type).toBe('audio/webm')
        expect(await blob.text()).toBe('audio-data')
        expect(stopTrack).toHaveBeenCalledOnce()
    })
})
