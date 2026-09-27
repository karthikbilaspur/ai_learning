// Wraps a plain string answer in the same Vercel AI SDK data-stream
// protocol used for streamed responses, so useChat can consume both
// cache hits and misses without branching.

export function textToDataStreamResponse(text: string, headers: Record<string, string> = {}): Response {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      // JSON.stringify handles \n, \r, ", \, unicode, etc correctly
      controller.enqueue(encoder.encode(`0:${JSON.stringify(text)}\n`))
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