import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
    User,
    LoginCredentials,
    RegisterData,
    AuthTokens,
    Document,
    DocumentDetail,
    ClinicalDecision,
    ClinicalQuery,
    ClinicalDecisionHistory,
} from '@/types';

class ApiService {
    private api: AxiosInstance;
    private accessToken: string | null = null;
    private refreshToken: string | null = null;

    constructor() {
        this.api = axios.create({
            baseURL: '/api/v1',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Load tokens from localStorage
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');

        // Request interceptor to add auth token
        this.api.interceptors.request.use(
            (config) => {
                if (this.accessToken) {
                    config.headers.Authorization = `Bearer ${this.accessToken}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor to handle token refresh
        this.api.interceptors.response.use(
            (response) => response,
            async (error: AxiosError) => {
                const originalRequest = error.config as any;

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        const tokens = await this.refreshAccessToken();
                        this.setTokens(tokens);

                        if (originalRequest.headers) {
                            originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
                        }

                        return this.api(originalRequest);
                    } catch (refreshError) {
                        this.clearTokens();
                        window.location.href = '/login';
                        return Promise.reject(refreshError);
                    }
                }

                return Promise.reject(error);
            }
        );
    }

    private setTokens(tokens: AuthTokens) {
        this.accessToken = tokens.access_token;
        this.refreshToken = tokens.refresh_token;
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
    }

    private clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    // Auth endpoints
    async register(data: RegisterData): Promise<User> {
        const response = await this.api.post<User>('/auth/register', data);
        return response.data;
    }

    async login(data: LoginCredentials): Promise<AuthTokens> {
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);

        const response = await this.api.post<AuthTokens>('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        this.setTokens(response.data);
        return response.data;
    }

    async refreshAccessToken(): Promise<AuthTokens> {
        if (!this.refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await this.api.post<AuthTokens>(
            `/auth/refresh?refresh_token=${this.refreshToken}`
        );

        return response.data;
    }

    async getCurrentUser(): Promise<User> {
        const response = await this.api.get<User>('/auth/me');
        return response.data;
    }

    logout() {
        this.clearTokens();
    }

    // Document endpoints
    async uploadDocument(file: File): Promise<Document> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.api.post<Document>('/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    }

    async listDocuments(): Promise<Document[]> {
        const response = await this.api.get<Document[]>('/documents/');
        return response.data;
    }

    async getDocument(id: string): Promise<DocumentDetail> {
        const response = await this.api.get<DocumentDetail>(`/documents/${id}`);
        return response.data;
    }

    async deleteDocument(id: string): Promise<void> {
        await this.api.delete(`/documents/${id}`);
    }

    // Clinical endpoints
    async analyzeClinical(query: ClinicalQuery): Promise<ClinicalDecision> {
        const response = await this.api.post<ClinicalDecision>('/clinical/analyze', query);
        return response.data;
    }

    async getClinicalHistory(limit = 50, skip = 0): Promise<ClinicalDecisionHistory[]> {
        const response = await this.api.get<ClinicalDecisionHistory[]>(
            `/clinical/history?limit=${limit}&skip=${skip}`
        );
        return response.data;
    }

    async getClinicalDecision(id: string): Promise<ClinicalDecision> {
        const response = await this.api.get<ClinicalDecision>(`/clinical/${id}`);
        return response.data;
    }

    async downloadPDF(id: string): Promise<Blob> {
        const response = await this.api.get(`/clinical/${id}/download/pdf`, {
            responseType: 'blob',
        });
        return response.data;
    }

    async downloadDOCX(id: string): Promise<Blob> {
        const response = await this.api.get(`/clinical/${id}/download/docx`, {
            responseType: 'blob',
        });
        return response.data;
    }

    isAuthenticated(): boolean {
        return !!this.accessToken;
    }
}

export const api = new ApiService();
