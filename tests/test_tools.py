import importlib

import pytest


@pytest.fixture()
def tools(tmp_path, monkeypatch):
    monkeypatch.setenv("WHISPERER_DATA_FILE", str(tmp_path / "mistakes.json"))
    import whisperer.tools as t
    return importlib.reload(t)


def test_first_mistake_is_new(tools):
    msg = tools.log_mistake(topic="RAG vs fine-tuning", trap="picked fine-tuning", domain="FM apps")
    assert "First time" in msg


def test_repeated_trap_is_detected_case_insensitive(tools):
    tools.log_mistake(topic="RAG vs fine-tuning", trap="a")
    msg = tools.log_mistake(topic="  rag VS Fine-Tuning ", trap="b")
    assert "1 time(s) before" in msg


def test_weak_spots_ranking(tools):
    for _ in range(3):
        tools.log_mistake(topic="Precision vs recall", trap="x")
    tools.log_mistake(topic="Temperature", trap="y")
    report = tools.weak_spots_report()
    assert report.index("Precision vs recall") < report.index("Temperature")
    assert "4 logged" in report


def test_corrupted_file_does_not_break(tools):
    tools.DATA_FILE.write_text("{not json", encoding="utf-8")
    assert "First time" in tools.log_mistake(topic="Tokens", trap="z")


def test_empty_report(tools):
    assert "No traps logged yet" in tools.weak_spots_report()
