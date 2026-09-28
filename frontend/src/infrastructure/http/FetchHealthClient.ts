import {
  HealthClientError,
  type HealthClient,
} from '../../features/system/healthClient'

interface HealthResponse {
  status: 'ok'
}

export class FetchHealthClient implements HealthClient {
  private readonly baseUrl: string

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  async check(): Promise<void> {
    let response: Response

    try {
      response = await fetch(`${this.baseUrl}/health`)
    } catch (cause) {
      throw new HealthClientError(
        'unreachable',
        'Der lokale MeetMe-Dienst ist nicht erreichbar.',
        { cause },
      )
    }

    if (!response.ok) {
      throw new HealthClientError(
        'request-failed',
        `Der MeetMe-Dienst antwortete mit HTTP ${response.status}.`,
      )
    }

    let body: unknown

    try {
      body = await response.json()
    } catch (cause) {
      throw new HealthClientError(
        'invalid-response',
        'Der MeetMe-Dienst lieferte kein gültiges JSON.',
        { cause },
      )
    }

    if (!isHealthResponse(body)) {
      throw new HealthClientError(
        'invalid-response',
        'Die Antwort des MeetMe-Dienstes ist ungültig.',
      )
    }
  }
}

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    value.status === 'ok'
  )
}
