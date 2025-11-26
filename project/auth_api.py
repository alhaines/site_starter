#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# filename: /home/al/projects/mainmenu/auth_api.py
#
# Authentication API helper module for external applications (like mediaplayer)
# This provides session-based authentication checking and user information retrieval

from flask import Blueprint, session, jsonify, request
from functools import wraps

auth_api_bp = Blueprint('auth_api', __name__)


def is_logged_in():
    """
    Check if a user is currently logged in.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return bool(session.get('user_id') or session.get('IFLOGED_IN'))


def get_username():
    """
    Get the username of the currently logged-in user.
    
    Returns:
        str: Username if logged in, None otherwise
    """
    return session.get('username', None)


def get_user_id():
    """
    Get the user ID of the currently logged-in user.
    
    Returns:
        int: User ID if logged in, None otherwise
    """
    return session.get('user_id', None)


def get_user_level():
    """
    Get the access level of the currently logged-in user.
    
    Returns:
        int: User level (1-3) if logged in, 0 otherwise
    """
    return session.get('level', 0)


def get_user_info():
    """
    Get comprehensive information about the currently logged-in user.
    
    Returns:
        dict: Dictionary containing user information:
            - logged_in (bool): Whether user is logged in
            - username (str|None): Username if logged in
            - user_id (int|None): User ID if logged in
            - level (int): User access level (0 if not logged in)
    """
    return {
        'logged_in': is_logged_in(),
        'username': get_username(),
        'user_id': get_user_id(),
        'level': get_user_level()
    }


# API Routes for external applications
@auth_api_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    """
    API endpoint to check authentication status.
    Returns JSON with user information.
    
    Usage: GET /api/auth/status
    
    Response:
        {
            "logged_in": true/false,
            "username": "username" or null,
            "user_id": 123 or null,
            "level": 0-3
        }
    """
    return jsonify(get_user_info())


@auth_api_bp.route('/api/auth/check', methods=['GET'])
def auth_check():
    """
    Simple API endpoint to check if user is logged in.
    Returns JSON with boolean status.
    
    Usage: GET /api/auth/check
    
    Response:
        {
            "logged_in": true/false
        }
    """
    return jsonify({'logged_in': is_logged_in()})


@auth_api_bp.route('/api/auth/username', methods=['GET'])
def auth_username():
    """
    API endpoint to get current username.
    
    Usage: GET /api/auth/username
    
    Response:
        {
            "username": "username" or null
        }
    """
    return jsonify({'username': get_username()})


# Decorator for protecting routes in other applications
def require_login_api(f):
    """
    Decorator to protect API routes requiring authentication.
    Returns JSON error if not logged in.
    
    Usage:
        @require_login_api
        def my_protected_route():
            return jsonify({'data': 'secret'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return jsonify({
                'error': 'Authentication required',
                'logged_in': False
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# Example usage in templates or other modules:
# from auth_api import is_logged_in, get_username, get_user_info
# 
# if is_logged_in():
#     username = get_username()
#     print(f"User {username} is logged in")
