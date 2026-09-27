import { useEffect, useState } from "react"

export function useElapsedTime(): number {
    const [elapsedSeconds, setElapsedSeconds] = useState(0)

    useEffect(() => {
        const startedAt = Date.now()

        const intervalId = window.setInterval(() => {
            const elapsedMilliseconds = Date.now() - startedAt
            setElapsedSeconds(Math.floor(elapsedMilliseconds / 1000))
        }, 1000)

        return () => window.clearInterval(intervalId)
    }, [])

    return elapsedSeconds
}

export function formatElapsedTime(totalSeconds: number): string {
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60

    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}