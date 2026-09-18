import json
from pathlib import Path

from src.facebook_comments.responders.universe_responder import UniverseResponder


FIXTURE = Path(__file__).parent / "fixtures" / "comment_classification_cases.json"


def test_classification_fixture_cases():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    responder = UniverseResponder()

    for case in data["cases"]:
        result = responder.respond(data["context"], case["comment"])
        for key, expected in case["expected"].items():
            assert result[key] == expected, (case["comment"], key, result[key], expected)
