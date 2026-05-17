# Architecture

This project is a modular coding-agent harness for local models served through
vLLM. It is inspired by `rasbt/mini-coding-agent`, but keeps responsibilities in
separate modules.

## Current Modules

- `harness.vllm_client`
  Calls the vLLM OpenAI-compatible chat API.

- `harness.workspace`
  Captures cwd, repo root, git state, recent commits, and short project-doc
  snippets.

- `harness.session`
  Saves, loads, and finds saved session JSON files.

- `harness.parsing`
  Parses JSON tool calls and final answers from model responses.

## Planned Modules

- `harness.tools`
  Implement file, search, shell, and patch tools.

- `harness.agent`
  Run the prompt/model/tool loop.

- `harness.cli`
  Provide CLI and REPL entry points.

## Rule of Thumb

Keep modules small, explicit, and directly testable. Add detail only when it
helps future changes.
