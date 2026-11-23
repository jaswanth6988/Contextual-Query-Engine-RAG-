import { FileText, Plus, Trash2, Layers } from "lucide-react";
import type { DocumentInfo } from "../types";

interface Props {
  documents: DocumentInfo[];
  selected: string | null;
  busy: boolean;
  maxSize: number;
  onSelect: (id: string | null) => void;
  onUpload: (files: File[]) => void;
  onDelete: (document: DocumentInfo) => void;
}

export function DocumentPanel({
  documents,
  selected,
  busy,
  maxSize,
  onSelect,
  onUpload,
  onDelete,
}: Props) {
  return (
    <aside className="sidebar">
      <div className="section-heading">
        <h2>Your documents</h2>
        <span className="count">{documents.length}</span>
      </div>
      <p className="muted small">Build a little library of knowledge.</p>
      <label className={`upload-zone ${busy ? "disabled" : ""}`}>
        <span className="upload-icon">
          <Plus size={22} />
        </span>
        <strong>Add PDF documents</strong>
        <span>Choose files · up to {maxSize} MB each</span>
        <input
          aria-label="Upload PDFs"
          type="file"
          accept=".pdf,application/pdf"
          multiple
          disabled={busy}
          onChange={(event) => {
            if (event.target.files) onUpload(Array.from(event.target.files));
            event.target.value = "";
          }}
        />
      </label>
      <button
        className={`scope-button ${selected === null ? "active" : ""}`}
        disabled={busy}
        onClick={() => onSelect(null)}
      >
        <Layers size={17} />
        <span>All documents</span>
        <span className="count">{documents.length}</span>
      </button>
      <div className="document-list">
        {documents.map((document) => (
          <div
            key={document.id}
            className={`document-row ${selected === document.id ? "selected" : ""}`}
          >
            <button
              className="document-select"
              disabled={busy}
              onClick={() => onSelect(document.id)}
              title={document.filename}
            >
              <FileText size={20} />
              <span>
                <strong>{document.filename}</strong>
                <small>
                  {document.chunks} indexed chunks · {document.id.slice(0, 6)}
                </small>
              </span>
            </button>
            <button
              className="icon-button"
              aria-label={`Remove ${document.filename}`}
              disabled={busy}
              onClick={() => onDelete(document)}
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}
        {!documents.length && (
          <p className="empty-library">
            Your PDFs will appear here.
            <br />
            Start with the included sample handbook.
          </p>
        )}
      </div>
      <div className="sidebar-note">
        <span className="status-dot" />
        Stored on your backend machine
        <p>Text-based PDFs work best. Scanned pages need OCR first.</p>
      </div>
    </aside>
  );
}
