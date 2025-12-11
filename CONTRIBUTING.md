# Contributing to Context Horizons

## Code Style

We follow PEP 8 with these modifications:
- Maximum line length: 120 characters
- Use 4 spaces for indentation
- Use snake_case for functions and variables
- Use PascalCase for classes

## Adding New Experiments

1. Create `expN_name.py` file
2. Implement experiment class with `__init__()` and `run()` methods
3. Follow existing pattern from exp1-4
4. Add experiment to main.py orchestrator
5. Add visualization function to analyze_results.py
6. Update README.md with experiment description

## Adding New Models

1. Add model identifier to `config.MODELS` list
2. Ensure model is available in Ollama: `ollama list`
3. Run benchmark: `python main.py --models "your-model:tag"`

## Testing Requirements

- All new utilities must have unit tests
- Aim for >70% code coverage
- Run tests before submitting: `pytest tests/`
- Check coverage: `pytest --cov=. --cov-report=html`
- CI/CD pipeline runs on every push and PR to ensure quality

## Pre-commit Hooks

We use pre-commit to ensure code quality.

1. Install pre-commit: `pip install pre-commit`
2. Install hooks: `pre-commit install`
3. Run hooks manually: `pre-commit run --all-files`

Hooks include: black, isort, flake8, mypy, and bandit.

## Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run linting: `pylint *.py`
5. Run tests: `pytest tests/`
6. Commit with clear message: `git commit -m "Add amazing feature"`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open Pull Request with description
