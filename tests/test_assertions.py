"""Unit tests for the assertion engine.

These tests cover the deterministic assertion types (contains_any, contains_all,
forbidden, react, latency_under_ms). The `intent` assertion is excluded because
it requires a live LLM call and is tested via integration scenarios instead.
"""

import pytest
from app.core.assertions import run_assertion, AssertionContext, AssertionResult
from app.models.scenario import AssertionConfig, AssertionType


# ---------------------------------------------------------------------------
# contains_any
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_contains_any_passes_when_one_value_present():
    assertion = AssertionConfig(type=AssertionType.contains_any, values=["friday", "7pm"])
    context = AssertionContext(response_text="See you on Friday at 8pm!", latency_ms=200)
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_contains_any_is_case_insensitive():
    assertion = AssertionConfig(type=AssertionType.contains_any, values=["FRIDAY"])
    context = AssertionContext(response_text="Your table is booked for friday.", latency_ms=100)
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_contains_any_fails_when_no_value_present():
    assertion = AssertionConfig(type=AssertionType.contains_any, values=["saturday", "8pm"])
    context = AssertionContext(response_text="See you on Friday at 7pm!", latency_ms=200)
    result = await run_assertion(assertion, context)
    assert result.passed is False


@pytest.mark.asyncio
async def test_contains_any_fails_on_none_response():
    assertion = AssertionConfig(type=AssertionType.contains_any, values=["friday"])
    context = AssertionContext(response_text=None, latency_ms=200)
    result = await run_assertion(assertion, context)
    assert result.passed is False


# ---------------------------------------------------------------------------
# contains_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_contains_all_passes_when_all_values_present():
    assertion = AssertionConfig(type=AssertionType.contains_all, values=["friday", "7pm"])
    context = AssertionContext(response_text="Booked for Friday at 7pm!", latency_ms=100)
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_contains_all_fails_when_one_value_missing():
    assertion = AssertionConfig(type=AssertionType.contains_all, values=["friday", "7pm", "4 people"])
    context = AssertionContext(response_text="Booked for Friday at 7pm!", latency_ms=100)
    result = await run_assertion(assertion, context)
    assert result.passed is False


# ---------------------------------------------------------------------------
# forbidden
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_forbidden_passes_when_no_forbidden_value_present():
    assertion = AssertionConfig(type=AssertionType.forbidden, values=["booked", "confirmed"])
    context = AssertionContext(
        response_text="For parties over 10, please call us directly.", latency_ms=150
    )
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_forbidden_fails_when_forbidden_value_present():
    assertion = AssertionConfig(type=AssertionType.forbidden, values=["booked", "confirmed"])
    context = AssertionContext(
        response_text="Your table is booked for 15 people!", latency_ms=150
    )
    result = await run_assertion(assertion, context)
    assert result.passed is False


# ---------------------------------------------------------------------------
# react
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_react_passes_on_matching_reaction():
    assertion = AssertionConfig(type=AssertionType.react, values=["love", "like"])
    context = AssertionContext(response_text="[love reaction]", latency_ms=50, reaction_type="love")
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_react_fails_on_wrong_reaction():
    assertion = AssertionConfig(type=AssertionType.react, values=["love", "like"])
    context = AssertionContext(response_text="[laugh reaction]", latency_ms=50, reaction_type="laugh")
    result = await run_assertion(assertion, context)
    assert result.passed is False


@pytest.mark.asyncio
async def test_react_fails_when_no_reaction_received():
    assertion = AssertionConfig(type=AssertionType.react, values=["love", "like"])
    context = AssertionContext(response_text="Thanks!", latency_ms=50, reaction_type=None)
    result = await run_assertion(assertion, context)
    assert result.passed is False


# ---------------------------------------------------------------------------
# latency_under_ms
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_latency_passes_when_under_threshold():
    assertion = AssertionConfig(type=AssertionType.latency_under_ms, value=5000)
    context = AssertionContext(response_text="Hi!", latency_ms=2000)
    result = await run_assertion(assertion, context)
    assert result.passed is True


@pytest.mark.asyncio
async def test_latency_fails_when_over_threshold():
    assertion = AssertionConfig(type=AssertionType.latency_under_ms, value=3000)
    context = AssertionContext(response_text="Hi!", latency_ms=5000)
    result = await run_assertion(assertion, context)
    assert result.passed is False


@pytest.mark.asyncio
async def test_latency_fails_when_latency_is_none():
    assertion = AssertionConfig(type=AssertionType.latency_under_ms, value=3000)
    context = AssertionContext(response_text="Hi!", latency_ms=None)
    result = await run_assertion(assertion, context)
    assert result.passed is False
