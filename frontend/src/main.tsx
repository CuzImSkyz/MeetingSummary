import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App.tsx'
import { BrowserAudioRecorder } from './infrastructure/audio/BrowserAudioRecorder'
import { FetchHealthClient } from './infrastructure/http/FetchHealthClient.ts'
import './shared/styles/tokens.css'
import './shared/styles/global.css'

const audioRecorder = new BrowserAudioRecorder()
const healthClient = new FetchHealthClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App
      audioRecorder={audioRecorder}
      healthClient={healthClient}
    />
  </StrictMode>,
)
