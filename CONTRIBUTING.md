# 🤝 Contributing to Terra Scout

Thank you for your interest in contributing to Terra Scout!

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/TerraScout.git
   ```
3. Set up development environment (see [SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md))
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🔄 Development Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Create    │────>│   Develop   │────>│    Test     │
│   Branch    │     │   Feature   │     │   Changes   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│   Merged!   │<────│   Review    │<────│   Create    │
│             │     │   Process   │     │     PR      │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 📝 Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters (Black default)
- Use docstrings for all public functions

### Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type check
mypy .
```

### Example Code

```python
def calculate_reward(
    observation: dict,
    action: dict,
    next_observation: dict,
    info: dict
) -> float:
    """
    Calculate the reward for a state transition.

    Args:
        observation: Current state observation
        action: Action taken
        next_observation: Resulting state observation
        info: Additional environment info

    Returns:
        Calculated reward value
    """
    reward = 0.0

    # Diamond found
    if info.get("diamond_found", False):
        reward += 1000.0

    return reward
```

---

## 💬 Commit Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type       | Description                |
| ---------- | -------------------------- |
| `feat`     | New feature                |
| `fix`      | Bug fix                    |
| `docs`     | Documentation only         |
| `style`    | Formatting, no code change |
| `refactor` | Code restructuring         |
| `test`     | Adding tests               |
| `chore`    | Maintenance tasks          |

### Examples

```bash
feat(agent): add curiosity-based exploration bonus

fix(env): resolve memory leak in observation wrapper

docs(readme): update installation instructions

test(reward): add unit tests for reward calculation
```

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

Describe testing done.

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
```

---

## 📁 Project Structure Reference

```
Terra-Scout/
├── agent/          # Agent code - core logic
├── training/       # Training scripts
├── docs/           # Documentation
├── shared/         # Shared utilities
└── scripts/        # Development scripts
```

---

## ❓ Questions?

Open an issue with the `question` label.

---

Thank you for contributing! 🎉
