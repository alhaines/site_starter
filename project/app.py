#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# filename: /home/your_user/projects/site_starter/project/app.py
#
# Main application file for the MainMenu system

from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sys
sys.path.append('/home/your_user/py')
from MySql import MySQL
import config
import menu_view
import gallery
from auth import init_auth, login_required
from auth_api import auth_api_bp
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Session configuration for cross-subdomain authentication
# This allows login.your_domain session to be shared with media.your_domain
app.config['SESSION_COOKIE_NAME'] = 'your_session'
app.config['SESSION_COOKIE_DOMAIN'] = '.your_domain'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for HTTP, True for HTTPS

db = MySQL(**config.mysql_config)
# initialize auth blueprint and give it the db instance
init_auth(app, db)
# expose DB to blueprints via app.config
app.config['DB'] = db
# register menu blueprint
app.register_blueprint(menu_view.menu_bp)
# register gallery blueprint
app.register_blueprint(gallery.gallery_bp)
# register auth API blueprint for external apps (like mediaplayer)
app.register_blueprint(auth_api_bp)

# Serve bundled Highslide assets from the project `highslide/` directory.
# This keeps the original vendor files where they are but makes them
# available under the URL path `/highslide/...` so templates can load them.
HS_DIR = os.path.join(os.path.dirname(__file__), 'highslide')


@app.route('/highslide/<path:filename>')
def highslide_static(filename):
    return send_from_directory(HS_DIR, filename)

# --- User Routes (Unchanged) ---
@app.route('/')
def home():
    from flask import session, redirect, url_for
    if session.get('IFLOGED_IN') or session.get('user_id'):
        return redirect(url_for('menu.show_menu'))
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5056, debug=True)
