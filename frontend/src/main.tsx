import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App.tsx'
import { BrowserAudioRecorder } from './infrastructure/audio/BrowserAudioRecorder'
import './shared/styles/tokens.css'
import './shared/styles/global.css'

const audioRecorder = new BrowserAudioRecorder()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App audioRecorder={audioRecorder} />
  </StrictMode>,
)
