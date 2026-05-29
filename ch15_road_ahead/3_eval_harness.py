"""
Eval harness: test Claude systematically before upgrading models.
Three match types: exact, contains, llm_judge.
Run before and after any model change to catch regressions.
"""
import json
import time
import statistics
from dataclasses import dataclass
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()


@dataclass
class EvalCase:
    id: str
    prompt: str
    expected: str
    match_type: str = "contains"  # "exact" | "contains" | "llm_judge"
    system: str = ""


@dataclass
class EvalResult:
    case_id: str
    passed: bool
    actual: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    judge_reasoning: str = ""


def run_case(case: EvalCase, model: str) -> EvalResult:
    start = time.perf_counter()
    kwargs = {
        "model": model,
        "max_tokens": 512,
        "messages": [{"role": "user", "content": case.prompt}]
    }
    if case.system:
        kwargs["system"] = case.system
    resp = client.messages.create(**kwargs)
    elapsed = (time.perf_counter() - start) * 1000
    actual = resp.content[0].text.strip()

    if case.match_type == "exact":
        passed = actual.lower() == case.expected.lower()
        reasoning = ""
    elif case.match_type == "contains":
        passed = case.expected.lower() in actual.lower()
        reasoning = ""
    else:  # llm_judge
        judge = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system="You are an evaluator. Reply with PASS or FAIL followed by one sentence reason.",
            messages=[{"role": "user", "content":
                f"Task: {case.prompt}\nExpected theme: {case.expected}\n"
                f"Actual response: {actual}\nDoes the response satisfy the expected theme?"}]
        )
        j = judge.content[0].text
        passed = j.upper().startswith("PASS")
        reasoning = j

    return EvalResult(
        case_id=case.id,
        passed=passed,
        actual=actual,
        latency_ms=round(elapsed, 1),
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        judge_reasoning=reasoning
    )


def run_eval(model: str, cases: list[EvalCase]) -> dict:
    results = [run_case(c, model) for c in cases]
    passed = sum(r.passed for r in results)
    latencies = [r.latency_ms for r in results]
    return {
        "model": model,
        "pass_rate": passed / len(results),
        "passed": passed,
        "total": len(results),
        "avg_latency_ms": round(statistics.mean(latencies), 1),
        "p95_latency_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 1),
        "total_input_tokens": sum(r.input_tokens for r in results),
        "total_output_tokens": sum(r.output_tokens for r in results),
        "failures": [r for r in results if not r.passed]
    }


def compare_models(cases: list[EvalCase], *models: str):
    print(f"Running eval on {len(cases)} cases across {len(models)} models...\n")
    for model in models:
        result = run_eval(model, cases)
        cost = (result["total_input_tokens"] * 3 + result["total_output_tokens"] * 15) / 1_000_000
        print(f"Model: {model}")
        print(f"  Pass rate:     {result['pass_rate']:.1%} ({result['passed']}/{result['total']})")
        print(f"  Avg latency:   {result['avg_latency_ms']}ms  |  p95: {result['p95_latency_ms']}ms")
        print(f"  Est. cost:     ${cost:.4f}")
        if result["failures"]:
            print("  Failures:")
            for f in result["failures"][:3]:
                print(f"    [{f.case_id}] Got: {f.actual[:80]}...")
        print()


if __name__ == "__main__":
    import os
    cases_path = os.path.join(os.path.dirname(__file__), "..", "evals", "support_triage.json")
    raw = json.load(open(cases_path))
    cases = [
        EvalCase(
            id=f"case_{i}",
            prompt=c["prompt"],
            expected=c["expected"],
            match_type="contains",
            system="Classify this support ticket as: billing, technical, feature, or general. Reply with one word only."
        )
        for i, c in enumerate(raw)
    ]
    compare_models(cases, "claude-haiku-4-5-20251001", "claude-sonnet-4-6")
