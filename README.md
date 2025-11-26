# Main Menu Application v1.0

This is a simple, clean, and secure web-based main menu application built with Python and the Flask web framework. It allows multiple users to register, log in, and access various menu items.

This project is built using modern, modular, and secure coding practices.

## Features

-   **Multi-User Support:** Each user has a separate, secure login and can only see and manage their own contacts.
-   **Secure Password Storage:** User passwords are not stored in plaintext. They are securely hashed using modern cryptographic standards (`werkzeug.security`).
-   **Full CRUD Functionality:** Users can **C**reate, **R**ead, **U**pdate, and **D**elete their contacts through a clean web interface.
-   **Role-Based Menu Access:** Menu items can be restricted by user level. Higher-level users see more options; lower-level users see only items appropriate to their access level.
-   **Modular, Robust Backend:** The application is built on a modular design, separating the web routes (in `app.py`) from the application logic (in `MainMenu.py`).
-   **Centralized Database Management:** Uses a global `MySql.py` module for all database connections, ensuring reliable database operations.

## Requirements

1.  A Linux system with Python 3 and `pip`.
2.  A working MySQL/MariaDB server.
3.  The `werkzeug` and `flask` Python libraries (installation is handled by the installer).

## Installation

1.  Download or clone this project to a directory on your server (e.g., `~/projects/mainmenu`).
2.  Navigate into the project directory: `cd ~/projects/mainmenu`
3.  **Database Setup:** Before running the app, you must create the database and tables. An SQL script is provided to do this automatically.
    *   First, ensure your MySQL database is properly configured.
    *   Then, update the `config.py` file with the correct database name and your credentials.
    *   Ensure that /home/$USER/.my.cnf contains your MySQL credentials.
    *   Finally, import the provided schema file:
        ```bash
        mysql --defaults-file=/home/$USER/.my.cnf als < mainmenu_schema.sql
        ```
4.  **Install Python Dependencies:** A `requirements.txt` file is included. Install the necessary libraries with pip:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file containing `Flask`, `PyMySQL`, and `Werkzeug`)*

## Running the Application

### For Development / Testing:

You can run the application directly using Python. This will start the built-in Flask development server.

```bash
cd ~/projects/mainmenu
python3 ./app.py
```

## User Levels and Menu Access

The application supports **role-based access control** via user levels. Each menu item in the `siteslinks` table has a `level` field that determines the minimum user level required to view that item.

### Level Hierarchy

- **Level 0:** Anonymous users (not logged in). See no menu items.
- **Level 1:** Default registered users. See public menu items (galleries, book library, address book, etc.).
- **Level 3:** Admin/power users. See all menu items including admin tools (Media Library, Blog, File Browser, GeminiAI, Admin).

### How It Works

1. When a user logs in, their `level` is retrieved from the `users` table and stored in the Flask session (`session['level']`).
2. When the menu page (`/menu`) is rendered, `menu_view.py` filters the `siteslinks` table to show only items where `level <= user_level`.
3. This filtering happens **server-side** in Python, preventing client-side bypasses.

### Managing User Levels

#### Setting a User's Level

Users are created with `level=1` by default via the registration form. To change a user's level:

```sql
-- Grant admin privileges (level 3) to a user
UPDATE users SET level = 3 WHERE username = 'dee';

-- Revoke admin privileges (set back to level 1)
UPDATE users SET level = 1 WHERE username = 'dee';
```

#### Changing a Menu Item's Required Level

Edit the `siteslinks` table:

```sql
-- Restrict an item to level 3 only (admin item)
UPDATE siteslinks SET level = 3 WHERE title = 'My Media Library';

-- Make an item public (level 1)
UPDATE siteslinks SET level = 1 WHERE title = 'My Book Library';
```

### Database Schema Notes

- `users.level`: TINYINT field storing the user's access level (default 1).
- `siteslinks.level`: VARCHAR field storing the required level for each menu item (should be normalized to TINYINT using `db_migrations/normalize_siteslinks_levels.sql`).

### Future Enhancements

- Role-based groups (e.g., "Admin", "Editor", "Viewer") instead of numeric levels.
- Permission-based access (fine-grained control over specific features).
- Audit logging to track who accessed what and when.

---

## Session Authentication Integration for Other Apps

The mainmenu app serves as the **central authentication server** for all Flask applications in the workspace. Other apps can share the same login session across different subdomains using a reusable session authentication module.

### How It Works

1. **Mainmenu** handles user login and creates a session cookie
2. The session cookie is shared across all `*.your.domain` subdomains
3. Other apps import the `session_auth_check` module to verify authentication
4. All apps use the **same secret key** and **cookie configuration** to decrypt the session

### Adding Session Authentication to Your App

Follow these steps to integrate session authentication into any Flask app:

#### Step 1: Import the Session Check Module

Add these imports to the top of your `app.py`:

