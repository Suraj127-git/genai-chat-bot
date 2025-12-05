export type ChatPayload = { provider: string; model: string; usecase: string; message: string }
export type ChatResult = { content: string; from_cache?: boolean }
export type NewsPayload = { timeframe: string }
export type NewsResult = { summary: string; saved_file?: string; from_cache?: boolean }

const base = import.meta.env.VITE_API_URL || '/api'

async function request<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text)
  }
  return await res.json()
}

export const api = {
  chat: (payload: ChatPayload) => request<ChatResult>('/chat', payload),
  newsSummary: (payload: NewsPayload) => request<NewsResult>('/news/summary', payload)
}

