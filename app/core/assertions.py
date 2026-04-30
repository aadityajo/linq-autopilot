from dataclasses import dataclass
from app.models.scenario import AssertionConfig, AssertionType
from app.core.judge import judge_intent


@dataclass
class AssertionContext:
    response_text: str | None
    latency_ms: int | None
    reaction_type: str | None = None


@dataclass
class AssertionResult:
    passed: bool
    reason: str | None = None


async def run_assertion(
    assertion: AssertionConfig, context: AssertionContext
) -> AssertionResult:
    if assertion.type == AssertionType.react:
        if not context.reaction_type:
            return AssertionResult(
                passed=False, reason="No reaction received (reaction_type was None)"
            )

        expected = []
        if assertion.values:
            expected.extend([str(v).lower() for v in assertion.values])
        if assertion.value:
            expected.append(str(assertion.value).lower())

        passed = context.reaction_type.lower() in expected
        return AssertionResult(
            passed=passed,
            reason=f"Received reaction '{context.reaction_type}'"
            if passed
            else f"Expected reaction in {expected}, got '{context.reaction_type}'",
        )
    if assertion.type == AssertionType.latency_under_ms:
        if context.latency_ms is None:
            return AssertionResult(passed=False, reason="Latency is None")
        passed = context.latency_ms < int(assertion.value)
        return AssertionResult(
            passed=passed,
            reason=f"Latency {context.latency_ms}ms"
            if passed
            else f"Latency {context.latency_ms}ms exceeded {assertion.value}ms",
        )

    if context.response_text is None:
        return AssertionResult(passed=False, reason="No response received or timed out")

    response = context.response_text

    if assertion.type == AssertionType.contains_any:
        passed = any(v.lower() in response.lower() for v in assertion.values)
        return AssertionResult(
            passed=passed,
            reason=f"Found one of {assertion.values}"
            if passed
            else f"Missing any of {assertion.values}",
        )
    elif assertion.type == AssertionType.contains_all:
        passed = all(v.lower() in response.lower() for v in assertion.values)
        return AssertionResult(
            passed=passed,
            reason=f"Found all of {assertion.values}"
            if passed
            else f"Missing some of {assertion.values}",
        )
    elif assertion.type == AssertionType.forbidden:
        passed = all(v.lower() not in response.lower() for v in assertion.values)
        return AssertionResult(
            passed=passed,
            reason=f"Found none of {assertion.values}"
            if passed
            else f"Found some of {assertion.values}",
        )
    elif assertion.type == AssertionType.intent:
        judgment = await judge_intent(response, str(assertion.value))
        return AssertionResult(passed=judgment.passed, reason=judgment.reason)

    return AssertionResult(
        passed=False, reason=f"Unknown assertion type: {assertion.type}"
    )
