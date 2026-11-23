import ReactMarkdown from "react-markdown";
import { BookOpen, FileText, Workflow } from "lucide-react";
import type { QueryResult } from "../types";

export function AnswerPanel({
  result,
  question,
}: {
  result: QueryResult;
  question: string;
}) {
  return (
    <section className="answer-panel">
      <div className="eyebrow">
        <BookOpen size={15} /> FROM YOUR DOCUMENTS
      </div>
      <h2>{question}</h2>
      <div className="answer-text">
        <ReactMarkdown>{result.answer}</ReactMarkdown>
      </div>
      <div className="sources-heading">
        <h3>Supporting evidence</h3>
        <span className="count">{result.sources.length} passages</span>
      </div>
      <div className="sources-grid">
        {result.sources.map((source) => (
          <details key={source.chunk_id} className="source-card">
            <summary>
              <span className="source-label">{source.label}</span>
              <span className="source-title">
                <strong>{source.filename}</strong>
                <small>Page {source.page}</small>
              </span>
              <FileText size={16} />
            </summary>
            <p className="source-text">{source.text}</p>
            <div className="source-scores">
              Cosine distance: {source.cosine_distance.toFixed(4)} · lower is
              closer
              {source.rerank_score !== null && (
                <>
                  <br />
                  Rerank score: {source.rerank_score.toFixed(4)} · higher ranks
                  first
                </>
              )}
            </div>
          </details>
        ))}
      </div>
      {result.trace.length > 0 && (
        <details className="trace">
          <summary>
            <Workflow size={16} />
            Tool execution · {result.trace.length} steps
          </summary>
          <ol>
            {result.trace.map((step, index) => (
              <li key={index}>
                <strong>{step.tool}</strong>
                {step.fallback && " (fallback search)"}
                <pre>{JSON.stringify(step.arguments, null, 2)}</pre>
              </li>
            ))}
          </ol>
        </details>
      )}
      <p className="muted small">
        Check important claims against the original PDF. Retrieval scores are
        not confidence percentages.
      </p>
    </section>
  );
}
