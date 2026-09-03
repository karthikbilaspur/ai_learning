type ChatEmptyStateProps = {
  onQuestionSelect: (
    question: string,
  ) => void;
};

const questions = [
  "Build a landing page with Tailwind",
  "Explain RAG in simple terms",
  "Write a rate limiter in Node",
  "Debug my streaming response",
];

export function ChatEmptyState({
  onQuestionSelect,
}: ChatEmptyStateProps) {
  return (
    <div className="text-center mt-20 space-y-4">
      <div className="text-4xl">✨</div>

      <h2 className="text-2xl font-semibold">
        How can I help you today?
      </h2>

      <div className="grid sm:grid-cols-2 gap-2 max-w-lg mx-auto mt-6">
        {questions.map((question) => (
          <button
            key={question}
            onClick={() =>
              onQuestionSelect(question)
            }
            className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-left hover:bg-zinc-800 transition"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}