# CLAUDE.md

## Core Rules

- Never invent information, methods, or libraries. If unsure how to solve a task — say so and ask clarifying questions.
- If user request lacks details — ask clarifying questions before generating anything.
- Use simple English. Be brief and emotionless.

## Documentation vs Code

- Separate documentation work from code generation.
- If user asks for documentation — do not generate code. Provide only descriptions of code blocks to be implemented later.

## Code Generation

- Generate minimum code required to solve the task.
- Avoid decorative logs, colored terminal output, fancy formatting, excessive diagrams.
- Avoid comments in functions and classes.

## Context Window

- Before solving a task, estimate if it fits the context window.
- If task may consume >75% of context — warn user and suggest splitting into smaller chunks.

## MCP Servers

- Prefer using available MCP servers for analysis and task solving.
- If user requires MCP servers — always use them.
- See `agent_docs/mcp_usage.md` for details.

## Additional Instructions

Select appropriate instruction file from `agent_docs/` based on task type:

```
agent_docs/
├── tech_project_description.md
├── mcp_usage.md
├── python_code_generation.md
├── python_code_testing.md
├── infrastructure_code_generation.md
└── vector_databases.md
```

| File | When to use |
|------|-------------|
| `tech_project_description.md` | Read on every response to understand project context |
| `mcp_usage.md` | List of available MCP servers and when to use them |
| `python_code_generation.md` | Rules for Python code generation tasks |
| `python_code_testing.md` | Rules for Python testing tasks (pytest, coverage, test requirements) |
| `infrastructure_code_generation.md` | Rules for Docker files and service deployment |
| `vector_databases.md` | Rules for vector DB code generation and queries |


