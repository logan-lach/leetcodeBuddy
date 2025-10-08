from flask import Blueprint, request, jsonify, current_app
import os
import requests
from utils.supabase_client import get_supabase_client
from utils.crypto import encrypt_token
from utils.jwt_helper import generate_session_token

github_bp = Blueprint('github', __name__)

@github_bp.route('/authorize', methods=['POST'])
def authorize():
    """
    Handle GitHub OAuth authorization

    Flow:
    1. Receive authorization code from Chrome extension
    2. Exchange code for GitHub access token
    3. Fetch GitHub user info
    4. Encrypt and store token in Supabase
    5. Return JWT session token to extension

    Expected request body:
    {
        "code": "github_oauth_code"
    }

    Returns:
    {
        "session_token": "jwt_token",
        "user": {
            "username": "...",
            "email": "..."
        }
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    if not data or not data.get('code'):
        return jsonify({'error': 'Missing authorization code'}), 400

    try:
        # Step 1: Exchange authorization code for access token
        token_url = 'https://github.com/login/oauth/access_token'
        token_data = {
            'client_id': current_app.config['GITHUB_CLIENT_ID'],
            'client_secret': current_app.config['GITHUB_CLIENT_SECRET'],
            'code': data['code']
        }
        token_headers = {'Accept': 'application/json'}

        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        token_json = token_response.json()

        if 'error' in token_json:
            return jsonify({'error': f"GitHub OAuth error: {token_json.get('error_description', 'Unknown error')}"}), 400

        access_token = token_json.get('access_token')
        if not access_token:
            return jsonify({'error': 'Failed to obtain access token from GitHub'}), 400

        # Step 2: Fetch GitHub user info
        user_url = 'https://api.github.com/user'
        user_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        user_response = requests.get(user_url, headers=user_headers)
        user_response.raise_for_status()
        github_user = user_response.json()

        github_id = github_user.get('id')
        github_username = github_user.get('login')
        github_email = github_user.get('email')

        if not github_id or not github_username:
            return jsonify({'error': 'Failed to fetch GitHub user information'}), 400

        # Step 3: Store/update user in Supabase
        supabase = get_supabase_client()

        # Upsert user (insert or update if exists)
        user_result = supabase.table('users').upsert({
            'github_id': github_id,
            'github_username': github_username,
            'github_email': github_email
        }, on_conflict='github_id').execute()

        if not user_result.data:
            return jsonify({'error': 'Failed to create/update user in database'}), 500

        user_id = user_result.data[0]['id']

        # Step 4: Encrypt and store GitHub token
        encryption_key = current_app.config['ENCRYPTION_KEY']
        encrypted_token = encrypt_token(access_token, encryption_key)

        token_scopes = token_json.get('scope', '').split(',') if token_json.get('scope') else []

        # Upsert token (one token per user)
        token_result = supabase.table('github_tokens').upsert({
            'user_id': user_id,
            'encrypted_token': encrypted_token,
            'token_scopes': token_scopes
        }, on_conflict='user_id').execute()

        if not token_result.data:
            return jsonify({'error': 'Failed to store GitHub token'}), 500

        # Step 5: Generate session token for extension
        session_token = generate_session_token(user_id)

        return jsonify({
            'session_token': session_token,
            'user': {
                'username': github_username,
                'email': github_email
            }
        }), 200

    except requests.RequestException as e:
        return jsonify({'error': f'GitHub API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Authorization failed: {str(e)}'}), 500


@github_bp.route('/push-solution', methods=['POST'])
def push_solution():
    """
    Push LeetCode solution to GitHub repository

    Uses session token authentication - GitHub token fetched from Supabase

    Expected request body:
    {
        "repo_name": "leetcode-solutions",
        "problem_title": "Two Sum",
        "problem_number": 1,
        "difficulty": "Easy",
        "language": "python",
        "code": "def twoSum(...)...",
        "runtime": "52ms",
        "memory": "14.2MB"
    }

    Expected headers:
    Authorization: Bearer <session_token>

    Returns:
    {
        "success": true,
        "commit_url": "https://github.com/...",
        "file_path": "python/1_two_sum.py"
    }
    """
    from middleware.auth import require_session_token
    from utils.crypto import decrypt_token
    from github import Github
    import base64

    @require_session_token
    def push_solution_authenticated():
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        user_id = request.user_id

        # Validate required fields
        required_fields = ['repo_name', 'problem_title', 'code', 'language']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        try:
            # Fetch and decrypt GitHub token from Supabase
            supabase = get_supabase_client()
            token_result = supabase.table('github_tokens').select('encrypted_token').eq('user_id', user_id).execute()

            if not token_result.data:
                return jsonify({'error': 'GitHub token not found. Please re-authenticate.'}), 401

            encrypted_token = token_result.data[0]['encrypted_token']
            encryption_key = current_app.config['ENCRYPTION_KEY']
            github_token = decrypt_token(encrypted_token, encryption_key)

            # Authenticate with GitHub
            g = Github(github_token)
            user = g.get_user()
            repo = user.get_repo(data['repo_name'])

            # Format file path: language/problem_number_problem_title.ext
            language = data['language'].lower()
            problem_number = data.get('problem_number', '')
            problem_title = data['problem_title'].lower().replace(' ', '_')

            extension_map = {
                'python': 'py',
                'javascript': 'js',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'go': 'go',
                'rust': 'rs',
                'typescript': 'ts'
            }
            extension = extension_map.get(language, 'txt')

            file_name = f"{problem_number}_{problem_title}.{extension}" if problem_number else f"{problem_title}.{extension}"
            file_path = f"{language}/{file_name}"

            # Format code with metadata
            difficulty = data.get('difficulty', 'Unknown')
            runtime = data.get('runtime', 'N/A')
            memory = data.get('memory', 'N/A')
            code = data['code']

            content = f"""# {data['problem_title']}
