# Contributing to Text2File

Thank you for considering contributing to Text2File! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment:
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install dependencies
   poetry install --with dev
   
   # Set up pre-commit hooks
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with a descriptive message
3. Run tests and checks:
   ```bash
   # Run tests
   poetry run pytest
   
   # Run linter
   poetry run ruff check .
   
   # Run type checker
   poetry run mypy .
   ```

4. Push your changes to your fork and open a pull request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep lines under 88 characters (Black will handle this)
- Run `black .` and `ruff --fix .` before committing

## Testing

- Write tests for all new functionality
- Run tests with `pytest`
- Aim for at least 80% test coverage
- Update documentation when adding new features

## Pull Request Guidelines

- Keep PRs focused on a single feature or bugfix
- Update the documentation and tests as needed
- Reference any related issues in your PR description
- Ensure all tests pass before submitting for review

## Reporting Issues

When reporting issues, please include:
- A clear description of the issue
- Steps to reproduce the issue
- Expected vs. actual behavior
- Version information (Python version, package version, etc.)

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
