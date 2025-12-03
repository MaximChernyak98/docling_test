# Python Code Generation Rules

## Package Management

- ONLY use pip

## Code Quality

- Type hints required for all code
- Functions must be focused and small
- Follow existing patterns exactly
- Line length: 120 chars maximum

## Code Style

- PEP 8 naming (snake_case for functions/variables)
- Class names in PascalCase
- Constants in UPPER_SNAKE_CASE
- Use f-strings for formatting

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively**: Start with minimal functionality and verify it works before adding complexity
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organisation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

## General Best Practic

- Keep changes minimal
- Follow existing patterns
- Document public APIs
- Use docstrings only in the very complex functions. Use comments only in the non-obvious parts. Do not use comments without necessity
