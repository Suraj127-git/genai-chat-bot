import { configureStore } from '@reduxjs/toolkit'
import chatReducer from '../features/chat/slice'
import newsReducer from '../features/news/slice'

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    news: newsReducer
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
