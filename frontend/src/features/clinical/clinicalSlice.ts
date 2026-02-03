import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '@/services/api';
import type { ClinicalDecision, ClinicalQuery, ClinicalDecisionHistory } from '@/types';

interface ClinicalState {
    currentDecision: ClinicalDecision | null;
    history: ClinicalDecisionHistory[];
    isAnalyzing: boolean;
    isLoadingHistory: boolean;
    error: string | null;
}

const initialState: ClinicalState = {
    currentDecision: null,
    history: [],
    isAnalyzing: false,
    isLoadingHistory: false,
    error: null,
};

export const analyzeClinical = createAsyncThunk(
    'clinical/analyze',
    async (query: ClinicalQuery, { rejectWithValue }) => {
        try {
            return await api.analyzeClinical(query);
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Analysis failed');
        }
    }
);

export const fetchHistory = createAsyncThunk(
    'clinical/fetchHistory',
    async ({ limit = 50, skip = 0 }: { limit?: number; skip?: number }, { rejectWithValue }) => {
        try {
            return await api.getClinicalHistory(limit, skip);
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch history');
        }
    }
);

export const fetchDecisionDetail = createAsyncThunk(
    'clinical/fetchDetail',
    async (id: string, { rejectWithValue }) => {
        try {
            return await api.getClinicalDecision(id);
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch decision');
        }
    }
);

const clinicalSlice = createSlice({
    name: 'clinical',
    initialState,
    reducers: {
        clearError: (state) => {
            state.error = null;
        },
        clearCurrentDecision: (state) => {
            state.currentDecision = null;
        },
    },
    extraReducers: (builder) => {
        // Analyze clinical
        builder.addCase(analyzeClinical.pending, (state) => {
            state.isAnalyzing = true;
            state.error = null;
        });
        builder.addCase(analyzeClinical.fulfilled, (state, action) => {
            state.isAnalyzing = false;
            state.currentDecision = action.payload;
        });
        builder.addCase(analyzeClinical.rejected, (state, action) => {
            state.isAnalyzing = false;
            state.error = action.payload as string;
        });

        // Fetch history
        builder.addCase(fetchHistory.pending, (state) => {
            state.isLoadingHistory = true;
            state.error = null;
        });
        builder.addCase(fetchHistory.fulfilled, (state, action) => {
            state.isLoadingHistory = false;
            state.history = action.payload;
        });
        builder.addCase(fetchHistory.rejected, (state, action) => {
            state.isLoadingHistory = false;
            state.error = action.payload as string;
        });

        // Fetch decision detail
        builder.addCase(fetchDecisionDetail.pending, (state) => {
            state.isAnalyzing = true;
        });
        builder.addCase(fetchDecisionDetail.fulfilled, (state, action) => {
            state.isAnalyzing = false;
            state.currentDecision = action.payload;
        });
        builder.addCase(fetchDecisionDetail.rejected, (state, action) => {
            state.isAnalyzing = false;
            state.error = action.payload as string;
        });
    },
});

export const { clearError, clearCurrentDecision } = clinicalSlice.actions;
export default clinicalSlice.reducer;
