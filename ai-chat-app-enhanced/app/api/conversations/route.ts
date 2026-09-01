import { db } from "@/lib/db";
import { jsonError } from "@/lib/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const conversations = await db.conversation.findMany({
      orderBy: { updatedAt: "desc" },
      take: 50,
      select: { id: true, title: true, promptKey: true, createdAt: true, updatedAt: true },
    });
    return Response.json({ conversations });
  } catch (error) {
    console.error("[CONVERSATIONS_GET]", error);
    return jsonError("Unable to load conversations.", 500);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const title = typeof body.title === "string" && body.title.trim() ? body.title.trim().slice(0, 100) : "New chat";
    const promptKey = typeof body.promptKey === "string" ? body.promptKey : "default";

    const conversation = await db.conversation.create({ data: { title, promptKey } });
    return Response.json({ conversation }, { status: 201 });
  } catch (error) {
    console.error("[CONVERSATIONS_POST]", error);
    return jsonError("Unable to create conversation.", 500);
  }
}
