# AI Coding Agent (Python + Gemini)

A command-line AI agent that takes a natural-language prompt and autonomously reads, writes, and
runs Python files in a sandboxed working directory to accomplish the task — powered by Google's
Gemini API and function calling.

> This is my implementation of the **boot.dev** guided project ["Build an AI Agent in Python"](https://www.boot.dev/).
> The core architecture (agent loop, tool schemas, sandboxing pattern) follows the course curriculum;
> I wrote the code, tests, and this documentation myself.

## What it does

You give the agent a plain-English instruction, e.g. "the calculator app doesn't handle nested
parentheses, fix it." The agent then:

1. Sends your prompt to Gemini along with a system prompt and four tool schemas.
2. Gemini decides which function(s) to call (list files, read a file, write a file, run a file).
3. The agent executes the requested function against a sandboxed working directory
   (`./calculator` in this repo) and feeds the result back to Gemini.
4. This repeats for up to **20 iterations**, until Gemini responds with a final answer instead of
   another function call, or the loop is exhausted.

The target codebase the agent operates on is `calculator/` — a small CLI calculator app (its own
`main.py`, an expression evaluator in `pkg/calculator.py`, and JSON output formatting in
`pkg/render.py`) that ships in this repo purely so the agent has something real to inspect, edit,
and execute.

## Setup

Requires **Python 3.12+**.

Install dependencies with [uv](https://docs.astral.sh/uv/) (recommended, matches `uv.lock`):

```bash
uv sync
```

Or with plain pip:

```bash
pip install google-genai==1.12.1 python-dotenv==1.1.0
```

You need a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). Create a
`.env` file in the repo root (it's git-ignored, never commit it):

```
GEMINI_API_KEY=your-key-here
```

## Usage

```bash
uv run main.py "your prompt here"
uv run main.py "your prompt here" --verbose
```

`--verbose` prints each function call with its full arguments, plus prompt/response token counts
for every round-trip to Gemini. Without it, you just see a one-line `- Calling function: ...` per
tool call and the final answer.

**Example 1 — read and explain** (no files modified):

```bash
uv run main.py "what does the calculator app do and how is it structured?"
```

The agent lists `calculator/`, reads `main.py` and `pkg/calculator.py`, then summarizes in plain
English.

**Example 2 — fix and verify:**

```bash
uv run main.py "the calculator's tests are failing, find out why and fix it" --verbose
```

```
 - Calling function: get_files_info
 - Calling function: get_file_content
 - Calling function: run_python_file
 - Calling function: write_file
 - Calling function: run_python_file
Final response:
The bug was in Calculator.evaluate — operator precedence wasn't applied ...
```

`--verbose` additionally interleaves raw `function_call.args`, each tool's return payload, and
token usage between steps.

## How it works

- **`main.py`** — the agent loop. Sends the running `messages` history to
  `client.models.generate_content`, checks `result.function_calls`, dispatches each one through
  `call_function`, appends both the model's turn and the tool results back into `messages`, and
  repeats (max 20 iterations, matching the "20 turns" cap common in the boot.dev course).
- **`prompts.py`** — the `system_prompt` string that tells Gemini what it's allowed to do and that
  all paths are relative to an (implicit, auto-injected) working directory.
- **`functions/call_function.py`** — maps a Gemini `FunctionCall` by name to the real Python
  function, injects `working_directory="./calculator"` into every call (the model never gets to
  choose the working directory itself), and wraps the result back into a `types.Content`/
  `types.Part.from_function_response` for the next Gemini turn.
- **The four tools**, each a plain Python function plus a matching `types.FunctionDeclaration`
  schema (so Gemini knows its name, description, and JSON-schema parameters):
  - `functions/get_files_info.py` — lists a directory's entries with size and `is_dir`.
  - `functions/get_file_content.py` — reads a file, truncated to `MAX_CHARS` (10,000, see
    `config.py`).
  - `functions/write_file.py` — creates/overwrites a file (creating parent directories as needed).
  - `functions/run_python_file.py` — runs a `.py` file with `subprocess.run`, `cwd` pinned to the
    working directory, 30-second timeout, captures stdout/stderr.
  - `available_functions = types.Tool(function_declarations=[...])` in `call_function.py` bundles
    all four schemas and is passed to Gemini via `GenerateContentConfig(tools=[...])`.

## Security note

This is an educational project. The agent can write files and execute arbitrary Python inside its
working directory — **do not point it at a repository or machine you care about.**

To be accurate about what the sandboxing actually does: each tool resolves the target path with
`os.path.abspath` / `os.path.normpath` and rejects it (returns an error string, doesn't raise) if
`os.path.commonpath([working_directory, target_path]) != working_directory` — this blocks path
traversal like `../../etc/passwd` or absolute paths outside the working directory. That's the whole
mechanism. There is no OS-level sandbox, container, or user isolation: `run_python_file` runs real
Python via `subprocess.run` with the *user's own permissions*, just with `cwd` set to `calculator/`.
Once a script is executing inside the working directory it can still hit the network, import
anything, or do whatever ordinary Python can do. Treat the check as guarding against naive path
escapes, not as a security boundary against a malicious or buggy prompt.

## What I learned / concepts practiced

- Wiring up LLM **function calling** end-to-end: declaring JSON-schema tool definitions
  (`types.FunctionDeclaration`), passing them to a model, and dispatching the model's chosen calls
  back into real code.
- Building an **agentic loop**: maintaining conversation state (`types.Content` history) across
  multiple model round-trips until a termination condition (no more function calls, or an
  iteration cap) is met.
- Designing a small **tool dispatch layer** (`call_function.py`) that's easy to extend with new
  functions without touching the agent loop itself.
- **Path sandboxing** with `os.path.commonpath` and thinking carefully about the difference between
  "prevents naive path traversal" and "provides a real security boundary."
- Practical use of the **Google GenAI Python SDK** (`google-genai`): `Client`, `GenerateContentConfig`,
  `system_instruction`, reading `usage_metadata`, and building `Part.from_function_response` replies.

## Note on the root-level `test_*.py` files

`test_get_files_info.py`, `test_get_file_content.py`, `test_write_file.py`, and
`test_run_python_file.py` are manual verification scripts from the boot.dev course: plain
`print()`-driven scripts you run directly (`uv run test_get_files_info.py`) and eyeball against the
expected output in the comments — not a `pytest`/`unittest` suite with assertions. Kept as-is
(that's how the course structures them); don't expect `pytest` semantics from them.
