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
