# Contributing

Thanks for contributing to this project.

This repository is a Python CLI project with spec-driven behavior, local test support, and optional local AWS emulation via MiniStack. Please keep contributions focused, practical, and aligned with the existing patterns in the codebase.

## Before You Start

For small fixes, feel free to open a pull request directly.

For larger changes, please discuss them first by opening an issue. This helps avoid duplicated work and makes sure the proposed direction fits the project.

Examples of changes that should be discussed before implementation:

- new pipeline stages or major flow changes
- substantial CLI behavior changes
- new infrastructure workflows
- changes to spec-driven validation behavior
- broad refactors

## Reporting Bugs

Please open a GitHub issue using the bug report template.

A good bug report should include:

- what you expected to happen
- what actually happened
- clear reproduction steps
- relevant environment details
- logs, tracebacks, or screenshots when helpful
- whether MiniStack / local AWS emulation was involved

If the issue is related to article generation quality, include the input context, focus, and questions used in the CLI when possible.

## Suggesting Features

Please open a GitHub issue using the feature request template.

Good feature requests usually explain:

- the problem being solved
- why the change is useful
- the expected behavior
- whether it affects the CLI, spec, validation rules, or local infrastructure

## Local Setup

1. Clone the repository.
2. Install dependencies:

```bash
uv sync
```

3. Create a local environment file if needed:

```bash
cp .env.example .env
```

On Windows PowerShell, if script activation is restricted, you can run commands with `uv run` directly instead of activating the virtual environment.

## Running the Project

Run the CLI:

```bash
uv run python main.py
```

Optional: if your change involves local AWS emulation, start MiniStack separately:

```bash
docker compose -f docker-compose.ministack.yml up -d
```

## Running Tests

Run the main test suite before opening a pull request:

```bash
uv run pytest -q
```

If you changed lint-relevant code, also run:

```bash
uv run ruff check .
```

## Development Expectations

Please keep changes:

- minimal in scope
- aligned with existing naming and structure
- consistent with the current CLI and spec-driven workflow
- focused on the problem being solved

Do not mix unrelated refactors with a feature or fix unless they are strictly necessary.

If you change behavior that affects the spec, validation flow, prompts, CLI flow, or MiniStack support, update the relevant documentation in the same pull request.

## Branching

Create a focused branch from the current default branch. For example:

```bash
git checkout -b fix/spec-validator-endpoint-url
```

Use branch names that describe the work clearly, such as:

- `fix/...`
- `feat/...`
- `docs/...`
- `test/...`

## Pull Requests

When opening a pull request:

- use a clear title
- describe what changed and why
- keep the pull request focused
- include test notes
- link related issues when applicable

A strong pull request usually includes:

- summary of the change
- motivation or bug being fixed
- testing performed
- any follow-up work that remains

Thank you for helping improve the project.
