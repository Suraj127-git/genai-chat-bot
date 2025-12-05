import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '../../lib/api'

type ChatState = {
  messages: { role: 'user'|'assistant', content: string }[]
  loading: boolean
  error?: string
  provider: 'Groq'|'Ollama'
  model: string
  usecase: 'Basic Chatbot'|'Chatbot With Web'
}

const initialState: ChatState = {
  messages: [],
  loading: false,
  provider: 'Groq',
  model: 'llama3-8b-8192',
  usecase: 'Basic Chatbot'
}


export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (payload: { content: string }, { getState }) => {
    const state = getState() as any
    const { provider, model, usecase } = state.chat
    return await api.chat({ provider, model, usecase, message: payload.content })
  }
)

const slice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setProvider(state, action) { state.provider = action.payload },
    setModel(state, action) { state.model = action.payload },
    setUsecase(state, action) { state.usecase = action.payload },
    addUserMessage(state, action) { state.messages.push({ role: 'user', content: action.payload }) }
  },
  extraReducers: builder => {
    builder.addCase(sendMessage.pending, (state) => { state.loading = true; state.error = undefined })
    builder.addCase(sendMessage.fulfilled, (state, action) => {
      state.loading = false
      state.messages.push({ role: 'assistant', content: action.payload.content })
    })
    builder.addCase(sendMessage.rejected, (state, action) => {
      state.loading = false
      state.error = action.error.message
    })
  }
})

export const { setProvider, setModel, setUsecase, addUserMessage } = slice.actions
export default slice.reducer
