// These types mirror backend/src/schemas.py.
export type Mode = "ask" | "search" | "agent";
export interface DocumentInfo {
  id: string;
  filename: string;
  chunks: number;
}
export interface AppConfig {
  provider?: "openai" | "ollama";
  chat_model: string;
  embedding_model: string;
  max_pdf_mb: number;
}
export interface UploadResult {
  status: string;
  chunks: number;
  skipped_pages: number[];
}
export interface Source {
  label: string;
  chunk_id: string;
  filename: string;
  page: number;
  text: string;
  cosine_distance: number;
  rerank_score: number | null;
}
export interface ToolStep {
  tool: string;
  arguments: Record<string, unknown>;
  fallback: boolean;
}
export interface QueryResult {
  answer: string;
  sources: Source[];
  trace: ToolStep[];
}
export interface QueryRequest {
  question: string;
  mode: Mode;
  document_id: string | null;
  rerank: boolean;
}
