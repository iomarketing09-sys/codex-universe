import re

def parse_publication_contexts_real(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # We'll split by lines that start with a date pattern like "dia ", "6 de septiembre", "7 DE SEPTIEMBRE", "08 DE SEPTIEMBRE"
    # Actually, we can split by double newline and then try to parse each block.
    blocks = content.split('\n\n')
    contexts = []
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
        ctx = {}
        # We'll look for known prefixes
        for line in lines:
            if line.lower().startswith('hora:'):
                ctx['hora'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('posturl:') or line.lower().startswith('posurl:'):
                # Extract URL from markdown link if present
                match = re.search(r'\[.*\]\((http[^)]+)\)', line)
                if match:
                    ctx['postURL'] = match.group(1)
                else:
                    ctx['postURL'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('asset:'):
                ctx['asset'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('meme:'):
                ctx['meme'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('caption:'):
                ctx['caption'] = line.split(':', 1)[1].strip()
            # Also handle lines like "dia 5 de Septiembre" - we can ignore for now
        # Only add if we have essential fields
        if ctx.get('asset') and ctx.get('postURL'):
            # Set defaults
            ctx.setdefault('hora', '')
            ctx.setdefault('meme', '')
            ctx.setdefault('caption', '')
            contexts.append(ctx)
    return contexts

if __name__ == '__main__':
    ctxs = parse_publication_contexts_real('../Coment_Responses_Universe/Publication_Contexts_Real_Universe.md')
    print(f"Found {len(ctxs)} publications")
    for i, ctx in enumerate(ctxs):
        print(f"{i}: {ctx}")
