"""Sample Deployable Background Agent.

Can be run directly via Python or compiled into a standalone Windows .exe
using agent_core/packaging/build_agent_exe.py.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent_core.harness.agent_daemon import BackgroundAgent


def main():
    print("=" * 60)
    print("  Titus Autonomous Background Agent Engine")
    print("  Powered by Multi-Provider Free Token Routing")
    print("=" * 60)

    agent = BackgroundAgent(
        name="OmniBackgroundWorker",
        state_file="omni_agent_state.json",
        max_iterations=10,
    )

    # Example goal: autonomous file inspection or periodic maintenance
    default_goal = "Inspect the current folder, count python files, and record a summary log."
    goal = sys.argv[1] if len(sys.argv) > 1 else default_goal

    print(f"\n[+] Executing Autonomous Goal: {goal}\n")
    result = agent.run_goal(goal)
    print("\n[+] Agent Execution Result:")
    print(result)


if __name__ == "__main__":
    main()
