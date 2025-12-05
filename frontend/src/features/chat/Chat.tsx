import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from '../../store'
import { sendMessage, setProvider, setModel, setUsecase, addUserMessage } from './slice'
import { useState } from 'react'

export default function Chat() {
  const dispatch = useDispatch()
  const { messages, loading, provider, model, usecase } = useSelector((s: RootState) => s.chat)
  const [input, setInput] = useState('')

  const onSend = () => {
    if (!input.trim()) return
    dispatch(addUserMessage(input) as any)
    dispatch(sendMessage({ content: input }) as any)
    setInput('')
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <select className="border p-2" value={provider} onChange={e => dispatch(setProvider(e.target.value) as any)}>
          <option>Groq</option>
          <option>Ollama</option>
        </select>
        <input className="border p-2" value={model} onChange={e => dispatch(setModel(e.target.value) as any)} />
        <select className="border p-2" value={usecase} onChange={e => dispatch(setUsecase(e.target.value) as any)}>
          <option>Basic Chatbot</option>
          <option>Chatbot With Web</option>
        </select>
      </div>
      <div className="border rounded p-4 h-96 overflow-y-auto space-y-2">
        {messages.map((m,i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <span className="inline-block bg-gray-100 rounded px-3 py-2">{m.content}</span>
          </div>
        ))}
        {loading && <div>Loading...</div>}
      </div>
      <div className="flex gap-2">
        <input className="flex-1 border p-2" value={input} onChange={e => setInput(e.target.value)} />
        <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={onSend}>Send</button>
      </div>
    </div>
  )
}
