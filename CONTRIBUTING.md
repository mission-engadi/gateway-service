# Contributing to Gateway Service

Thank you for your interest in contributing to Mission Engadi! This document provides guidelines and instructions for contributing to this service.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Review Process](#review-process)

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🚀 Getting Started

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues reported in GitHub Issues
- **Features**: Implement new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize code performance
- **Refactoring**: Improve code structure without changing behavior

### Before You Start

1. **Check existing issues**: Look for existing issues or discussions related to your contribution
2. **Create an issue**: If one doesn't exist, create an issue to discuss your proposed changes
3. **Get feedback**: Wait for feedback from maintainers before starting significant work
4. **Fork the repository**: Create your own fork to work in

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)
- Git

### Setup Steps

1. **Fork and clone**

```bash
git clone https://github.com/YOUR_USERNAME/gateway_service.git
cd gateway_service
```

2. **Add upstream remote**

```bash
git remote add upstream https://github.com/mission-engadi/gateway_service.git
```

3. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. **Setup environment**

```bash
cp .env.example .env
# Edit .env with your local configuration
```

6. **Start services**

```bash
docker-compose up -d
```

7. **Run migrations**

```bash
alembic upgrade head
```

8. **Verify setup**

```bash
pytest
uvicorn app.main:app --reload
```

## 🔄 Making Changes

### Create a Feature Branch

Always create a new branch for your changes:

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Development Workflow

1. **Make your changes**
   - Write clean, readable code
   - Follow coding standards (see below)
   - Add or update tests
   - Update documentation

2. **Test your changes**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific tests
pytest tests/unit/test_your_feature.py
```

3. **Check code quality**

```bash
# Format code
black app tests
isort app tests

# Lint code
flake8 app tests
mypy app

# Security check
bandit -r app
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: add new feature"
```

## 📏 Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized with isort

### Code Organization

#### File Structure

```python
"""Module docstring.

Detailed description of the module's purpose.
"""

# Standard library imports
import os
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from sqlalchemy import select

# Local imports
from app.core.config import settings
from app.models.example import ExampleModel

# Constants
MAX_ITEMS = 100

# Classes and functions
class MyClass:
    """Class docstring."""
    pass


def my_function():
    """Function docstring."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def create_user(username: str, email: str, password: str) -> User:
    """Create a new user.
    
    Args:
        username: The user's username
        email: The user's email address
        password: The user's password (will be hashed)
    
    Returns:
        The created User object
    
    Raises:
        ValueError: If username already exists
    """
    pass
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional

def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> List[User]:
    """Get list of users."""
    pass
```

### Error Handling

Be explicit with error handling:

```python
from fastapi import HTTPException, status

async def get_user(user_id: int) -> User:
    """Get user by ID."""
    user = await UserService.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    
    return user
```

### Async/Await

Use async/await consistently:

```python
# Good
async def get_items(db: AsyncSession) -> List[Item]:
    result = await db.execute(select(Item))
    return list(result.scalars().all())

# Avoid mixing sync and async
```

## 🧪 Testing Guidelines

### Test Structure

Organize tests by type:

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_services.py
│   └── test_security.py
├── integration/       # Integration tests (with database)
│   ├── test_endpoints.py
│   └── test_workflows.py
└── conftest.py        # Shared fixtures
```

### Writing Tests

#### Unit Tests

Test individual functions in isolation:

```python
import pytest
from app.core.security import verify_password, get_password_hash

@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing functions."""
    
    def test_password_hash_and_verify(self):
        """Test that password hashing and verification works."""
        password = "secure_password"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails verification."""
        password = "correct"
        wrong = "wrong"
        hashed = get_password_hash(password)
        
        assert not verify_password(wrong, hashed)
```

#### Integration Tests

Test API endpoints with database:

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestUserEndpoints:
    """Test user management endpoints."""
    
    def test_create_user(self, client: TestClient, admin_headers: dict):
        """Test user creation endpoint."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "secure_password",
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Sensitive data not returned
```

### Test Coverage

Aim for high test coverage:

- **Minimum**: 80% overall coverage
- **Critical paths**: 100% coverage for security and business logic
- **New features**: Must include tests

Check coverage:

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📝 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(auth): add JWT token refresh endpoint"

# Bug fix
git commit -m "fix(database): resolve connection pool exhaustion"

# Documentation
git commit -m "docs(api): update authentication examples"

# Breaking change
git commit -m "feat(api)!: change user schema structure

BREAKING CHANGE: User.name field split into first_name and last_name"
```

### Guidelines

- Use imperative mood ("add feature" not "added feature")
- Keep subject line under 72 characters
- Add body for complex changes
- Reference issues: "Fixes #123" or "Closes #456"

## 🔀 Pull Request Process

### Before Submitting

Checklist before creating a PR:

- [ ] Tests pass: `pytest`
- [ ] Code is formatted: `black app tests`
- [ ] Imports are sorted: `isort app tests`
- [ ] Linting passes: `flake8 app tests`
- [ ] Type checking passes: `mypy app`
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### Creating a Pull Request

1. **Push your branch**

```bash
git push origin feature/your-feature
```

2. **Create PR on GitHub**
   - Use a clear, descriptive title
   - Follow the PR template
   - Link related issues
   - Add screenshots if UI changes

3. **PR Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated

## Related Issues
Fixes #123
Relates to #456
```

### After Submitting

- **Respond to feedback**: Address reviewer comments promptly
- **Update PR**: Push additional commits as needed
- **Keep updated**: Merge main if conflicts arise
- **Be patient**: Maintainers will review when possible

## 👀 Review Process

### For Contributors

When your PR is under review:

1. **Be responsive**: Respond to comments within a few days
2. **Be open**: Accept constructive criticism gracefully
3. **Explain decisions**: If you disagree, explain your reasoning
4. **Update promptly**: Make requested changes quickly
5. **Ask questions**: If feedback is unclear, ask for clarification

### For Reviewers

When reviewing PRs:

1. **Be respectful**: Provide constructive, helpful feedback
2. **Be specific**: Point to specific lines and suggest improvements
3. **Be thorough**: Check code, tests, and documentation
4. **Be timely**: Review within a few days if possible
5. **Approve or request changes**: Don't leave PRs in limbo

### Review Criteria

PRs should meet these criteria:

- **Functionality**: Code works as intended
- **Tests**: Adequate test coverage
- **Code quality**: Follows style guidelines
- **Documentation**: Clear and up-to-date
- **Security**: No security vulnerabilities
- **Performance**: No significant performance regression

## 🎯 First Contributions

New to open source? Here's how to start:

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

### Simple Contributions

Easy ways to contribute:
- Fix typos in documentation
- Improve error messages
- Add code comments
- Write tests for existing code
- Update outdated documentation

### Getting Help

Need help? Reach out:
- Comment on the issue
- Ask in pull request
- Email: dev@engadi.org

## 📚 Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [pytest Documentation](https://docs.pytest.org)

### Tools

- [Black](https://black.readthedocs.io) - Code formatter
- [isort](https://pycqa.github.io/isort/) - Import sorter
- [flake8](https://flake8.pycqa.org) - Linter
- [mypy](https://mypy.readthedocs.io) - Type checker

### Mission Engadi

- [Website](https://engadi.org)
- [Documentation](https://docs.engadi.org)
- [GitHub](https://github.com/mission-engadi)

## 🤝 Community

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and discussions
- **Email**: dev@engadi.org for private matters

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Commit history

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Mission Engadi! 🙏
