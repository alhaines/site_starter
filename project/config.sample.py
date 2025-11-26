#
# filename: /home/your_user/projects/site_starter/project/config.py
#

# Configuration for MainMenu application
mysql_config = {
    'host': 'localhost',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'your_database'
}

# A secret key is required for Flask sessions
# IMPORTANT: Change this to a random string for production!
# You can generate one with: python3 -c "import os; print(os.urandom(24).hex())"
SECRET_KEY = 'change_this_to_a_random_secret_key'