```python
from flask import Flask, render_template, redirect
import sys
sys.path.append('/home/$USER/projects')
from session_auth_check import is_logged_in, get_auth_status
```

#### Step 2: Set the Shared Secret Key

**Critical:** All apps MUST use the same secret key as mainmenu:

```python
app = Flask(__name__)
app.secret_key = 'my22kids'  # MUST match mainmenu's SECRET_KEY
```

#### Step 3: Configure Session Cookie for Cross-Domain Sharing

Add this configuration immediately after creating the Flask app:

```python
# Session configuration for cross-subdomain authentication
app.config['SESSION_COOKIE_NAME'] = 'shared_session'
app.config['SESSION_COOKIE_DOMAIN'] = '.your.domain'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # False for HTTP, True for HTTPS
```

**Important Settings:**
- `SESSION_COOKIE_NAME`: Must be `'shared_session'` (same for all apps)
- `SESSION_COOKIE_DOMAIN`: Must be `'.your.domain'` (note the leading dot)
- `SESSION_COOKIE_SECURE`: Set to `False` for HTTP, `True` for HTTPS only

#### Step 4: Protect Your Routes

Add authentication checks to your routes:

```python
@app.route('/')
def index():
    # Check authentication status (GO/NOGO)
    if not is_logged_in():
        # NOGO - Not logged in, redirect to login after 5 seconds
        return f"""
        <html>
        <head>
            <title>Your App - Not Logged In</title>
            <meta http-equiv="refresh" content="5;url=http://login.your.domain/login">
        </head>
        <body>
            <div style="background-color: #f8d7da; color: #721c24; padding: 20px; 
                        border: 1px solid #f5c6cb; margin: 20px; text-align: center;">
                <h2>✗ NOT LOGGED IN</h2>
                <p>This application requires authentication to access.</p>
                <p>Redirecting to login page in 5 seconds...</p>
            </div>
        </body>
        </html>
        """
    
    # GO - User is authenticated, run normal app logic
    return render_template('index.html')
```

For immediate redirects (no delay):

```python
@app.route('/player/<int:item_id>')
def player(item_id):
    # Check authentication (GO/NOGO)
    if not is_logged_in():
        return redirect('http://login.your.domain/login')
    
    # GO - User authenticated
    return render_template('player.html', item_id=item_id)
```

#### Step 5: Restart and Test

1. Save your modified `app.py`
2. Restart your Flask application
3. Clear browser cookies for `your.domain` (if testing)
4. Login via mainmenu at `http://login.your.domain/login`
5. Access your app - it should recognize the session

### Authentication Functions

#### `is_logged_in()`
Returns boolean GO/NOGO status.

```python
if is_logged_in():
    # User is authenticated (GO)
    return show_content()
else:
    # User is not authenticated (NOGO)
    return redirect_to_login()
```

#### `get_auth_status()`
Returns detailed authentication information as a dictionary:

```python
auth = get_auth_status()
# Returns:
# {
#     'authenticated': True/False,
#     'user_id': 7,
#     'username': 'al',
#     'level': 3
# }
```

### Troubleshooting

**Problem:** App shows "NOT LOGGED IN" even after logging in.

**Solutions:**
1. Verify `app.secret_key` matches mainmenu's SECRET_KEY exactly
2. Check `SESSION_COOKIE_NAME = 'shared_session'` is set
3. Confirm `SESSION_COOKIE_DOMAIN = '.your.domain'` (note the leading dot)
4. Restart both mainmenu and your app
5. Clear browser cookies and login again
6. Verify accessing via `.your.domain` domain (not `localhost` or IP)
7. Check `SESSION_COOKIE_SECURE = False` if using HTTP

### Integration Checklist

- [ ] Add `session_auth_check` import
- [ ] Set `app.secret_key` to match mainmenu's SECRET_KEY
- [ ] Configure `SESSION_COOKIE_NAME = 'shared_session'`
- [ ] Configure `SESSION_COOKIE_DOMAIN = '.your.domain'`
- [ ] Set `SESSION_COOKIE_SECURE = False` (for HTTP)
- [ ] Add authentication check to main route
- [ ] Add redirect on NOGO with 5-second delay
- [ ] Protect sensitive routes with `is_logged_in()` checks
- [ ] Restart the application
- [ ] Test while logged out (should see redirect)
- [ ] Test while logged in (should work normally)

### Successfully Integrated Apps

- ✅ **mainmenu** - Authentication server (port 5056)
- ✅ **audio** - Audio player (port 5053)
- ✅ **mediaplayer** - Media player

### Additional Resources

- **Detailed Integration Guide:** `/home/$USER/projects/mainmenu/SESSION_AUTH_INTEGRATION_GUIDE.md`
- **Auth Module:** `/home/$USER/projects/session_auth_check.py`
- **Usage Examples:** `/home/$USER/projects/USAGE_EXAMPLE_session_auth_check.py`
- **Module Documentation:** `/home/$USER/projects/SESSION_AUTH_CHECK_README.md`