# Difficulty: {difficulty}
# Runtime: {runtime}
# Memory: {memory}

{code}
"""

            # Commit to repository
            try:
                # Try to get existing file to update
                existing_file = repo.get_contents(file_path)
                commit = repo.update_file(
                    file_path,
                    f"Update solution for {data['problem_title']}",
                    content,
                    existing_file.sha
                )
                action = 'updated'
            except:
                # File doesn't exist, create new
                commit = repo.create_file(
                    file_path,
                    f"Add solution for {data['problem_title']}",
                    content
                )
                action = 'created'

            commit_url = commit['commit'].html_url

            return jsonify({
                'success': True,
                'commit_url': commit_url,
                'file_path': file_path,
                'action': action
            }), 200

        except Exception as e:
            return jsonify({'error': f'Failed to push solution: {str(e)}'}), 500

    return push_solution_authenticated()


@github_bp.route('/repos', methods=['GET'])
def list_repos():
    """
    List user's GitHub repositories

    Uses session token authentication - GitHub token fetched from Supabase

    Expected headers:
    Authorization: Bearer <session_token>

    Returns:
    {
        "repos": [
            {
                "name": "leetcode-solutions",
                "full_name": "username/leetcode-solutions",
                "url": "https://github.com/username/leetcode-solutions",
                "private": false
            },
            ...
        ]
    }
    """
    from middleware.auth import require_session_token
    from utils.crypto import decrypt_token
    from github import Github

    @require_session_token
    def list_repos_authenticated():
        user_id = request.user_id

        try:
            # Fetch and decrypt GitHub token from Supabase
            supabase = get_supabase_client()
            token_result = supabase.table('github_tokens').select('encrypted_token').eq('user_id', user_id).execute()

            if not token_result.data:
                return jsonify({'error': 'GitHub token not found. Please re-authenticate.'}), 401

            encrypted_token = token_result.data[0]['encrypted_token']
            encryption_key = current_app.config['ENCRYPTION_KEY']
            github_token = decrypt_token(encrypted_token, encryption_key)

            # Authenticate with GitHub
            g = Github(github_token)
            user = g.get_user()

            # Fetch user's repositories
            repos = []
            for repo in user.get_repos():
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'url': repo.html_url,
                    'private': repo.private
                })

            return jsonify({'repos': repos}), 200

        except Exception as e:
            return jsonify({'error': f'Failed to fetch repositories: {str(e)}'}), 500

    return list_repos_authenticated()


@github_bp.route('/revoke', methods=['POST'])
def revoke():
    """
    Revoke GitHub authorization (sign out)

    Deletes user's GitHub token from Supabase

    Expected headers:
    Authorization: Bearer <session_token>

    Returns:
    {
        "success": true,
        "message": "Authorization revoked successfully"
    }
    """
    from middleware.auth import require_session_token

    @require_session_token
    def revoke_authenticated():
        user_id = request.user_id

        try:
            # Delete GitHub token from Supabase
            supabase = get_supabase_client()
            result = supabase.table('github_tokens').delete().eq('user_id', user_id).execute()

            # Note: We're not deleting the user record, just the token
            # This allows the user to re-authenticate later

            return jsonify({
                'success': True,
                'message': 'Authorization revoked successfully'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Failed to revoke authorization: {str(e)}'}), 500

    return revoke_authenticated()


@github_bp.route('/setup-repo', methods=['POST'])
def setup_repo():
    """
    Create a new GitHub repository for LeetCode solutions

    Uses session token authentication - GitHub token fetched from Supabase

    Expected request body:
    {
        "repo_name": "leetcode-solutions",
        "description": "My LeetCode problem solutions",
        "private": false
    }

    Expected headers:
    Authorization: Bearer <session_token>

    Returns:
    {
        "success": true,
        "repo_url": "https://github.com/username/leetcode-solutions",
        "repo_name": "leetcode-solutions"
    }
    """
    from middleware.auth import require_session_token
    from utils.crypto import decrypt_token
    from github import Github

    @require_session_token
    def setup_repo_authenticated():
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        user_id = request.user_id

        if not data or not data.get('repo_name'):
            return jsonify({'error': 'Missing repo_name'}), 400

        try:
            # Fetch and decrypt GitHub token from Supabase
            supabase = get_supabase_client()
            token_result = supabase.table('github_tokens').select('encrypted_token').eq('user_id', user_id).execute()

            if not token_result.data:
                return jsonify({'error': 'GitHub token not found. Please re-authenticate.'}), 401

            encrypted_token = token_result.data[0]['encrypted_token']
            encryption_key = current_app.config['ENCRYPTION_KEY']
            github_token = decrypt_token(encrypted_token, encryption_key)

            # Authenticate with GitHub
            g = Github(github_token)
            user = g.get_user()

            # Create repository
            repo_name = data['repo_name']
            description = data.get('description', 'My LeetCode problem solutions')
            private = data.get('private', False)

            repo = user.create_repo(
                repo_name,
                description=description,
                private=private,
                auto_init=True  # Initialize with README
            )

            return jsonify({
                'success': True,
                'repo_url': repo.html_url,
                'repo_name': repo.name,
                'full_name': repo.full_name
            }), 201

        except Exception as e:
            return jsonify({'error': f'Failed to create repository: {str(e)}'}), 500

    return setup_repo_authenticated()
