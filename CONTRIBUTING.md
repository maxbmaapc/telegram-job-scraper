# Contributing to Telegram Job Scraper

Thank you for your interest in contributing to the Telegram Job Scraper project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate of others.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- Telegram API credentials

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/telegram-job-scraper.git
   cd telegram-job-scraper
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/maxbmaapc/telegram-job-scraper.git
   ```

## Development Setup

### Local Development

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. Set up pre-commit hooks:

   ```bash
   pre-commit install
   ```

4. Copy and configure environment variables:
   ```bash
   cp config_template.txt .env
   # Edit .env with your Telegram API credentials
   ```

### Docker Development

1. Build the development image:

   ```bash
   docker-compose --profile development build
   ```

2. Start development services:

   ```bash
   docker-compose --profile development up -d
   ```

3. Access the application:
   - Web UI: http://localhost:5000
   - Logs: `docker-compose logs -f telegram-scraper-dev`

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black formatter default)
- Use type hints for all function parameters and return values
- Use f-strings for string formatting
- Use `pathlib` instead of `os.path` for file operations

### Code Formatting

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run formatting:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check types
mypy src/

# Lint code
flake8 src/ tests/
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `TelegramJobClient`)
- **Functions and variables**: snake_case (e.g., `get_messages`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Files**: snake_case (e.g., `telegram_client.py`)

### Documentation

- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include type hints in docstrings
- Document exceptions that may be raised

Example:

```python
def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve messages from configured channels.

    Args:
        limit: Maximum number of messages to retrieve per channel

    Returns:
        List of message dictionaries

    Raises:
        TelegramError: If API request fails
        ValueError: If limit is negative
    """
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_filters.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and failure cases

Example:

```python
def test_salary_extraction_with_range():
    """Test salary extraction with range format."""
    # Arrange
    text = "Salary: $50k-$80k USD"
    extractor = SalaryExtractor()

    # Act
    result = extractor.extract_salaries(text)

    # Assert
    assert len(result) == 1
    assert result[0].is_range is True
    assert result[0].min_amount == Decimal('50000')
    assert result[0].max_amount == Decimal('80000')
```

### Test Coverage

We aim for at least 80% test coverage. Check coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

## Pull Request Process

### Before Submitting

1. Ensure your code follows the coding standards
2. Run all tests and ensure they pass
3. Update documentation if needed
4. Add tests for new functionality
5. Update CHANGELOG.md with your changes

### Creating a Pull Request

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git add .
   git commit -m "feat: add enhanced salary extraction"
   ```

3. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request on GitHub

### Pull Request Guidelines

- Use descriptive titles
- Provide a detailed description of changes
- Reference related issues
- Include screenshots for UI changes
- Ensure CI checks pass

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:

```
feat(filters): add enhanced salary extraction with multiple currencies
fix(telegram): handle connection timeout errors gracefully
docs(readme): update installation instructions
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, Python version, dependencies
2. **Steps to reproduce**: Clear, step-by-step instructions
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Error messages**: Full error traceback
6. **Additional context**: Any relevant information

### Feature Requests

When requesting features, please include:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Use cases**: Examples of how it would be used
4. **Alternatives considered**: Other approaches you've considered

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in docstrings
- Keep documentation up to date with code changes

### User Documentation

- Update README.md for user-facing changes
- Add new sections to documentation as needed
- Include configuration examples

### API Documentation

- Document all configuration options
- Provide usage examples
- Include error handling information

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production

### Creating a Release

```bash
# Update version
bump2version patch  # or minor/major

# Create tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Create GitHub release
# (Do this on GitHub with release notes)
```

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README and inline documentation

## Recognition

Contributors will be recognized in:

- The README.md file
- Release notes
- The project's contributors page

Thank you for contributing to the Telegram Job Scraper project!
