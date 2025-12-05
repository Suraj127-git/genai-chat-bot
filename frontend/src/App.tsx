import { useState } from 'react'
import Chat from './features/chat/Chat'
import News from './features/news/News'

export default function App() {
  const [tab, setTab] = useState<'chat'|'news'>('chat')
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto p-4 flex gap-4">
          <button className={`px-3 py-2 rounded ${tab==='chat'?'bg-blue-600 text-white':'bg-gray-200'}`} onClick={() => setTab('chat')}>Chat</button>
          <button className={`px-3 py-2 rounded ${tab==='news'?'bg-blue-600 text-white':'bg-gray-200'}`} onClick={() => setTab('news')}>AI News</button>
        </div>
      </header>
      <main className="py-6">
        {tab==='chat' ? <Chat/> : <News/>}
      </main>
    </div>
  )
}
