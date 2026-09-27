import { describe, expect, it } from 'vitest'
import { formatElapsedTime } from './useElapsedTime'

describe('formatElapsedTime', () => {
  it.each([
    [0, '00:00'],
    [5, '00:05'],
    [65, '01:05'],
    [3600, '60:00'],
  ])('formatiert %i Sekunden als %s', (seconds, expected) => {
    expect(formatElapsedTime(seconds)).toBe(expected)
  })
})
