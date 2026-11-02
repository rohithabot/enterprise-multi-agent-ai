import json
import time
from pathlib import Path
from urllib import request, error

API_URL = "http://127.0.0.1:8002/chat"

TEST_CASES = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected_agent": "hr",
        "expected_keywords": ["20", "days"],
    },
    {
        "question": "Which department does Rahul Sharma work in?",
        "expected_agent": "employee",
        "expected_keywords": ["engineering"],
    },
    {
        "question": "What is the company's annual leave policy?",
        "expected_agent": "hr",
        "expected_keywords": ["20"],
    },
]


def ask_api(question):
    payload = json.dumps({"question": question}).encode("utf-8")

    req = request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def run_evaluation():
    results = []

    print("\nStarting Multi-Agent Evaluation...\n")

    for index, test in enumerate(TEST_CASES, start=1):
        start = time.perf_counter()

        try:
            response = ask_api(test["question"])

            elapsed = round(time.perf_counter() - start, 2)

            agent = response.get("agent", "")
            answer = str(response.get("answer", ""))

            routing_passed = agent == test["expected_agent"]

            answer_passed = all(
                keyword.lower() in answer.lower()
                for keyword in test["expected_keywords"]
            )

            passed = routing_passed and answer_passed

            result = {
                "question": test["question"],
                "expected_agent": test["expected_agent"],
                "actual_agent": agent,
                "answer": answer,
                "routing_passed": routing_passed,
                "answer_passed": answer_passed,
                "passed": passed,
                "response_time_seconds": elapsed,
            }

            print(
                f"Test {index}: {'PASS' if passed else 'FAIL'} "
                f"| Agent: {agent} | Time: {elapsed}s"
            )

        except (error.URLError, TimeoutError, ValueError) as exc:
            result = {
                "question": test["question"],
                "passed": False,
                "error": str(exc),
            }

            print(f"Test {index}: ERROR - {exc}")

        results.append(result)

    passed_count = sum(item["passed"] for item in results)
    total = len(results)

    report = {
        "total_tests": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": round(passed_count / total * 100, 2),
        "results": results,
    }

    output_file = (
        Path(__file__).resolve().parent / "evaluation_results.json"
    )

    output_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total - passed_count}")
    print(f"Pass Rate: {report['pass_rate']}%")
    print(f"Report: {output_file}")


if __name__ == "__main__":
    run_evaluation()