from itinerary_engine.edit_parser import rule_based
from itinerary_engine.edit_parser.rule_based import RuleBasedEditParser


def test_parser_reuses_compiled_regexes(monkeypatch) -> None:
    parser = RuleBasedEditParser()
    compile_calls = 0
    original_compile = rule_based.re.compile

    def tracking_compile(*args, **kwargs):
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(*args, **kwargs)

    monkeypatch.setattr(rule_based.re, "compile", tracking_compile)

    assert parser.parse("Replace the museum on day 2 with a food market.").action == "replace"
    assert parser.parse("Move the museum to day 2.").action == "move"
    assert compile_calls == 0


def test_parser_move_with_explicit_source_day() -> None:
    parser = RuleBasedEditParser()

    intent = parser.parse("Move the museum from day 1 to day 2.")

    assert intent.action == "move"
    assert intent.target_text == "museum"
    assert intent.source_day == 1
    assert intent.target_day == 2
