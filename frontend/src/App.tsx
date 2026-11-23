import { useEffect, useState } from "react";
import { ArrowUpRight, BookOpen, Command, RefreshCw } from "lucide-react";
import { api } from "./api";
import { DocumentPanel } from "./components/DocumentPanel";
import { QuestionPanel } from "./components/QuestionPanel";
import { AnswerPanel } from "./components/AnswerPanel";
import type { AppConfig, DocumentInfo, Mode, QueryResult } from "./types";

// This app is small enough for React state. Each child receives only the props it needs.
export default function App() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<Mode>("ask");
  const [rerank, setRerank] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [answeredQuestion, setAnsweredQuestion] = useState("");

  async function refresh() {
    setError("");
    try {
      const [nextDocuments, nextConfig] = await Promise.all([
        api.documents(),
        api.config(),
      ]);
      setDocuments(nextDocuments);
      setConfig(nextConfig);
      setSelected((current) =>
        nextDocuments.some((d) => d.id === current) ? current : null,
      );
    } catch (error) {
      showError(error);
    }
  }
  useEffect(() => {
    void refresh();
  }, []);

  function showError(error: unknown) {
    setError(
      error instanceof Error
        ? error.message
        : "Something went wrong. Please try again.",
    );
  }
  function changeScope(id: string | null) {
    setSelected(id);
    setResult(null);
  }

  async function upload(files: File[]) {
    setBusy(true);
    setError("");
    setNotice("");
    setResult(null);
    const messages: string[] = [];
    try {
      // Sequential uploads keep memory use and model work predictable on a laptop.
      for (const file of files) {
        if (!file.name.toLowerCase().endsWith(".pdf"))
          throw new Error("Please choose PDF files.");
        if (file.size > (config?.max_pdf_mb ?? 20) * 1024 * 1024)
          throw new Error(`${file.name} exceeds the upload size limit.`);
        setNotice(`Indexing ${file.name}…`);
        const response = await api.upload(file);
        const skipped = response.skipped_pages.length
          ? ` Skipped empty pages: ${response.skipped_pages.join(", ")}.`
          : "";
        messages.push(
          `${file.name}: ${response.status}, ${response.chunks} new chunks.${skipped}`,
        );
        // Keep successful earlier files visible if a later file fails.
        setDocuments(await api.documents());
      }
    } catch (error) {
      showError(error);
    } finally {
      setNotice(messages.join("\n"));
      setBusy(false);
    }
  }

  async function remove(document: DocumentInfo) {
    if (
      !window.confirm(
        `Remove the index for "${document.filename}"? You can upload it again later.`,
      )
    )
      return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api.remove(document.id);
      setDocuments((current) =>
        current.filter((item) => item.id !== document.id),
      );
      if (selected === document.id) setSelected(null);
      setResult(null);
      setNotice(`${document.filename} removed.`);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  async function submit() {
    if (!question.trim() || busy || !documents.length) return;
    setBusy(true);
    setError("");
    setNotice("");
    setResult(null);
    try {
      const response = await api.query({
        question,
        mode,
        document_id: selected,
        rerank,
      });
      setResult(response);
      setAnsweredQuestion(question);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">
            <Command size={22} />
          </span>
          contextual<span className="brand-dot">.</span>
        </a>
        <span className="workspace-label">PDF KNOWLEDGE WORKSPACE</span>
        <button
          className="refresh-button"
          onClick={() => void refresh()}
          disabled={busy}
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </header>
      <div className="workspace">
        <DocumentPanel
          documents={documents}
          selected={selected}
          busy={busy}
          maxSize={config?.max_pdf_mb ?? 20}
          onSelect={changeScope}
          onUpload={upload}
          onDelete={remove}
        />
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">READ LESS. UNDERSTAND MORE.</div>
              <h1>
                A clearer view of
                <br />
                your documents.
              </h1>
              <p>Turn pages of information into answers you can trace.</p>
            </div>
            <span className="heading-symbol">
              <BookOpen size={42} strokeWidth={1.2} />
            </span>
          </div>
          <div className="scope-caption">
            <span className="status-dot" />
            {selected
              ? documents.find((d) => d.id === selected)?.filename
              : "Searching across your library"}
            <span>
              {documents.reduce((sum, doc) => sum + doc.chunks, 0)} indexed
              chunks
            </span>
          </div>
          <QuestionPanel
            question={question}
            mode={mode}
            rerank={rerank}
            busy={busy}
            hasDocuments={documents.length > 0}
            onQuestion={setQuestion}
            onMode={(next) => {
              setMode(next);
              setResult(null);
            }}
            onRerank={setRerank}
            onSubmit={submit}
          />
          {error && (
            <div className="message error" role="alert">
              {error}
            </div>
          )}
          {notice && (
            <div className="message notice" role="status">
              {notice}
            </div>
          )}
          {busy && (
            <div className="working" role="status">
              <span className="spinner" />
              Working with your documents. Model requests may take a moment.
            </div>
          )}
          {result ? (
            <AnswerPanel result={result} question={answeredQuestion} />
          ) : (
            !busy && (
              <section className="getting-started">
                <div className="section-heading">
                  <h2>A good place to start</h2>
                  <span className="muted small">TRY THE SAMPLE HANDBOOK</span>
                </div>
                <div className="suggestions">
                  {[
                    "How many days of annual leave are provided?",
                    "What is the reimbursement limit for learning?",
                    "Compare the leave and learning policies.",
                  ].map((text, i) => (
                    <button key={text} onClick={() => setQuestion(text)}>
                      <span className="suggestion-number">0{i + 1}</span>
                      <span>{text}</span>
                      <ArrowUpRight size={17} />
                    </button>
                  ))}
                </div>
                <p className="muted small">
                  Upload a PDF on the left, choose a question, and inspect the
                  source passages below your answer.
                </p>
              </section>
            )
          )}
          <footer>
            <span>Built for curious minds.</span>
            <span>
              {config
                ? `${config.provider ?? ""} · ${config.chat_model} · ${config.embedding_model}`
                : "Connect to FastAPI to get started"}
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
