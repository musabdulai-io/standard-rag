import axios, { type AxiosInstance } from 'axios';
import { getEnv } from './env';
import { getSessionId } from './session';

// Lazy-initialized axios instance (created on first request, after window.__ENV is loaded)
let apiInstance: AxiosInstance | null = null;

function getApiInstance(): AxiosInstance {
  if (!apiInstance) {
    apiInstance = axios.create({
      baseURL: `${getEnv('NEXT_PUBLIC_API_URL')}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
  return apiInstance;
}

// Types
export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'indexed' | 'failed';
  chunk_count: number;
  error_message?: string;
  is_sample: boolean;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  filename: string;
  text: string;
  score: number;
  chunk_index: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sources: SearchResult[];
}

// API functions
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', getSessionId());

  const response = await getApiInstance().post('/rag/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const listDocuments = async (): Promise<{ documents: Document[]; total: number }> => {
  const sessionId = getSessionId();
  const response = await getApiInstance().get(`/rag/documents?session_id=${sessionId}`);
  return response.data;
};

export const deleteDocument = async (id: string): Promise<void> => {
  const sessionId = getSessionId();
  await getApiInstance().delete(`/rag/documents/${id}?session_id=${sessionId}`);
};

export const searchDocuments = async (
  query: string,
  topK: number = 10,
  scoreThreshold: number = 0.5,
): Promise<SearchResponse> => {
  const response = await getApiInstance().post('/rag/search', {
    query,
    session_id: getSessionId(),
    top_k: topK,
    score_threshold: scoreThreshold,
  });
  return response.data;
};

export const queryDocuments = async (
  question: string,
  topK: number = 5,
): Promise<QueryResponse> => {
  const response = await getApiInstance().post('/rag/query', {
    question,
    session_id: getSessionId(),
    top_k: topK,
  });
  return response.data;
};

export const healthCheck = async (): Promise<{
  status: string;
  services: Record<string, string>;
}> => {
  const apiUrl = getEnv('NEXT_PUBLIC_API_URL');
  const response = await axios.get(`${apiUrl}/health`);
  return response.data;
};
