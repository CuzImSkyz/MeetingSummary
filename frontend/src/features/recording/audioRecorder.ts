export type AudioRecorderErrorCode =
  | 'not-supported'
  | 'permission-denied'
  | 'device-not-found'
  | 'already-recording'
  | 'not-recording'
  | 'capture-failed'

export class AudioRecorderError extends Error {
  public readonly code: AudioRecorderErrorCode

  constructor(
    code: AudioRecorderErrorCode,
    message: string,
    options?: ErrorOptions,
  ) {
    super(message, options)
    this.name = 'AudioRecorderError'
    this.code = code
  }
}

export interface AudioRecorder {
  start(): Promise<void>
  stop(): Promise<Blob>
}
