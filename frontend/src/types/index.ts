// User types
export interface User {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string;
}

export interface LoginCredentials {
    username: string;
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name: string;
}

export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

// Document types
export interface Document {
    id: string;
    filename: string;
    file_type: 'pdf' | 'txt' | 'docx' | 'doc';
    file_size: number;
    upload_date: string;
    processed: boolean;
}

export interface DocumentDetail extends Document {
    extracted_text?: string;
    chunk_count: number;
}

// Clinical Decision types
export interface Citation {
    document_id: string;
    document_name: string;
    excerpt: string;
    relevance_score: number;
}

export interface ClinicalDecision {
    id: string;
    query: string;
    decision: string;
    confidence_score?: number;
    citations: Citation[];
    created_at: string;
}

export interface ClinicalQuery {
    query: string;
    document_ids: string[];
    include_history: boolean;
}

export interface ClinicalDecisionHistory {
    id: string;
    query: string;
    decision_summary: string;
    created_at: string;
    document_count: number;
}

// API Response types
export interface ApiError {
    detail: string;
}
