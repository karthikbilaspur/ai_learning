"""
Repo ingestion: clone -> AST-aware chunking -> embeddings -> BM25 corpus ->
a name-based static call graph.

Call graph note (read this before trusting it blindly): this is a
*name-based* heuristic, not a scope-resolved one. If two files each define
a function called `handle`, a call to `handle()` will be linked to both.
That's a real limitation of doing this without a full type/scope resolver
(which is a much bigger project), and it's called out in the README rather
than hidden behind a green checkmark.
"""

import json
import os
import shutil

from git import Repo
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tree_sitter_languages import get_parser

from ..vectorstore import get_chroma, get_embedding_model

LANG_MAP = {".js": "javascript", ".ts": "typescript", ".py": "python", ".jsx": "javascript", ".tsx": "typescript"}

DEFINITION_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "class_definition",
    "class_declaration",
}

# Tree-sitter node types that represent a call site, per language family.
CALL_TYPES = {"call_expression", "call"}

MAX_FILE_CHARS = 20_000
DATA_ROOT = "./chroma_db"


def _node_name(node) -> str | None:
    """Best-effort extraction of a definition's identifier via tree-sitter's
    named field, falling back to None (chunk still gets indexed, just
    without a call-graph-linkable name)."""
    name_node = node.child_by_field_name("name")
    if name_node is not None:
        return name_node.text.decode("utf-8", errors="ignore")
    return None


def _callee_name(call_node) -> str | None:
    """Extract the identifier being called from a call/call_expression node.
    Handles plain calls (`foo()`) and attribute/member calls (`obj.foo()`),
    in which case we key off the trailing property name."""
    fn_node = call_node.child_by_field_name("function")
    if fn_node is None:
        return None
    if fn_node.type in ("identifier",):
        return fn_node.text.decode("utf-8", errors="ignore")
    if fn_node.type in ("member_expression", "attribute"):
        prop = fn_node.child_by_field_name("property") or fn_node.child_by_field_name("attribute")
        if prop is not None:
            return prop.text.decode("utf-8", errors="ignore")
    return None


def parse_file(file_path: str, content: str):
    """
    Parse one file with tree-sitter and return:
      - chunks: [{text, type, name, start_line, end_line, file}]
      - calls: [{caller_start_line, caller_end_line, callee_name, line}]
    for languages we support. `calls` is every call site found in the file,
    independent of chunk boundaries, so the caller can be resolved later by
    line-range containment.
    """
    ext = os.path.splitext(file_path)[1]
    lang = LANG_MAP.get(ext)
    chunks, calls = [], []

    if lang:
        try:
            parser = get_parser(lang)
            tree = parser.parse(bytes(content, "utf-8"))
            lines = content.split("\n")

            def walk(node):
                if node.type in DEFINITION_TYPES:
                    start, end = node.start_point[0], node.end_point[0]
                    snippet = "\n".join(lines[start : end + 1])
                    if len(snippet.strip()) > 30:
                        chunks.append(
                            {
                                "text": snippet,
                                "type": node.type,
                                "name": _node_name(node) or "",
                                "start_line": start,
                                "end_line": end,
                                "file": file_path,
                            }
                        )
                elif node.type in CALL_TYPES:
                    callee = _callee_name(node)
                    if callee:
                        calls.append({"line": node.start_point[0], "callee": callee})
                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception as exc:
            print(f"AST parse failed for {file_path}: {exc}")

    if not chunks:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        for piece in splitter.split_text(content):
            chunks.append({"text": piece, "type": "chunk", "name": "", "start_line": 0, "end_line": 0, "file": file_path})

    return chunks, calls


def _enclosing_chunk(chunks: list, line: int):
    """Find the smallest definition chunk in this file whose line range
    contains `line`, i.e. the function/method a call site lives inside."""
    best = None
    for chunk in chunks:
        if chunk["type"] == "chunk":
            continue
        if chunk["start_line"] <= line <= chunk["end_line"]:
            if best is None or (chunk["end_line"] - chunk["start_line"]) < (best["end_line"] - best["start_line"]):
                best = chunk
    return best


