// FIX (portfolio pass): cache hits previously returned plain JSON while
// cache misses returned result.toDataStreamResponse() — two different wire
// formats for the same endpoint, forcing every client to branch on the
// X-Cache header just to parse the body. This wraps a plain string answer
// in the same Vercel AI SDK data-stream-protocol wire format used for
// streamed responses, so `useChat`/any data-stream client can consume both
// without special-casing cache hits.

export function textToDataStreamResponse(text: string, headers: Record<string, string> = {}): Response {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      const escaped = text.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n')
      controller.enqueue(encoder.encode(`0:"${escaped}"\n`))
      controller.enqueue(
        encoder.encode(`d:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n`)
      )
      controller.close()
    },
  })
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'x-vercel-ai-data-stream': 'v1',
      ...headers,
    },
  })
}
