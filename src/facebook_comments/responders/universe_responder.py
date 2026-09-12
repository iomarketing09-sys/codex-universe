# universe_responder.py
"""
Minimum implementation of the comment responder for Universe Sent Me.
Follows the CONTRACT_COMMENT_RESPONSES.md and the Manual/Ejemplos.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import re


class UniverseResponder:
    def __init__(self) -> None:
        # Simple keyword maps for classification (can be expanded)
        self.humor_keywords = ["jaja", "ja ja", "😂", "lol", "risas", "crack", "divertido", "gracioso", "🤣", "jajaja"]
        self.identification_keywords = ["me pasa", "soy yo", "igual", "también", "yo también", "a mí me"]
        self.personal_experience_keywords = ["me pasó", "mi experiencia", "personal", "en mi caso", "a mí me sucedió"]
        self.story_keywords = ["novio", "novia", "historia", "chisme", "cuentame", "algo pasó", "algo pasó"]
        self.question_keywords = ["?", "cómo", "qué", "cuándo", "dónde", "por qué", "cuál", "será"]
        self.affection_keywords = ["amo", "love", "te quiero", "adoro", "♥", "💖", "te amo", "me encanta"]
        self.opinion_keywords = ["pienso", "creo", "opino", "parece", "me parece", "opinion", "creo que"]
        self.disagreement_keywords = ["no", "no creo", "discrepo", "falso", "incorrecto", "estás equivocado", "pero", "sin embargo"]
        self.troll_keywords = ["idiota", "estúpido", "molesto", "odio", "baste", "callate", "cállate", "basura", "peor", "peor aún"]
        self.commercial_keywords = ["compro", "vendo", "precio", "cuánto cuesta", "dónde compro", "link", "promo", "descuento", "oferta"]
        self.spam_keywords = ["http", ".com", "www", "follow me", "suscribete", "visita mi", "gana dinero", "bitcoin", "cripto"]
        self.mention_pattern = "@"

    def _classify_comment(self, comment: str) -> str:
        comment_lower = comment.lower()
        if any(k in comment_lower for k in self.spam_keywords):
            return "spam"
        if any(k in comment_lower for k in self.troll_keywords):
            return "troll"
        if any(k in comment_lower for k in self.commercial_keywords):
            return "commercial_intent"
        if any(k in comment_lower for k in self.question_keywords):
            return "question"
        if any(k in comment_lower for k in self.affection_keywords):
            return "affection"
        if any(k in comment_lower for k in self.opinion_keywords):
            return "opinion"
        if any(k in comment_lower for k in self.disagreement_keywords):
            return "disagreement"
        if any(k in comment_lower for k in self.identification_keywords):
            return "identification"
        if any(k in comment_lower for k in self.personal_experience_keywords):
            return "personal_experience"
        if any(k in comment_lower for k in self.story_keywords):
            return "story_or_gossip"
        if any(k in comment_lower for k in self.humor_keywords):
            return "humor"
        if self.mention_pattern in comment:
            return "mention"
        return "other"

    def _intention_apparent(self, comment_type: str, comment: str) -> str:
        intentions = {
            "humor": "Está expresando humor o risa ante la publicación.",
            "identification": "Se identifica con la situación o personaje de la publicación.",
            "personal_experience": "Está compartiendo una experiencia personal relacionada.",
            "story_or_gossip": "Está mencionando una historia personal o chisme relacionado.",
            "question": "Está haciendo una pregunta legítima sobre la publicación o su contenido.",
            "affection": "Está expresando afecto o apoyo hacia la publicación o su creador.",
            "opinion": "Está dando una opinión o interpretación del contenido.",
            "disagreement": "Está expresando desacuerdo o crítica constructiva.",
            "troll": "Está intentando provocar o molestar (troll).",
            "commercial_intent": "Muestra intención de comprar, vender o consultar sobre un producto/servicio.",
            "spam": "Es contenido promocional no relacionado o mensaje repetitivo.",
        "mention": "Está mencionando a otro usuario o participando en una conversación entre usuarios.",
            "other": "Intención no clara a partir del comentario.",
        }
        return intentions.get(comment_type, "Intención no determinada.")

    def _relation_to_meme(self, publication_context: Dict[str, Any], comment: str) -> str:
        """Determine the relationship between comment and publication context."""
        # stopwords from contract
        stopwords = {"el", "la", "los", "las", "un", "una", "y", "o", "de", "del", "al", "en", "con", "por", "para", "se", "lo", "su", "sus", "mi", "mis", "tu", "tus", "que", "como", "más", "pero", "sin", "sobre"}
        def sig_words(text):
            import re
            words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
            return [w for w in words if w not in stopwords]
        meme_text = publication_context.get("meme_text", "")
        caption = publication_context.get("caption", "")
        character = publication_context.get("character", "")
        comment_lower = comment.lower()
        
        # 1. direct_meme_reference
        if meme_text:
            for w in sig_words(meme_text):
                if w in comment_lower:
                    return "direct_meme_reference"
        
        # 2. character_reference
        if character and character.lower() in comment_lower:
            return "character_reference"
        
        # 3. caption_reference (whole word match)
        if caption:
            for w in sig_words(caption):
                if re.search(r"\b" + re.escape(w) + r"\b", comment_lower):
                    return "caption_reference"
        
        # 4. topic_reference (substring match from caption)
        if caption:
            for w in sig_words(caption):
                if w in comment_lower:
                    return "topic_reference"
        
        # 5. personal_identification
        personal_patterns = ["me pasa", "me pasó", "soy yo", "literalmente yo", "ese soy yo", "yo soy", "idéntico", "lo soy"]
        for p in personal_patterns:
            if p in comment_lower:
                return "personal_identification"
        
        # 6. humor_extension
        humor_indicators = ["jaja", "ja ja", "😂", "lol", "risas", "crack", "divertido", "gracioso", "🤣", "jajaja"]
        for h in humor_indicators:
            if h in comment_lower:
                return "humor_extension"
        
        # 7. story_extension
        story_indicators = ["novio", "novia", "historia", "chisme", "cuentame", "algo pasó", "rumor", "se dice"]
        for s in story_indicators:
            if s in comment_lower:
                return "story_extension"
        
        # 8. question_about_content
        question_indicators = ["cómo", "qué", "cuándo", "dónde", "por qué", "cuál", "será", "?"]
        for q in question_indicators:
            if q in comment_lower:
                return "question_about_content"
        
        # 9. commercial_reference
        commercial_indicators = ["compro", "vendo", "precio", "cuánto cuesta", "dónde compro", "link", "promo", "descuento", "oferta", "comprar", "vender"]
        for c in commercial_indicators:
            if c in comment_lower:
                return "commercial_reference"
        
        # 10. unrelated vs unclear
        comment_sig = sig_words(comment)
        if comment_sig:
            return "unrelated"
        else:
            return "unclear"
    
    def _decision(
        self,
        comment_type: str,
        relation_to_meme: str,
        intention: str,
        publication_context: Dict[str, Any],
    ) -> str:
        if comment_type == "mention":
            return "no_response"
        if comment_type in ["spam", "troll", "commercial_intent"]:
            return "no_response"
        if comment_type == "question" and relation_to_meme == "question_about_content":
            return "respond"
        if comment_type == "question" and relation_to_meme != "question_about_content":
            return "review"
        if comment_type in ["humor", "identification", "personal_experience", "story_or_gossip", "affection"]:
            return "respond"
        if comment_type == "opinion":
            return "respond"
        if comment_type == "disagreement":
            return "respond"
        if comment_type == "other":
            if relation_to_meme in ["direct_meme_reference", "character_reference", "caption_reference"]:
                return "respond"
            if relation_to_meme in ["topic_reference", "personal_identification", "humor_extension", "story_extension"]:
                return "review"
            if relation_to_meme in ["unrelated", "unclear"]:
                return "no_response"
        return "no_response"
    def _generate_response(
        self,
        publication_context: Dict[str, Any],
        comment: str,
        comment_type: str,
    ) -> str:
        """Generate a short response from the meme/comment relationship.

        The text is intentionally composed from context rather than a single
        catch-all reply. Publication context is treated as untrusted input:
        it is quoted only when a question genuinely needs clarification.
        """
        meme_text = (publication_context.get("meme_text") or "").strip()
        caption = (publication_context.get("caption") or "").strip()
        character = (publication_context.get("character") or "").strip()
        comment_lower = comment.lower()
        cosmic = "El universo" if not character else f"{character}"

        if comment_type == "humor":
            if any(word in comment_lower for word in ("jajaja", "😂", "🤣", "lol")):
                return f"{cosmic} tomó nota de esa risa. 😂"
            return f"Ese remate ya venía con órbita propia. 😂"

        if comment_type == "identification":
            return "Lo sospechábamos, pero gracias por confirmarlo. 😂"

        if comment_type == "personal_experience":
            return "El universo también guarda historias que llegan sin pedir permiso. Gracias por compartirla."

        if comment_type == "story_or_gossip":
            return "Eso no es chisme: es investigación de campo con excelente memoria. 👀"

        if comment_type == "question":
            if character:
                return f"Buena pregunta; {character} probablemente tendría una teoría. 👀"
            if meme_text and len(meme_text) < 120:
                return f"Buena pregunta. El meme dejó esa puerta abierta a propósito. 👀"
            return "Buena pregunta; el universo todavía está tomando notas. 👀"

        if comment_type == "affection":
            if any(word in comment_lower for word in ("amo", "te amo", "te quiero")):
                return "El universo recibe ese cariño y lo guarda en favoritos. 🫶"
            return "Gracias por pasar a dejar un poco de cariño por aquí. ✨"

        if comment_type == "opinion":
            return "Esa lectura también cabe en el universo. 👀"

        if comment_type == "disagreement":
            return "Puede ser; el universo admite más de una teoría. 😌"

        # Only reached for a response-worthy contextual comment.
        if meme_text or caption:
            return "El universo dejó el remate abierto para que ustedes lo terminaran. 😏"
        return "El universo tomó nota. 😏"

    def respond(
        self,
        publication_context: Dict[str, Any],
        comment: str,
    ) -> Dict[str, Any]:
        """
        Main entry point: receives publication context and comment,
        returns a dict matching the CONTRACT_COMMENT_RESPONSES.md.
        """
        comment_type = self._classify_comment(comment)
        intention = self._intention_apparent(comment_type, comment)
        relation = self._relation_to_meme(publication_context, comment)
        decision = self._decision(comment_type, relation, intention, publication_context)
        # NO_TEXT override
        stripped = comment.strip()
        if stripped == "" or stripped.lower() == "(no text)":
            decision = "no_response"

        response_text: Optional[str] = None
        review_reason: Optional[str] = None
        risk_level = "low"

        if decision == "respond":
            response_text = self._generate_response(publication_context, comment, comment_type)
        elif decision == "review":
            review_reason = "Requiere revisión humana debido a ambigüedad o posible riesgo."
            risk_level = "medium"
        elif decision == "react_only":
            # Not implemented in decision logic for now; could be added
            response_text = None
            review_reason = None
            risk_level = "low"
        else:  # no_response
            response_text = None
            review_reason = None
            risk_level = "low"

        result: Dict[str, Any] = {
            "publication_id": publication_context.get("publication_id"),
            "comment": comment,
            "comment_type": comment_type,
            "apparent_intent": intention,
            "relation_to_meme": relation,
            "decision": decision,
            "response": response_text,
            "risk_level": risk_level,
        }
        if review_reason is not None:
            result["review_reason"] = review_reason
        return result


# Helper to parse fixture file (for tests)
def parse_publication_contexts_real(md_path: str) -> list[dict]:
    """
    Very permissive parser for the fixture file.
    Returns a list of dicts with keys matching the Publication Context schema.
    Missing keys will be None.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    contexts = []
    current = {}
    current_date = None  # to store date from lines like "dia 5 de Septiembre"
    expected_keys = ["publication_id", "published_at", "asset_ref", "post_url", "character", "visual_context", "meme_text", "caption"]
    for line in lines:
        stripped = line.strip()
        # Detect date lines: e.g., "dia 5 de Septiembre", "6 de septiembre", "7 DE SEPTIEMBRE"
        if stripped.lower().startswith("dia ") or ("de septiembre" in stripped.lower()) or stripped.lower().endswith("de septiembre"):
            # Extract date: we keep the whole line as date for simplicity
            current_date = stripped
            continue
        # Detect start of a new entry: line with "hora:" or "Hora:"
        if stripped.lower().startswith("hora:"):
            # If we have accumulated a context, store it
            if current:
                # If we have a date, add it as published_at (we'll keep raw; could be parsed later)
                if current_date:
                    current.setdefault("published_at", current_date)
                # Ensure all expected keys are present
                for key in expected_keys:
                    current.setdefault(key, None)
                contexts.append(current)
                # Start a new context
                current = {}
                # reset date? keep same date for subsequent entries same day
            # Parse time from hora line
            # format: "hora: 13:50" or "hora:19:13"
            time_part = stripped.split(":", 1)[1].strip()
            current["_hora"] = time_part
            # We'll combine with date later if needed
        # Parse known fields
        if stripped.lower().startswith("asset:"):
            current["asset_ref"] = stripped.split(":", 1)[1].strip()
        elif stripped.lower().startswith("posturl:") or stripped.lower().startswith("posurl:"):
            url = stripped.split(":", 1)[1].strip()
            # Strip markdown link if present
            if url.startswith("["):
                # format [text](url)
                match = re.search(r"\]\((http[^)]+)\)", url)
                if match:
                    url = match.group(1)
            current["post_url"] = url
            # Extract fbid and set publication_id
            match = re.search(r'fbid=(\d+)', url)
            if match:
                current["publication_id"] = match.group(1)
            else:
                match = re.search(r'/reel/(\d+)', url)
                if match:
                    current["publication_id"] = match.group(1)
        elif stripped.lower().startswith("meme:"):
            meme = stripped.split(":", 1)[1].strip()
            # Remove surrounding quotes if present
            if meme.startswith('"') and meme.endswith('"'):
                meme = meme[1:-1]
            current["meme_text"] = meme
        elif stripped.lower().startswith("caption:"):
            caption = stripped.split(":", 1)[1].strip()
            # Remove escape backslashes before #
            caption = caption.replace("\\#", "#")
            current["caption"] = caption
        # character and visual_context are not directly in fixture; leave as None
    if current:
        # Add date if we have one
        if current_date:
            current.setdefault("published_at", current_date)
        # Ensure all expected keys are present
        for key in expected_keys:
            current.setdefault(key, None)
        contexts.append(current)
    # Post-process: fill missing keys with None (already done, but ensure)
    for c in contexts:
        for key in expected_keys:
            c.setdefault(key, None)
    return contexts