def build_call_graph(all_chunks: list, all_calls: list):
    """
    Build a name-based call graph.

    Nodes are every named function/class definition (qualified as
    `file::name` so same-named functions in different files stay distinct).
    Edges connect a caller node to every definition anywhere in the repo
    whose bare name matches the call site — this is the over-approximation
    documented at the top of this file.
    """
    # name -> list of qualified ids sharing that name (repo-wide, ambiguous by design)
    by_name: dict[str, list[str]] = {}
    nodes = []
    for chunk in all_chunks:
        if not chunk["name"]:
            continue
        qid = f"{chunk['file']}::{chunk['name']}"
        nodes.append({"id": qid, "label": chunk["name"], "file": chunk["file"], "type": chunk["type"]})
        by_name.setdefault(chunk["name"], []).append(qid)

    edges = []
    seen_edges = set()
    for file_path, chunks, calls in all_calls:
        for call in calls:
            caller_chunk = _enclosing_chunk(chunks, call["line"])
            if caller_chunk is None or not caller_chunk["name"]:
                continue
            caller_id = f"{file_path}::{caller_chunk['name']}"
            for callee_id in by_name.get(call["callee"], []):
                if callee_id == caller_id:
                    continue
                edge_key = (caller_id, callee_id)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append({"source": caller_id, "target": callee_id})

    return {"nodes": nodes, "edges": edges}


def ingest_repo_advanced(repo_url: str, repo_id: str):
    tmp_dir = f"/tmp/repo_{repo_id}"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    print(f"Cloning {repo_url} -> {tmp_dir}")
    Repo.clone_from(repo_url, tmp_dir, depth=1)

    all_chunks = []
    per_file_calls = []  # (file_path, chunks_for_that_file, calls_for_that_file)
    files_count = 0

    for root, dirs, files in os.walk(tmp_dir):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist", "build", "__pycache__")]
        for file in files:
            if not file.endswith((".js", ".ts", ".jsx", ".tsx", ".py", ".md")):
                continue
            fp = os.path.join(root, file)
            rel = os.path.relpath(fp, tmp_dir)
            try:
                with open(fp, "r", errors="ignore") as f:
                    content = f.read()
                if len(content) > MAX_FILE_CHARS:
                    continue

                file_chunks, file_calls = parse_file(rel, content)
                for chunk in file_chunks:
                    chunk["id"] = f"{repo_id}_{rel}_{chunk['start_line']}_{len(all_chunks)}"
                all_chunks.extend(file_chunks)
                per_file_calls.append((rel, file_chunks, file_calls))
                files_count += 1
            except Exception as exc:
                print(f"skip {rel}: {exc}")

    print(f"Total AST chunks: {len(all_chunks)} from {files_count} files")

    call_graph = build_call_graph(all_chunks, per_file_calls)
    print(f"Call graph: {len(call_graph['nodes'])} nodes, {len(call_graph['edges'])} edges")

    # Embed and store in Chroma
    chroma = get_chroma(repo_id)
    embed_model = get_embedding_model()
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_model.encode(texts, show_progress_bar=True, batch_size=32) if texts else []

    if texts:
        chroma.add(
            ids=[c["id"] for c in all_chunks],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[
                {"file": c["file"], "line": c["start_line"], "type": c["type"], "name": c["name"]} for c in all_chunks
            ],
        )

    repo_dir = os.path.join(DATA_ROOT, repo_id)
    os.makedirs(repo_dir, exist_ok=True)

    with open(os.path.join(repo_dir, "bm25.json"), "w") as f:
        json.dump({"chunks": all_chunks}, f)

    with open(os.path.join(repo_dir, "call_graph.json"), "w") as f:
        json.dump(call_graph, f)

    return {
        "name": repo_url.rstrip("/").split("/")[-1].removesuffix(".git"),
        "files": files_count,
        "chunks": len(all_chunks),
        "path": tmp_dir,
        "call_graph_nodes": len(call_graph["nodes"]),
        "call_graph_edges": len(call_graph["edges"]),
    }


def load_call_graph(repo_id: str) -> dict:
    path = os.path.join(DATA_ROOT, repo_id, "call_graph.json")
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"nodes": [], "edges": []}


def find_callers(repo_id: str, function_name: str) -> list[str]:
    """Everyone who calls a function with this bare name, anywhere in the repo."""
    graph = load_call_graph(repo_id)
    matches = {n["id"] for n in graph["nodes"] if n["label"] == function_name}
    callers = [e["source"] for e in graph["edges"] if e["target"] in matches]
    return sorted(set(callers))
