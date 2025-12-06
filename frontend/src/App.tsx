import React, { useState } from 'react'
import { SystemBar } from './components/SystemBar'
import { BotList } from './components/BotList'
import { BotDetails } from './components/BotDetails'
import { CreateBotForm } from './components/CreateBotForm'
import './App.css'

const App: React.FC = () => {
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null)
  const [botsReloadToken, setBotsReloadToken] = useState(0)

  const handleBotCreated = () => {
    setBotsReloadToken(prev => prev + 1)
  }

  return (
    <div className="app">
      <header>
        <h1>Binance Microtrade Bot</h1>
      </header>

      <SystemBar />

      <main className="main-layout">
        <section className="left-panel">
          <CreateBotForm onCreated={handleBotCreated} />
          <BotList onSelectBot={setSelectedBotId} reloadToken={botsReloadToken} />
        </section>
        <section className="right-panel">
          <BotDetails botId={selectedBotId} />
        </section>
      </main>
    </div>
  )
}

export default App
