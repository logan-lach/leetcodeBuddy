# Backend Test Suite

Comprehensive unit tests for the leetcodeBuddy Flask backend API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run all tests:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov=routes --cov-report=html
```

4. Run specific test file:
```bash
pytest tests/test_github_routes.py
```

5. Run specific test class:
```bash
pytest tests/test_github_routes.py::TestAuthorizeEndpoint
```

6. Run specific test:
```bash
pytest tests/test_github_routes.py::TestAuthorizeEndpoint::test_authorize_success
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_github_routes.py    # Tests for GitHub API endpoints
└── README.md               # This file
```

## Test Coverage

### Endpoints Tested

1. **Health Check** (`GET /health`)
   - Successful health check
   - Method not allowed

2. **OAuth Authorization** (`POST /api/github/authorize`)
   - Successful authorization with valid code
   - Missing authorization code
   - Empty code string
   - No JSON body
   - Invalid JSON format
   - Wrong content type
   - Null code value
   - Method not allowed

3. **Push Solution** (`POST /api/github/push-solution`)
   - Successful push with all fields
   - Missing each required field individually
   - Missing multiple required fields
   - Optional fields missing (should succeed)
   - Empty code string
   - No JSON body
   - Invalid JSON format
   - Extra unexpected fields
   - Method not allowed
   - Special characters in problem title
   - Unicode characters in code

4. **List Repositories** (`GET /api/github/repos`)
   - Successful listing with valid Bearer token
   - Missing Authorization header
   - Invalid Authorization format
   - Missing Bearer prefix
   - Empty Authorization header
   - Bearer only without token
   - Case sensitive Bearer check
   - Method not allowed
   - Multiple Authorization headers

5. **Setup Repository** (`POST /api/github/setup-repo`)
   - Successful creation with all fields
   - Minimal required fields only
   - Missing access_token
   - Missing repo_name
   - Missing both required fields
   - Empty access_token
   - Empty repo_name
   - No JSON body
   - Invalid JSON format
   - Null values
   - Method not allowed
   - Special characters in repo name
   - Private flag set to True
   - Long description

6. **Integration Tests**
   - CORS headers present
   - All endpoints return valid JSON
   - Non-existent endpoint handling
   - Blueprint prefix validation

## Test Statistics

- **Total Test Cases**: 73
- **Test Classes**: 6
- **Endpoints Covered**: 5
- **Code Coverage**: High (all routes and error paths)

## Fixtures

All fixtures are defined in `conftest.py`:

- `app` - Flask application instance with test configuration
- `client` - Flask test client for making requests
- `runner` - Flask CLI test runner
- `valid_oauth_code` - Sample OAuth code
- `valid_access_token` - Sample GitHub access token
- `valid_solution_data` - Complete solution submission data
- `valid_repo_data` - Repository creation data
- `auth_headers` - HTTP headers with Bearer token

## Writing New Tests

When adding new tests:

1. Use descriptive test names that explain what is being tested
2. Add docstrings explaining the expected behavior
3. Use fixtures for common test data
4. Group related tests in test classes
5. Test both success and failure scenarios
6. Include edge cases and boundary conditions

Example:
```python
def test_new_feature_success(client, fixture_name):
    """
    Test successful execution of new feature.

    Expected: 200 OK with expected response
    """
    response = client.post('/api/endpoint',
                          data=json.dumps({'field': 'value'}),
                          content_type='application/json')
    assert response.status_code == 200
```
