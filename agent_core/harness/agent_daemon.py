"""Autonomous Background Agent Daemon.

A lightweight, production-ready execution loop designed to run in the background,
execute multi-step tasks, invoke tools, persist state, and operate cleanly
either as a background service or compiled into a standalone Windows .exe.
"""

import os
import sys
import time
import json
import logging
import threading
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

# Relative import of the free provider router
try:
    from ..providers.free_providers import FreeAIProviderRouter
except (ImportError, ValueError):
    from agent_core.providers.free_providers import FreeAIProviderRouter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("AutonomousAgentDaemon")


class BackgroundAgent:
    """Autonomous agent engine with persistent memory and tool execution."""

    def __init__(
        self,
        name: str = "TitusBackgroundAgent",
        state_file: str = "agent_state.json",
        max_iterations: int = 15,
    ):
        self.name = name
        self.state_file = state_file
        self.max_iterations = max_iterations
        self.router = FreeAIProviderRouter()
        self.tools: Dict[str, Callable[[str], str]] = {}
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

        # Register standard default tools
        self._register_default_tools()
        self.state = self._load_state()

    def register_tool(self, name: str, func: Callable[[str], str]):
        """Register an executable capability for the agent."""
        self.tools[name] = func

    def _register_default_tools(self):
        """Standard filesystem and execution tools."""
        def read_file(path: str) -> str:
            try:
                with open(path.strip(), "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(4000)
            except Exception as e:
                return f"Error reading file: {e}"

        def write_file(param_str: str) -> str:
            try:
                # Expecting path:::content
                parts = param_str.split(":::", 1)
                if len(parts) < 2:
                    return "Error: write_file requires 'filepath:::content'"
                path, content = parts[0].strip(), parts[1]
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote {len(content)} characters to {path}"
            except Exception as e:
                return f"Error writing file: {e}"

        def execute_cmd(cmd: str) -> str:
            import subprocess
            try:
                res = subprocess.run(cmd.strip(), shell=True, capture_output=True, text=True, timeout=30)
                output = res.stdout or res.stderr
                return output[:2000] if output else "Command completed with no output."
            except Exception as e:
                return f"Command execution error: {e}"

        self.register_tool("read_file", read_file)
        self.register_tool("write_file", write_file)
        self.register_tool("execute_cmd", execute_cmd)

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"history": [], "tasks_completed": 0, "created_at": str(datetime.now())}

    def _save_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist state: {e}")

    def run_goal(self, goal: str) -> str:
        """Run an autonomous multi-step loop to accomplish a goal."""
        logger.info(f"Starting goal execution: {goal}")
        tool_descriptions = "\n".join([f"- {t}" for t in self.tools.keys()])

        system_prompt = (
            f"You are {self.name}, an autonomous agent. Complete the user goal.\n"
            f"Available tools:\n{tool_descriptions}\n\n"
            "To use a tool, respond ONLY with a JSON object: {\"action\": \"tool_name\", \"input\": \"parameters\"}\n"
            "When the goal is fully accomplished, respond with: {\"action\": \"finish\", \"output\": \"summary\"}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Goal: {goal}"},
        ]

        for step in range(self.max_iterations):
            logger.info(f"Step {step + 1}/{self.max_iterations} querying model...")
            resp = self.router.chat_complete(messages)

            if not resp.get("success"):
                logger.error(f"Model dispatch failed: {resp.get('message')}")
                return f"Failure: Unable to reach any free token provider. Errors: {resp.get('errors')}"

            reply = resp["content"].strip()
            logger.info(f"Agent thought: {reply[:120]}...")

            # Parse tool call or finish
            try:
                # Find JSON block in reply
                start = reply.find("{")
                end = reply.rfind("}") + 1
                if start != -1 and end != 0:
                    action_data = json.loads(reply[start:end])
                else:
                    action_data = {"action": "finish", "output": reply}
            except Exception:
                action_data = {"action": "finish", "output": reply}

            action = action_data.get("action", "finish")
            if action == "finish":
                final_out = action_data.get("output", reply)
                self.state["tasks_completed"] += 1
                self.state["history"].append({"goal": goal, "result": final_out, "date": str(datetime.now())})
                self._save_state()
                return final_out

            tool_name = action
            tool_input = action_data.get("input", "")
            if tool_name in self.tools:
                logger.info(f"Executing tool '{tool_name}' with input: {str(tool_input)[:80]}")
                tool_output = self.tools[tool_name](str(tool_input))
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"Tool output: {tool_output}"})
            else:
                messages.append({"role": "user", "content": f"Tool '{tool_name}' does not exist. Available: {list(self.tools.keys())}"})

        return "Loop terminated: Max iterations reached before goal completion."

    def start_background_daemon(self, goal_queue: List[str], interval_seconds: int = 60):
        """Run continuously in a background daemon thread."""
        def daemon_loop():
            self.is_running = True
            logger.info("Background daemon started.")
            while self.is_running:
                if goal_queue:
                    goal = goal_queue.pop(0)
                    self.run_goal(goal)
                time.sleep(interval_seconds)

        self._thread = threading.Thread(target=daemon_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2)
