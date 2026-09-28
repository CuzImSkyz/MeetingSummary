export type HealthStatus = 'ok'

export type HealthClientErrorCode =
  | 'unreachable'
  | 'request-failed'
  | 'invalid-response'

export class HealthClientError extends Error {
  readonly code: HealthClientErrorCode

  constructor(
    code: HealthClientErrorCode,
    message: string,
    options?: ErrorOptions,
  ) {
    super(message, options)
    this.name = 'HealthClientError'
    this.code = code
  }
}

export interface HealthClient {
  check(): Promise<HealthStatus>
}
