"""
Pytest configuration and fixtures for Flask backend tests
"""
import pytest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def app():
    """
    Create and configure a Flask application instance for testing.

    Returns:
        Flask: Configured Flask application with testing enabled
    """
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'GITHUB_CLIENT_ID': 'test-client-id',
        'GITHUB_CLIENT_SECRET': 'test-client-secret',
    })

    yield flask_app


@pytest.fixture
def client(app):
    """
    Create a test client for the Flask application.

    Args:
        app: Flask application fixture

    Returns:
        FlaskClient: Test client for making requests
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a test CLI runner for the Flask application.

    Args:
        app: Flask application fixture

    Returns:
        FlaskCliRunner: Test runner for CLI commands
    """
    return app.test_cli_runner()


@pytest.fixture
def valid_oauth_code():
    """
    Sample valid OAuth authorization code.

    Returns:
        str: Mock OAuth code
    """
    return 'github_oauth_code_1234567890abcdef'


@pytest.fixture
def valid_access_token():
    """
    Sample valid GitHub access token.

    Returns:
        str: Mock GitHub access token
    """
    return 'ghp_1234567890abcdefghijklmnopqrstuvwxyz'


@pytest.fixture
def valid_solution_data(valid_access_token):
    """
    Sample valid LeetCode solution data.

    Args:
        valid_access_token: Access token fixture

    Returns:
        dict: Complete solution submission data
    """
    return {
        'access_token': valid_access_token,
        'repo_name': 'leetcode-solutions',
        'problem_title': 'Two Sum',
        'problem_number': 1,
        'difficulty': 'Easy',
        'language': 'python',
        'code': 'def twoSum(nums, target):\n    # Solution code here\n    pass',
        'runtime': '52ms',
        'memory': '14.2MB'
    }


@pytest.fixture
def valid_repo_data(valid_access_token):
    """
    Sample valid repository creation data.

    Args:
        valid_access_token: Access token fixture

    Returns:
        dict: Repository setup data
    """
    return {
        'access_token': valid_access_token,
        'repo_name': 'leetcode-solutions',
        'description': 'My LeetCode problem solutions',
        'private': False
    }


@pytest.fixture
def auth_headers(valid_access_token):
    """
    Sample valid authorization headers.

    Args:
        valid_access_token: Access token fixture

    Returns:
        dict: HTTP headers with Bearer token
    """
    return {
        'Authorization': f'Bearer {valid_access_token}'
    }
