from datetime import datetime, timedelta, timezone


def should_run_autonomous_check(session_state):
    last_run = session_state.get("last_autonomous_run")

    if last_run is None:
        return True

    elapsed = datetime.now(timezone.utc) - last_run

    return elapsed >= timedelta(minutes=5)


def mark_autonomous_run(session_state):
    session_state["last_autonomous_run"] = datetime.now(timezone.utc)
