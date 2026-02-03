import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/features/auth/authSlice';
import documentsReducer from '@/features/documents/documentsSlice';
import clinicalReducer from '@/features/clinical/clinicalSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        documents: documentsReducer,
        clinical: clinicalReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
