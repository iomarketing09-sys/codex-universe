from src.facebook_comments.responders.universe_responder import UniverseResponder


CONTEXT = {
    "publication_id": "test-post",
    "meme_text": "Una verdad incómoda sobre relaciones",
    "caption": "😏 #UniverseSentMe",
    "character": "",
    "visual_context": "",
}


def test_humor_response_uses_contextual_remate():
    result = UniverseResponder().respond(CONTEXT, "Jajaja, me representa")
    assert result["decision"] == "respond"
    assert result["response"] == "El universo tomó nota de esa risa. 😂"


def test_question_response_does_not_repeat_meme_as_explanation():
    result = UniverseResponder().respond(CONTEXT, "¿Y eso cómo funciona?")
    assert result["decision"] == "respond"
    assert "Una verdad incómoda" not in result["response"]
    assert "universo" in result["response"] or "meme" in result["response"]


def test_unrelated_comment_is_not_forced_into_reply():
    result = UniverseResponder().respond(CONTEXT, "El martes llueve")
    assert result["decision"] == "no_response"
    assert result["response"] is None
