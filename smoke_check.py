import subprocess
import sys


COMMANDS = [
    ("Compile app", [sys.executable, "-m", "py_compile", "app.py"]),
    ("Acceptance checks", [sys.executable, "acceptance_checks.py"]),
    ("Auth flow static regression", [sys.executable, "test_auth_flow_static.py"]),
    ("Routing tests", [sys.executable, "test_routing.py"]),
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