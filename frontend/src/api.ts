import type {
  AppConfig,
  DocumentInfo,
  QueryRequest,
  QueryResult,
  UploadResult,
} from "./types";

// One place for network requests and readable error messages.
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, options);
  } catch {
    throw new Error("Cannot reach the backend. Start FastAPI and try again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(
      typeof body?.detail === "string"
        ? body.detail
        : `Request failed (${response.status}). Check your input and backend terminal.`,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  documents: () => request<DocumentInfo[]>("/documents"),
  config: () => request<AppConfig>("/config"),
  upload: (file: File) => {
    const data = new FormData();
    data.append("file", file);
    return request<UploadResult>("/documents", { method: "POST", body: data });
  },
  remove: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),
  query: (body: QueryRequest) =>
    request<QueryResult>("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
