import { db } from "@/lib/db";
import { jsonError } from "@/lib/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const conversation = await db.conversation.findUnique({
      where: { id },
      include: { messages: { orderBy: { createdAt: "asc" } } },
    });
    if (!conversation) return jsonError("Conversation not found.", 404);
    return Response.json({ conversation });
  } catch (error) {
    console.error("[CONVERSATION_GET]", error);
    return jsonError("Unable to load conversation.", 500);
  }
}

export async function DELETE(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    await db.conversation.delete({ where: { id } });
    return Response.json({ ok: true });
  } catch (error) {
    console.error("[CONVERSATION_DELETE]", error);
    return jsonError("Unable to delete conversation.", 500);
  }
}
