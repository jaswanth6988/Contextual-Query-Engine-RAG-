import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { api } from "./api";

vi.mock("./api", () => ({
  api: {
    documents: vi.fn(),
    config: vi.fn(),
    query: vi.fn(),
    upload: vi.fn(),
    remove: vi.fn(),
  },
}));
const document = { id: "a".repeat(64), filename: "handbook.pdf", chunks: 2 };
beforeEach(() => {
  vi.mocked(api.documents).mockResolvedValue([document]);
  vi.mocked(api.config).mockResolvedValue({
    chat_model: "test-model",
    embedding_model: "test-embedding",
    max_pdf_mb: 20,
  });
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

test("asks a question and shows page-level evidence", async () => {
  vi.mocked(api.query).mockResolvedValue({
    answer: "Employees receive 24 days. [S1]",
    sources: [
      {
        label: "S1",
        chunk_id: "one",
        filename: "handbook.pdf",
        page: 1,
        text: "24 days of annual leave.",
        cosine_distance: 0.15,
        rerank_score: null,
      },
    ],
    trace: [],
  });
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText("handbook.pdf");
  await user.type(
    screen.getByLabelText("Your question"),
    "How many leave days?",
  );
  await user.click(screen.getByRole("button", { name: "Get answer" }));
  await screen.findByText("Employees receive 24 days. [S1]");
  expect(api.query).toHaveBeenCalledWith({
    question: "How many leave days?",
    mode: "ask",
    document_id: null,
    rerank: false,
  });
  expect(screen.getByText("Page 1")).toBeTruthy();
});

test("uploads a PDF and removes its index after confirmation", async () => {
  vi.mocked(api.documents)
    .mockResolvedValueOnce([])
    .mockResolvedValue([document]);
  vi.mocked(api.upload).mockResolvedValue({
    status: "indexed",
    chunks: 2,
    skipped_pages: [3],
  });
  vi.mocked(api.remove).mockResolvedValue(undefined);
  vi.spyOn(window, "confirm").mockReturnValue(true);
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText(/Your PDFs will appear here/);
  await user.upload(
    screen.getByLabelText("Upload PDFs"),
    new File(["%PDF-test"], "handbook.pdf", { type: "application/pdf" }),
  );
  await screen.findByText(/Skipped empty pages: 3/);
  await user.click(screen.getByRole("button", { name: "Remove handbook.pdf" }));
  await waitFor(() => expect(api.remove).toHaveBeenCalledWith(document.id));
  await screen.findByText("handbook.pdf removed.");
});

test("shows backend errors and allows retry", async () => {
  vi.mocked(api.query).mockRejectedValueOnce(
    new Error("Ollama is unavailable."),
  );
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText("handbook.pdf");
  await user.type(screen.getByLabelText("Your question"), "Explain the policy");
  await user.click(screen.getByRole("button", { name: "Get answer" }));
  expect((await screen.findByRole("alert")).textContent).toContain(
    "Ollama is unavailable.",
  );
  expect(
    (screen.getByRole("button", { name: "Get answer" }) as HTMLButtonElement)
      .disabled,
  ).toBe(false);
});
