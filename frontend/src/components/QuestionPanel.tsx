import { ArrowUpRight, MessageSquare, Search, Workflow } from "lucide-react";
import type { Mode } from "../types";

const modes = [
  { id: "ask" as const, label: "Ask documents", icon: MessageSquare },
  { id: "search" as const, label: "Semantic search", icon: Search },
  { id: "agent" as const, label: "Agent mode", icon: Workflow },
];
interface Props {
  question: string;
  mode: Mode;
  rerank: boolean;
  busy: boolean;
  hasDocuments: boolean;
  onQuestion: (question: string) => void;
  onMode: (mode: Mode) => void;
  onRerank: (enabled: boolean) => void;
  onSubmit: () => void;
}
export function QuestionPanel(props: Props) {
  const {
    question,
    mode,
    rerank,
    busy,
    hasDocuments,
    onQuestion,
    onMode,
    onRerank,
    onSubmit,
  } = props;
  return (
    <section className="question-panel">
      <div className="mode-tabs" aria-label="Query mode">
        {modes.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={mode === id ? "active" : ""}
            aria-pressed={mode === id}
            disabled={busy}
            onClick={() => onMode(id)}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <label htmlFor="question" className="sr-only">
          Your question
        </label>
        <textarea
          id="question"
          value={question}
          disabled={busy}
          maxLength={4000}
          onChange={(event) => onQuestion(event.target.value)}
          placeholder={
            mode === "search"
              ? "Find a passage by its meaning…"
              : "What would you like to know about your documents?"
          }
        />
        <div className="composer-footer">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={rerank}
              disabled={busy}
              onChange={(event) => onRerank(event.target.checked)}
            />
            Rerank results
          </label>
          <button
            className="primary-button"
            disabled={busy || !hasDocuments || !question.trim()}
            type="submit"
          >
            {busy
              ? "Working…"
              : mode === "search"
                ? "Find passages"
                : "Get answer"}
            <ArrowUpRight size={17} />
          </button>
        </div>
      </form>
      <p className="composer-hint">
        {rerank
          ? "Reranking requires the optional Python dependencies and downloads a model on first use."
          : mode === "agent"
            ? "The agent can list documents and run focused searches. Its tool calls are visible below."
            : "Each question stands alone. Answers link back to the retrieved evidence."}
      </p>
    </section>
  );
}
