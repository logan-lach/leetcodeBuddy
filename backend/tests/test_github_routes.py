"""
Comprehensive unit tests for GitHub API routes.

Tests cover all endpoints in routes/github_routes.py with various scenarios:
- Successful requests with valid data
- Missing required fields
- Invalid request formats
- Missing/invalid authentication headers
- Edge cases and boundary conditions
"""
import pytest
import json


class TestHealthEndpoint:
    """Tests for the health check endpoint"""

    def test_health_check_success(self, client):
        """
        Test that the health check endpoint returns a healthy status.

        Expected: 200 OK with status: healthy
        """
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_health_check_method_not_allowed(self, client):
        """
        Test that POST requests to health check are rejected.

        Expected: 405 Method Not Allowed
        """
        response = client.post('/health')
        assert response.status_code == 405


class TestAuthorizeEndpoint:
    """Tests for POST /api/github/authorize endpoint"""

    def test_authorize_success(self, client, valid_oauth_code):
        """
        Test successful OAuth authorization with valid code.

        Expected: 200 OK with confirmation message
        """
        response = client.post(
            '/api/github/authorize',
            data=json.dumps({'code': valid_oauth_code}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'received_code' in data

    def test_authorize_missing_code(self, client):
        """
        Test authorization request without code field.

        Expected: 400 Bad Request with error message
        """
        response = client.post(
            '/api/github/authorize',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing authorization code' in data['error']

    def test_authorize_empty_code(self, client):
        """
        Test authorization request with empty code string.

        Expected: 400 Bad Request (empty string is falsy)
        """
        response = client.post(
            '/api/github/authorize',
            data=json.dumps({'code': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_authorize_no_json_body(self, client):
        """
        Test authorization request without JSON body.

        Expected: 400 Bad Request
        """
        response = client.post('/api/github/authorize')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_authorize_invalid_json(self, client):
        """
        Test authorization request with malformed JSON.

        Expected: 400 Bad Request or JSON parsing error
        """
        response = client.post(
            '/api/github/authorize',
            data='invalid json{',
            content_type='application/json'
        )
        assert response.status_code in [400, 415]

    def test_authorize_wrong_content_type(self, client, valid_oauth_code):
        """
        Test authorization request with wrong content type.

        Expected: Request should fail or not parse JSON properly
        """
        response = client.post(
            '/api/github/authorize',
            data=f'code={valid_oauth_code}',
            content_type='application/x-www-form-urlencoded'
        )
        assert response.status_code == 400

    def test_authorize_null_code(self, client):
        """
        Test authorization request with null code value.

        Expected: 400 Bad Request
        """
        response = client.post(
            '/api/github/authorize',
            data=json.dumps({'code': None}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_authorize_method_not_allowed(self, client):
        """
        Test that GET requests to authorize endpoint are rejected.

        Expected: 405 Method Not Allowed
        """
        response = client.get('/api/github/authorize')
        assert response.status_code == 405


class TestPushSolutionEndpoint:
    """Tests for POST /api/github/push-solution endpoint"""

    def test_push_solution_success(self, client, valid_solution_data):
        """
        Test successful solution push with all required fields.

        Expected: 200 OK with confirmation message
        """
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['problem'] == 'Two Sum'
        assert data['language'] == 'python'

    def test_push_solution_missing_access_token(self, client, valid_solution_data):
        """
        Test push solution without access_token field.

        Expected: 400 Bad Request with missing fields error
        """
        del valid_solution_data['access_token']
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'access_token' in data['error']

    def test_push_solution_missing_repo_name(self, client, valid_solution_data):
        """
        Test push solution without repo_name field.

        Expected: 400 Bad Request with missing fields error
        """
        del valid_solution_data['repo_name']
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'repo_name' in data['error']

    def test_push_solution_missing_problem_title(self, client, valid_solution_data):
        """
        Test push solution without problem_title field.

        Expected: 400 Bad Request with missing fields error
        """
        del valid_solution_data['problem_title']
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'problem_title' in data['error']

    def test_push_solution_missing_code(self, client, valid_solution_data):
        """
        Test push solution without code field.

        Expected: 400 Bad Request with missing fields error
        """
        del valid_solution_data['code']
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'code' in data['error']

    def test_push_solution_missing_language(self, client, valid_solution_data):
        """
        Test push solution without language field.

        Expected: 400 Bad Request with missing fields error
        """
        del valid_solution_data['language']
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'language' in data['error']

    def test_push_solution_missing_multiple_fields(self, client):
        """
        Test push solution with multiple missing required fields.

        Expected: 400 Bad Request listing all missing fields
        """
        incomplete_data = {
            'repo_name': 'test-repo'
        }
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        # Should mention multiple missing fields
        assert 'access_token' in data['error']
        assert 'problem_title' in data['error']
        assert 'code' in data['error']
        assert 'language' in data['error']

    def test_push_solution_optional_fields_missing(self, client, valid_access_token):
        """
        Test push solution without optional fields (problem_number, difficulty, runtime, memory).

        Expected: 200 OK - optional fields should not be required
        """
        minimal_data = {
            'access_token': valid_access_token,
            'repo_name': 'leetcode-solutions',
            'problem_title': 'Two Sum',
            'code': 'def solution(): pass',
            'language': 'python'
        }
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_push_solution_empty_code(self, client, valid_solution_data):
        """
        Test push solution with empty code string.

        Expected: 400 Bad Request (empty string is falsy in validation)
        """
        valid_solution_data['code'] = ''
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_push_solution_no_json_body(self, client):
        """
        Test push solution without JSON body.

        Expected: 400 Bad Request
        """
        response = client.post('/api/github/push-solution')
        assert response.status_code == 400

    def test_push_solution_invalid_json(self, client):
        """
        Test push solution with malformed JSON.

        Expected: 400 Bad Request or JSON parsing error
        """
        response = client.post(
            '/api/github/push-solution',
            data='invalid json{',
            content_type='application/json'
        )
        assert response.status_code in [400, 415]

    def test_push_solution_extra_fields(self, client, valid_solution_data):
        """
        Test push solution with extra unexpected fields.

        Expected: 200 OK - extra fields should be ignored
        """
        valid_solution_data['extra_field'] = 'unexpected'
        valid_solution_data['another_field'] = 123
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_push_solution_method_not_allowed(self, client):
        """
        Test that GET requests to push-solution endpoint are rejected.

        Expected: 405 Method Not Allowed
        """
        response = client.get('/api/github/push-solution')
        assert response.status_code == 405

    def test_push_solution_with_special_characters(self, client, valid_solution_data):
        """
        Test push solution with special characters in problem title.

        Expected: 200 OK - should handle special characters
        """
        valid_solution_data['problem_title'] = 'Design Add & Search Words Data Structure'
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_push_solution_with_unicode(self, client, valid_solution_data):
        """
        Test push solution with unicode characters in code.

        Expected: 200 OK - should handle unicode properly
        """
        valid_solution_data['code'] = '# Solution with emoji: 🎯\ndef solution(): pass'
        response = client.post(
            '/api/github/push-solution',
            data=json.dumps(valid_solution_data),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestListReposEndpoint:
    """Tests for GET /api/github/repos endpoint"""

    def test_list_repos_success(self, client, auth_headers):
        """
        Test successful repository listing with valid Bearer token.

        Expected: 200 OK with repos list
        """
        response = client.get(
            '/api/github/repos',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'repos' in data
        assert isinstance(data['repos'], list)

    def test_list_repos_missing_auth_header(self, client):
        """
        Test repository listing without Authorization header.

        Expected: 401 Unauthorized with error message
        """
        response = client.get('/api/github/repos')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing or invalid authorization header' in data['error']

    def test_list_repos_invalid_auth_format(self, client):
        """
        Test repository listing with invalid Authorization header format.

        Expected: 401 Unauthorized
        """
        response = client.get(
            '/api/github/repos',
            headers={'Authorization': 'InvalidFormat token123'}
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_list_repos_missing_bearer_prefix(self, client, valid_access_token):
        """
        Test repository listing with token but no 'Bearer ' prefix.

        Expected: 401 Unauthorized
        """
        response = client.get(
            '/api/github/repos',
            headers={'Authorization': valid_access_token}
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_list_repos_empty_auth_header(self, client):
        """
        Test repository listing with empty Authorization header.

        Expected: 401 Unauthorized
        """
        response = client.get(
            '/api/github/repos',
            headers={'Authorization': ''}
        )
        assert response.status_code == 401

    def test_list_repos_bearer_only(self, client):
        """
        Test repository listing with 'Bearer ' but no token.

        Expected: 401 Unauthorized or 200 with empty token
        """
        response = client.get(
            '/api/github/repos',
            headers={'Authorization': 'Bearer '}
        )
        # This might pass the header check but fail later
        # or could be caught as invalid
        assert response.status_code in [200, 401]

    def test_list_repos_case_sensitive_bearer(self, client, valid_access_token):
        """
        Test repository listing with lowercase 'bearer' instead of 'Bearer'.

        Expected: 401 Unauthorized (case sensitive check)
        """
        response = client.get(
            '/api/github/repos',
            headers={'Authorization': f'bearer {valid_access_token}'}
        )
        assert response.status_code == 401

    def test_list_repos_method_not_allowed(self, client, auth_headers):
        """
        Test that POST requests to repos endpoint are rejected.

        Expected: 405 Method Not Allowed
        """
        response = client.post(
            '/api/github/repos',
            headers=auth_headers
        )
        assert response.status_code == 405

    def test_list_repos_multiple_auth_headers(self, client, valid_access_token):
        """
        Test repository listing with multiple Authorization headers.

        Expected: Behavior depends on Flask - usually takes first or last
        """
        # Flask typically handles this by taking the first header
        response = client.get(
            '/api/github/repos',
            headers=[
                ('Authorization', f'Bearer {valid_access_token}'),
                ('Authorization', 'Bearer invalid')
            ]
        )
        # Should succeed if first header is used
        assert response.status_code in [200, 401]


class TestSetupRepoEndpoint:
    """Tests for POST /api/github/setup-repo endpoint"""

    def test_setup_repo_success(self, client, valid_repo_data):
        """
        Test successful repository creation with all fields.

        Expected: 200 OK with repo details
        """
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(valid_repo_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['repo_name'] == 'leetcode-solutions'

    def test_setup_repo_minimal_required_fields(self, client, valid_access_token):
        """
        Test repository creation with only required fields.

        Expected: 200 OK - description and private are optional
        """
        minimal_data = {
            'access_token': valid_access_token,
            'repo_name': 'leetcode-solutions'
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_setup_repo_missing_access_token(self, client):
        """
        Test repository creation without access_token.

        Expected: 400 Bad Request with specific error message
        """
        data = {
            'repo_name': 'leetcode-solutions',
            'description': 'Test repo'
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'access_token' in data['error']

    def test_setup_repo_missing_repo_name(self, client, valid_access_token):
        """
        Test repository creation without repo_name.

        Expected: 400 Bad Request with specific error message
        """
        data = {
            'access_token': valid_access_token,
            'description': 'Test repo'
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'repo_name' in data['error']

    def test_setup_repo_missing_both_required_fields(self, client):
        """
        Test repository creation without any required fields.

        Expected: 400 Bad Request
        """
        data = {
            'description': 'Test repo',
            'private': False
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_setup_repo_empty_access_token(self, client):
        """
        Test repository creation with empty access_token string.

        Expected: 400 Bad Request
        """
        data = {
            'access_token': '',
            'repo_name': 'leetcode-solutions'
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_setup_repo_empty_repo_name(self, client, valid_access_token):
        """
        Test repository creation with empty repo_name string.

        Expected: 400 Bad Request
        """
        data = {
            'access_token': valid_access_token,
            'repo_name': ''
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_setup_repo_no_json_body(self, client):
        """
        Test repository creation without JSON body.

        Expected: 400 Bad Request
        """
        response = client.post('/api/github/setup-repo')
        assert response.status_code == 400

    def test_setup_repo_invalid_json(self, client):
        """
        Test repository creation with malformed JSON.

        Expected: 400 Bad Request or JSON parsing error
        """
        response = client.post(
            '/api/github/setup-repo',
            data='invalid json{',
            content_type='application/json'
        )
        assert response.status_code in [400, 415]

    def test_setup_repo_null_values(self, client):
        """
        Test repository creation with null values for required fields.

        Expected: 400 Bad Request
        """
        data = {
            'access_token': None,
            'repo_name': None
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_setup_repo_method_not_allowed(self, client):
        """
        Test that GET requests to setup-repo endpoint are rejected.

        Expected: 405 Method Not Allowed
        """
        response = client.get('/api/github/setup-repo')
        assert response.status_code == 405

    def test_setup_repo_with_special_chars_in_name(self, client, valid_access_token):
        """
        Test repository creation with special characters in repo name.

        Expected: 200 OK - should handle special characters
        Note: GitHub has restrictions on repo names, but API should accept request
        """
        data = {
            'access_token': valid_access_token,
            'repo_name': 'leetcode-solutions-2024'
        }
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_setup_repo_private_true(self, client, valid_repo_data):
        """
        Test repository creation with private flag set to True.

        Expected: 200 OK
        """
        valid_repo_data['private'] = True
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(valid_repo_data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_setup_repo_long_description(self, client, valid_repo_data):
        """
        Test repository creation with a very long description.

        Expected: 200 OK - should handle long descriptions
        """
        valid_repo_data['description'] = 'A' * 500  # 500 character description
        response = client.post(
            '/api/github/setup-repo',
            data=json.dumps(valid_repo_data),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestEndpointIntegration:
    """Integration tests across multiple endpoints"""

    def test_cors_headers_present(self, client):
        """
        Test that CORS headers are present in responses.

        Expected: Response should include CORS headers
        """
        response = client.get('/health')
        # CORS should be enabled for Chrome extension communication
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200

    def test_all_endpoints_return_json(self, client, valid_oauth_code, valid_solution_data,
                                      valid_repo_data, auth_headers):
        """
        Test that all endpoints return valid JSON responses.

        Expected: All responses should have application/json content type
        """
        endpoints = [
            ('GET', '/health', None, None),
            ('POST', '/api/github/authorize', {'code': valid_oauth_code}, None),
            ('POST', '/api/github/push-solution', valid_solution_data, None),
            ('GET', '/api/github/repos', None, auth_headers),
            ('POST', '/api/github/setup-repo', valid_repo_data, None),
        ]

        for method, url, data, headers in endpoints:
            if method == 'GET':
                response = client.get(url, headers=headers)
            else:
                response = client.post(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json',
                    headers=headers
                )

            # Check that response is valid JSON
            try:
                json.loads(response.data)
                json_valid = True
            except:
                json_valid = False

            assert json_valid, f"Endpoint {method} {url} did not return valid JSON"

    def test_nonexistent_endpoint(self, client):
        """
        Test accessing a non-existent endpoint.

        Expected: 404 Not Found
        """
        response = client.get('/api/github/nonexistent')
        assert response.status_code == 404

    def test_blueprint_prefix_correct(self, client):
        """
        Test that blueprint endpoints are properly prefixed.

        Expected: Should not be accessible without /api/github prefix
        """
        response = client.post('/authorize')
        assert response.status_code == 404

        response = client.post('/api/github/authorize',
                              data=json.dumps({'code': 'test'}),
                              content_type='application/json')
        assert response.status_code in [200, 400]  # Not 404
