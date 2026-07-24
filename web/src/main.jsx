import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { bootstrapPlatformAuth, installAuthenticatedFetch } from './platformAuth'

async function start() {
  await bootstrapPlatformAuth()
  installAuthenticatedFetch()
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}

start().catch((error) => {
  document.getElementById('root').textContent = `Platform startup failed: ${error.message}`
})
