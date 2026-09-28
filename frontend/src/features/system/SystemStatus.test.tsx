// @vitest-environment jsdom

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { HealthClient } from './healthClient'
import { SystemStatus } from './SystemStatus'

describe('SystemStatus', () => {
  it('zeigt einen verfügbaren lokalen Dienst', async () => {
    const healthClient: HealthClient = {
      check: vi.fn().mockResolvedValue(undefined),
    }

    render(<SystemStatus healthClient={healthClient} />)

    expect(
      await screen.findByText('Lokaler Dienst bereit'),
    ).toBeInTheDocument()

    expect(screen.getByRole('status')).toHaveAttribute(
      'aria-live',
      'polite',
    )
  })

  it('zeigt einen nicht erreichbaren lokalen Dienst', async () => {
    const healthClient: HealthClient = {
      check: vi.fn().mockRejectedValue(
        new Error('Dienst nicht erreichbar'),
      ),
    }

    render(<SystemStatus healthClient={healthClient} />)

    expect(
      await screen.findByText('Lokaler Dienst offline'),
    ).toBeInTheDocument()
  })
})
