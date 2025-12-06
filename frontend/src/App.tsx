import React, { useState } from 'react'
import { SystemBar } from './components/SystemBar'
import { BotList } from './components/BotList'
import { BotDetails } from './components/BotDetails'
import './App.css'

const App: React.FC = () => {
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null)

  return (
    <div className="app">
      <header>
        <h1>Binance Microtrade Bot</h1>
      </header>

      <SystemBar />

      <main className="main-layout">
        <section className="left-panel">
          <BotList onSelectBot={setSelectedBotId} />
        </section>
        <section className="right-panel">
          <BotDetails botId={selectedBotId} />
        </section>
      </main>
    </div>
  )
}

export default App
