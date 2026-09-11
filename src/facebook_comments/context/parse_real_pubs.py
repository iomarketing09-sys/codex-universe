import re


def parse_publication_contexts_real(md_path):
    """Parse publication notes into the schema consumed by UniverseResponder."""
    contexts = []
    current = None

    def finish():
        if not current or not current.get("post_url"):
            return
        current.setdefault("publication_id", None)
        current.setdefault("published_at", None)
        current.setdefault("asset_ref", "")
        current.setdefault("character", "")
        current.setdefault("visual_context", "")
        current.setdefault("meme_text", "")
        current.setdefault("caption", "")
        contexts.append(dict(current))

    with open(md_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()

            if lower.startswith("hora:"):
                finish()
                current = {"hora": line.split(":", 1)[1].strip()}
                continue
            if current is None:
                continue
            if lower.startswith("posturl:") or lower.startswith("posurl:"):
                match = re.search(r"\[.*?\]\((http[^)]+)\)", line)
                current["post_url"] = match.group(1) if match else line.split(":", 1)[1].strip()
            elif lower.startswith("asset:"):
                current["asset_ref"] = line.split(":", 1)[1].strip()
            elif lower.startswith("meme:"):
                current["meme_text"] = line.split(":", 1)[1].strip()
            elif lower.startswith("caption:"):
                current["caption"] = line.split(":", 1)[1].strip()

    finish()
    return contexts


if __name__ == "__main__":
    ctxs = parse_publication_contexts_real("../Coment_Responses_Universe/Publication_Contexts_Real_Universe.md")
    print(f"Found {len(ctxs)} publications")
    for i, ctx in enumerate(ctxs):
        print(f"{i}: {ctx}")
