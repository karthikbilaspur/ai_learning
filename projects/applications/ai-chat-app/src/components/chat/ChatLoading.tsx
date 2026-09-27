type ChatLoadingProps = {
  onStop: () => void;
};

export function ChatLoading({
  onStop,
}: ChatLoadingProps) {
  return (
    <div className="flex gap-2 items-center text-zinc-500 text-sm">
      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" />

      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.2s]" />

      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.4s]" />

      <button
        onClick={onStop}
        className="ml-3 border border-zinc-700 rounded-full px-3 py-1 text-xs hover:bg-zinc-800"
      >
        Stop
      </button>
    </div>
  );
}