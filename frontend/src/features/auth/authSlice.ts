import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '@/services/api';
import type { User, LoginCredentials, RegisterData } from '@/types';

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    user: null,
    isAuthenticated: api.isAuthenticated(),
    isLoading: false,
    error: null,
};

// Async thunks
export const login = createAsyncThunk(
    'auth/login',
    async (credentials: LoginCredentials, { rejectWithValue }) => {
        try {
            await api.login(credentials);
            const user = await api.getCurrentUser();
            return user;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Login failed');
        }
    }
);

export const register = createAsyncThunk(
    'auth/register',
    async (data: RegisterData, { rejectWithValue }) => {
        try {
            const user = await api.register(data);
            return user;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Registration failed');
        }
    }
);

export const fetchCurrentUser = createAsyncThunk(
    'auth/fetchCurrentUser',
    async (_, { rejectWithValue }) => {
        try {
            const user = await api.getCurrentUser();
            return user;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user');
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            api.logout();
            state.user = null;
            state.isAuthenticated = false;
            state.error = null;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        // Login
        builder.addCase(login.pending, (state) => {
            state.isLoading = true;
            state.error = null;
        });
        builder.addCase(login.fulfilled, (state, action: PayloadAction<User>) => {
            state.isLoading = false;
            state.user = action.payload;
            state.isAuthenticated = true;
        });
        builder.addCase(login.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload as string;
        });

        // Register
        builder.addCase(register.pending, (state) => {
            state.isLoading = true;
            state.error = null;
        });
        builder.addCase(register.fulfilled, (state, action: PayloadAction<User>) => {
            state.isLoading = false;
            state.user = action.payload;
        });
        builder.addCase(register.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload as string;
        });

        // Fetch current user
        builder.addCase(fetchCurrentUser.pending, (state) => {
            state.isLoading = true;
        });
        builder.addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
            state.isLoading = false;
            state.user = action.payload;
            state.isAuthenticated = true;
        });
        builder.addCase(fetchCurrentUser.rejected, (state) => {
            state.isLoading = false;
            state.isAuthenticated = false;
            state.user = null;
        });
    },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
