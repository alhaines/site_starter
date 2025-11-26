# Site Starter - Flask Multi-User Web Application Template

A complete, production-ready Flask application template for building a multi-user website with authentication, role-based access control, and modular design.

## Features

- **Multi-User Authentication:** Secure user registration and login with password hashing
- **Role-Based Access Control:** 3-tier user levels (1=User, 2=Power User, 3=Admin)
- **Cross-Subdomain Sessions:** Single sign-on across multiple subdomains (*.your_domain)
- **Dynamic Menu System:** Database-driven menu with level-based filtering
- **Photo Galleries:** Built-in photo gallery system with automatic thumbnail generation
- **Modular Architecture:** Clean separation of concerns with Flask Blueprints
- **Production Ready:** Includes systemd service file for deployment with Gunicorn

## Quick Start

### Prerequisites

- Linux server with Python 3.7+
- MySQL/MariaDB database server
- Python `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   cd ~/projects
   git clone <your-repo-url> site_starter
   cd site_starter/project
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure the application:**
   ```bash
   cp config.sample.py config.py
   nano config.py
   ```
   
   Update the following in `config.py`:
   - MySQL credentials (host, user, password, database)
   - SECRET_KEY (generate with: `python3 -c "import os; print(os.urandom(24).hex())"`)

4. **Update domain references:**
   
   Replace `your_domain` with your actual domain in:
   - `app.py`: SESSION_COOKIE_DOMAIN
   - `auth.py`: Login redirect URL
   
   Replace `/home/your_user` with your actual home directory in:
   - `app.py`: sys.path.append line
   - `../login.service`: All paths

5. **Set up the database:**
   ```bash
   mysql --defaults-file=/home/your_user/.my.cnf your_database < ../siteslinks.sample.sql
   ```
   
   Or manually create the `siteslinks` table and import the sample data.

6. **Create the users table:**
   
   Create a `users` table in your database with this structure:
   ```sql
   CREATE TABLE `users` (
     `id` int(11) NOT NULL AUTO_INCREMENT,
     `username` varchar(50) NOT NULL UNIQUE,
     `password_hash` varchar(255) NOT NULL,
     `firstname` varchar(100) DEFAULT NULL,
     `lastname` varchar(100) DEFAULT NULL,
     `address` varchar(255) DEFAULT NULL,
     `city` varchar(100) DEFAULT NULL,
     `state` varchar(50) DEFAULT NULL,
     `zipcode` varchar(20) DEFAULT NULL,
     `birthday` date DEFAULT NULL,
     `email` varchar(100) DEFAULT NULL,
     `phone1` varchar(20) DEFAULT NULL,
     `phone2` varchar(20) DEFAULT NULL,
     `comment` text DEFAULT NULL,
     `level` tinyint(4) DEFAULT 1,
     PRIMARY KEY (`id`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
   ```

7. **Run the development server:**
   ```bash
   python3 app.py
   ```
   
   Access the application at `http://localhost:5056`

### Production Deployment

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Configure the systemd service:**
   ```bash
   sudo cp ../login.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable login.service
   sudo systemctl start login.service
   ```

3. **Check service status:**
   ```bash
   sudo systemctl status login.service
   ```

4. **Configure reverse proxy (nginx/Apache):**
   
   Set up a reverse proxy to forward requests from your domain to port 5056.
   
   Example nginx config:
   ```nginx
   server {
       listen 80;
       server_name login.your_domain;
       
       location / {
           proxy_pass http://127.0.0.1:5056;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Project Structure

```
site_starter/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── login.service               # Systemd service file
├── siteslinks.sample.sql       # Sample menu links database
└── project/                    # Main application directory
    ├── app.py                  # Flask application entry point
    ├── config.sample.py        # Configuration template
    ├── MySql.py                # Database connection wrapper
    ├── auth.py                 # Authentication blueprint
    ├── auth_api.py             # Authentication API for other apps
    ├── menu.py                 # Menu generator class
    ├── menu_view.py            # Menu view blueprint
    ├── gallery.py              # Photo gallery blueprint
    ├── templates/              # HTML templates
    │   ├── login.html
    │   ├── register.html
    │   ├── menu.html
    │   ├── gallery_list.html
    │   └── gallery_grid.html
    └── static/                 # Static assets (CSS, JS, images)
        ├── styles.css
        └── gallery/            # Gallery photos
```

## User Levels

The application supports 3 user access levels:

- **Level 1 (User):** Default registered users. See public menu items.
- **Level 2 (Power User):** Advanced users with access to additional features.
- **Level 3 (Admin):** Full access to all menu items including admin tools.

### Managing User Levels

```sql
-- Grant admin privileges (level 3)
UPDATE users SET level = 3 WHERE username = 'admin_user';

-- Set power user (level 2)
UPDATE users SET level = 2 WHERE username = 'power_user';

-- Set regular user (level 1)
UPDATE users SET level = 1 WHERE username = 'regular_user';
```

### Managing Menu Item Access

```sql
-- Restrict menu item to admins only
UPDATE siteslinks SET level = 3 WHERE title = 'Admin Panel';

-- Make menu item available to power users and above
UPDATE siteslinks SET level = 2 WHERE title = 'My Blog';

-- Make menu item public (all registered users)
UPDATE siteslinks SET level = 1 WHERE title = 'Photo Gallery';
```

## Cross-Subdomain Authentication

The application supports single sign-on across multiple subdomains using shared session cookies.

### Configuration

All apps using the shared authentication must:

1. Use the **same SECRET_KEY**
2. Use the **same SESSION_COOKIE_NAME** (default: 'your_session')
3. Use the **same SESSION_COOKIE_DOMAIN** (e.g., '.your_domain')

See the main README in `project/` for detailed integration instructions.

## Customization

### Adding Menu Items

Insert new items into the `siteslinks` table:

```sql
INSERT INTO siteslinks (title, link, level, comment) 
VALUES ('New Feature', 'http://feature.your_domain', 1, 'A new feature');
```

### Creating Photo Galleries

1. Create a new folder in `static/gallery/`:
   ```bash
   mkdir -p project/static/gallery/my_photos
   ```

2. Add images to the folder

3. Add gallery entry to database (if using DB-driven gallery list):
   ```sql
   INSERT INTO galleries (title, slug, folder, description, public)
   VALUES ('My Photos', 'my_photos', 'my_photos', 'My photo collection', 1);
   ```

4. Access at: `http://login.your_domain/gallery/my_photos/`

### Adding New Routes

Create a new blueprint in a separate file:

```python
from flask import Blueprint, render_template

my_bp = Blueprint('my_feature', __name__)

@my_bp.route('/my-route')
def my_route():
    return render_template('my_template.html')
```

Register it in `app.py`:

```python
from my_feature import my_bp
app.register_blueprint(my_bp)
```

## Security Notes

- **Change the SECRET_KEY** before deploying to production
- Use **HTTPS in production** (set SESSION_COOKIE_SECURE=True)
- Store database credentials securely (use environment variables or `.my.cnf`)
- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Enable firewall rules to restrict database access
- Use strong passwords for user accounts

## Troubleshooting

### "ModuleNotFoundError: No module named 'config'"

Make sure you copied `config.sample.py` to `config.py` and updated it with your credentials.

### "Access denied for user"

Check your MySQL credentials in `config.py`. Ensure the database user has proper permissions.

### Session not working across subdomains

1. Verify SESSION_COOKIE_DOMAIN starts with a dot (`.your_domain`)
2. Ensure all apps use the same SECRET_KEY
3. Check that SESSION_COOKIE_NAME is identical across apps
4. Clear browser cookies and try again

### Service fails to start

```bash
# Check service logs
sudo journalctl -u login.service -n 50

# Check permissions
ls -l /home/your_user/projects/site_starter/project

# Verify Python path
which gunicorn
```

## Contributing

This is a template repository. Feel free to fork and customize for your needs.

## License

This project is provided as-is for educational and personal use.

## Support

For issues and questions, please create an issue in the repository.
