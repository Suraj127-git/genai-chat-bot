import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '../../lib/api'

type NewsState = {
  summary?: string
  loading: boolean
  error?: string
  timeframe: string
}

const initialState: NewsState = {
  loading: false,
  timeframe: 'last 24 hours'
}


export const fetchNews = createAsyncThunk(
  'news/fetch',
  async (_: void, { getState }) => {
    const state = getState() as any
    const { timeframe } = state.news
    return await api.newsSummary({ timeframe })
  }
)

const slice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    setTimeframe(state, action) { state.timeframe = action.payload }
  },
  extraReducers: builder => {
    builder.addCase(fetchNews.pending, (state) => { state.loading = true; state.error = undefined })
    builder.addCase(fetchNews.fulfilled, (state, action) => {
      state.loading = false
      state.summary = action.payload.summary
    })
    builder.addCase(fetchNews.rejected, (state, action) => {
      state.loading = false
      state.error = action.error.message
    })
  }
})

export const { setTimeframe } = slice.actions
export default slice.reducer
