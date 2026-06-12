import subprocess
import sys


COMMANDS = [
    ("Compile app", [sys.executable, "-m", "py_compile", "app.py"]),
    ("Acceptance checks", [sys.executable, "acceptance_checks.py"]),
    ("Auth flow static regression", [sys.executable, "test_auth_flow_static.py"]),
    ("Routing tests", [sys.executable, "test_routing.py"]),
    ("Memory pipeline tests", [sys.executable, "test_memory_pipeline.py"]),
    ("Memory quality tests", [sys.executable, "test_memory_quality.py"]),
    ("Memory direct answer tests", [sys.executable, "test_memory_direct_answer.py"]),
    ("Supabase SQL schema tests", [sys.executable, "test_supabase_sql_schema.py"]),
    ("Supabase memory V2 tests", [sys.executable, "test_supabase_memory_v2.py"]),
    ("Event logger tests", [sys.executable, "test_event_logger.py"]),
    ("Final acceptance tests", [sys.executable, "test_final_acceptance.py"]),
    ("Runtime fallback tests", [sys.executable, "test_runtime_fallback.py"]),
    ("Agent tool safety tests", [sys.executable, "test_agent_tools.py"]),
    ("Planner tool compatibility tests", [sys.executable, "test_planner_tools.py"]),
    ("Planner guard tests", [sys.executable, "test_planner_guard.py"]),
]


def run_check(name: str, command: list[str]) -> bool:
    print(f"\n=== {name} ===")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"FAILED: {name}")
        return False

    print(f"PASSED: {name}")
    return True


def main() -> int:
    all_passed = True

    for name, command in COMMANDS:
        passed = run_check(name, command)
        all_passed = all_passed and passed

    print("\n=== SUMMARY ===")
    if all_passed:
        print("SMOKE CHECK PASSED")
        return 0

    print("SMOKE CHECK FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())