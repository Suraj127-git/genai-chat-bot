import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '@/services/api';
import type { Document, DocumentDetail } from '@/types';

interface DocumentsState {
    documents: Document[];
    selectedDocument: DocumentDetail | null;
    isLoading: boolean;
    uploadProgress: number;
    error: string | null;
}

const initialState: DocumentsState = {
    documents: [],
    selectedDocument: null,
    isLoading: false,
    uploadProgress: 0,
    error: null,
};

export const fetchDocuments = createAsyncThunk(
    'documents/fetchAll',
    async (_, { rejectWithValue }) => {
        try {
            return await api.listDocuments();
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch documents');
        }
    }
);

export const uploadDocument = createAsyncThunk(
    'documents/upload',
    async (file: File, { rejectWithValue }) => {
        try {
            return await api.uploadDocument(file);
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Upload failed');
        }
    }
);

export const fetchDocumentDetail = createAsyncThunk(
    'documents/fetchDetail',
    async (id: string, { rejectWithValue }) => {
        try {
            return await api.getDocument(id);
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch document');
        }
    }
);

export const deleteDocument = createAsyncThunk(
    'documents/delete',
    async (id: string, { rejectWithValue }) => {
        try {
            await api.deleteDocument(id);
            return id;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Delete failed');
        }
    }
);

const documentsSlice = createSlice({
    name: 'documents',
    initialState,
    reducers: {
        clearError: (state) => {
            state.error = null;
        },
        clearSelectedDocument: (state) => {
            state.selectedDocument = null;
        },
    },
    extraReducers: (builder) => {
        // Fetch documents
        builder.addCase(fetchDocuments.pending, (state) => {
            state.isLoading = true;
            state.error = null;
        });
        builder.addCase(fetchDocuments.fulfilled, (state, action) => {
            state.isLoading = false;
            state.documents = action.payload;
        });
        builder.addCase(fetchDocuments.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload as string;
        });

        // Upload document
        builder.addCase(uploadDocument.pending, (state) => {
            state.isLoading = true;
            state.error = null;
            state.uploadProgress = 0;
        });
        builder.addCase(uploadDocument.fulfilled, (state, action) => {
            state.isLoading = false;
            state.documents.unshift(action.payload);
            state.uploadProgress = 100;
        });
        builder.addCase(uploadDocument.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload as string;
            state.uploadProgress = 0;
        });

        // Fetch document detail
        builder.addCase(fetchDocumentDetail.pending, (state) => {
            state.isLoading = true;
        });
        builder.addCase(fetchDocumentDetail.fulfilled, (state, action) => {
            state.isLoading = false;
            state.selectedDocument = action.payload;
        });
        builder.addCase(fetchDocumentDetail.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload as string;
        });

        // Delete document
        builder.addCase(deleteDocument.fulfilled, (state, action) => {
            state.documents = state.documents.filter(doc => doc.id !== action.payload);
        });
    },
});

export const { clearError, clearSelectedDocument } = documentsSlice.actions;
export default documentsSlice.reducer;
