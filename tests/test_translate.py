# tests/test_translate.py
from src.api.translate import translate_text, is_chinese


class FakeLLM:
    def __init__(self, output):
        self.output = output

    def invoke(self, messages):
        class R:
            content = self.output
        return R()


def test_is_chinese():
    assert is_chinese("你好") is True
    assert is_chinese("hello") is False
    assert is_chinese("工程师 engineer") is True


def test_translate_text(monkeypatch):
    """
    Mock the translator LLM so no real API call happens.
    """
    from src.api import translate as translate_module

    fake = FakeLLM("翻译后的文字")
    monkeypatch.setattr(translate_module, "translator_llm", fake)

    result = translate_text("hello world", "Chinese")
    assert result == "翻译后的文字"
