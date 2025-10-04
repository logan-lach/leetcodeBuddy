from flask import Blueprint, request, jsonify
import os

github_bp = Blueprint('github', __name__)

@github_bp.route('/authorize', methods=['POST'])
def authorize():
    """
    Handle GitHub OAuth callback

    Expected request body:
    {
        "code": "github_oauth_code"
    }

    Returns:
    {
        "access_token": "github_access_token",
        "user": {...}
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    if not data or not data.get('code'):
        return jsonify({'error': 'Missing authorization code'}), 400

    # TODO: Exchange code for access token with GitHub
    # TODO: Store token securely
    # TODO: Fetch user information

    return jsonify({
        'message': 'Authorization endpoint - implementation pending',
        'received_code': data['code'][:10] + '...'  # Show partial code for debugging
    }), 200


@github_bp.route('/push-solution', methods=['POST'])
def push_solution():
    """
    Push LeetCode solution to GitHub repository

    Expected request body:
    {
        "access_token": "user_github_token",
        "repo_name": "leetcode-solutions",
        "problem_title": "Two Sum",
        "problem_number": 1,
        "difficulty": "Easy",
        "language": "python",
        "code": "def twoSum(...)...",
        "runtime": "52ms",
        "memory": "14.2MB"
    }

    Returns:
    {
        "success": true,
        "commit_url": "https://github.com/..."
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ['access_token', 'repo_name', 'problem_title', 'code', 'language']
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # TODO: Authenticate with GitHub using access_token
    # TODO: Format code with metadata (title, difficulty, stats)
    # TODO: Create file path: language/problem_number_problem_title.ext
    # TODO: Commit and push to repository
    # TODO: Return commit URL

    return jsonify({
        'message': 'Push solution endpoint - implementation pending',
        'problem': data['problem_title'],
        'language': data['language']
    }), 200


@github_bp.route('/repos', methods=['GET'])
def list_repos():
    """
    List user's GitHub repositories

    Expected headers:
    Authorization: Bearer <access_token>

    Returns:
    {
        "repos": [
            {"name": "leetcode-solutions", "url": "..."},
            ...
        ]
    }
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401

    access_token = auth_header.split('Bearer ')[1]

    # TODO: Fetch user's repositories from GitHub
    # TODO: Filter for relevant repos or show all

    return jsonify({
        'message': 'List repos endpoint - implementation pending',
        'repos': []
    }), 200


@github_bp.route('/setup-repo', methods=['POST'])
def setup_repo():
    """
    Create a new GitHub repository for LeetCode solutions

    Expected request body:
    {
        "access_token": "user_github_token",
        "repo_name": "leetcode-solutions",
        "description": "My LeetCode problem solutions",
        "private": false
    }

    Returns:
    {
        "success": true,
        "repo_url": "https://github.com/username/leetcode-solutions",
        "repo_name": "leetcode-solutions"
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    if not data or not data.get('access_token') or not data.get('repo_name'):
        return jsonify({'error': 'Missing access_token or repo_name'}), 400

    # TODO: Create repository using GitHub API
    # TODO: Initialize with README
    # TODO: Create directory structure (python/, javascript/, etc.)
    # TODO: Return repository details

    return jsonify({
        'message': 'Setup repo endpoint - implementation pending',
        'repo_name': data['repo_name']
    }), 200
