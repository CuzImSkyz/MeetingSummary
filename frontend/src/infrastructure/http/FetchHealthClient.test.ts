import { afterEach, describe, expect, it, vi } from 'vitest'

import { FetchHealthClient } from './FetchHealthClient'

describe('FetchHealthClient', () => {
    afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('liefert ok bei einer gültigen Antwort', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    )

    vi.stubGlobal('fetch', fetchMock)

    const client = new FetchHealthClient()

    await expect(client.check()).resolves.toBeUndefined()
    expect(fetchMock).toHaveBeenCalledWith('/api/health')
  })

  it('übersetzt einen HTTP-Fehler', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(null, { status: 503 })),
    )

    const client = new FetchHealthClient()

    await expect(client.check()).rejects.toMatchObject({
      name: 'HealthClientError',
      code: 'request-failed',
    })
  })

  it('weist eine ungültige Antwort zurück', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'broken' }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        }),
      ),
    )

    const client = new FetchHealthClient()

    await expect(client.check()).rejects.toMatchObject({
      name: 'HealthClientError',
      code: 'invalid-response',
    })
  })
})
