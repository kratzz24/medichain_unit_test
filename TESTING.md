# MediChain Testing Guide

This document provides information about the testing setup and CI/CD pipeline for the MediChain project.

## 🧪 Testing Overview

The project includes comprehensive testing for both backend (Python/Flask) and frontend (React) components.

### Backend Testing

**Framework:** pytest with Flask-Testing
**Coverage:** pytest-cov for coverage reporting
**Location:** `backend/tests/`

#### Running Backend Tests

```bash
# From the backend directory
cd backend

# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_auth_routes.py -v

# Run using the test runner script
python run_tests.py
```

#### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures and configuration
├── test_app.py             # Flask app tests
├── test_auth_routes.py     # Authentication route tests
├── test_database.py        # Database operation tests
└── __pycache__/
```

### Frontend Testing

**Framework:** Jest with React Testing Library
**Location:** `src/`

#### Running Frontend Tests

```bash
# Run all tests
npm test

# Run in CI mode (no watch)
npm run test:ci

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/Dashboard.test.js
```

#### Test Structure

```
src/
├── App.test.js                    # Main app component tests
├── components/
│   └── Dashboard.test.js         # Dashboard component tests
├── context/
│   └── AuthContext.test.js       # Authentication context tests
└── setupTests.js                 # Test configuration
```

## 🚀 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

### Workflow Triggers

- **Push** to `main` or `develop` branches
- **Pull Requests** to `main` or `develop` branches

### CI Jobs

1. **Backend Tests** (`backend-tests`)
   - Python 3.9 environment
   - Install dependencies
   - Run pytest with coverage
   - Upload coverage reports

2. **Frontend Tests** (`frontend-tests`)
   - Node.js 18 environment
   - Install dependencies
   - Run Jest tests with coverage
   - Upload coverage reports

3. **Backend Linting** (`lint-backend`)
   - Flake8 for code quality
   - Black for code formatting
   - isort for import sorting

4. **Frontend Linting** (`lint-frontend`)
   - ESLint for JavaScript/React linting

5. **Security Scan** (`security-scan`)
   - Trivy vulnerability scanner
   - SARIF report generation

6. **Frontend Build** (`build-frontend`)
   - Build production bundle
   - Upload build artifacts

### Coverage Reports

Coverage reports are automatically generated and uploaded to Codecov for both backend and frontend code.

## 📊 Test Coverage Goals

- **Backend:** Minimum 80% coverage
- **Frontend:** Minimum 70% coverage
- **Overall:** Minimum 75% coverage

## 🛠️ Development Workflow

### Before Committing

1. **Run tests locally:**
   ```bash
   # Backend
   cd backend && python -m pytest tests/ -v --cov=.

   # Frontend
   npm run test:ci
   ```

2. **Check code quality:**
   ```bash
   # Backend
   flake8 backend/
   black --check backend/
   isort --check-only backend/

   # Frontend
   npm run lint
   ```

3. **Fix any issues** before committing

### Writing New Tests

#### Backend Test Example

```python
import pytest
from unittest.mock import Mock, patch

def test_user_registration(client):
    """Test user registration endpoint"""
    with patch('your_module.supabase') as mock_supabase:
        # Arrange
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[{'id': '123', 'email': 'test@example.com'}]
        )

        # Act
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
```

#### Frontend Test Example

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UserProfile from './UserProfile';

test('displays user information', async () => {
  // Arrange
  const mockUser = { name: 'John Doe', email: 'john@example.com' };

  // Act
  render(<UserProfile user={mockUser} />);

  // Assert
  expect(screen.getByText('John Doe')).toBeInTheDocument();
  expect(screen.getByText('john@example.com')).toBeInTheDocument();
});
```

## 🔧 Configuration Files

- `backend/pytest.ini` - pytest configuration
- `backend/tests/conftest.py` - Shared test fixtures
- `.github/workflows/ci.yml` - GitHub Actions workflow
- `src/setupTests.js` - Jest configuration

## 📈 Monitoring Test Results

- **GitHub Actions:** Check the Actions tab in your repository
- **Codecov:** View coverage reports at [codecov.io](https://codecov.io)
- **Local Coverage:** Open `backend/htmlcov/index.html` for detailed reports

## 🤝 Contributing

When contributing to the project:

1. Write tests for new features
2. Ensure all tests pass locally
3. Maintain or improve code coverage
4. Follow the existing code style and patterns
5. Update this documentation if needed

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
