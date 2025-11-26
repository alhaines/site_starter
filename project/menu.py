#!/usr/bin/python3 
# -*- coding: utf-8 -*-

#  Copyright 2025 AL Haines <alfredhaines@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  filename:  menu.py
#  This program generates an HTML menu of links from a MySQL database.

import pymysql
import config  # Import MySQL credentials
import sys      # For error output to browser

class LinkMenuGenerator:
    """
    Generates an HTML menu of links from the siteslinks MySQL table.
    """

    def __init__(self):
        self.db_config = config.mysql_config  # Get database config
        self.links = []
        # Serve the app's stylesheet from Flask's static endpoint
        # Use an absolute path so the menu works when served at /menu
        self.css_file = "/static/styles.css"
        self.page_title = "Haines Family Home"

    def connect_to_db(self):
        """Connects to the MySQL database."""
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except pymysql.MySQLError as e:
            # Don't exit the whole process from a request handler — return None
            # and let the caller handle the failure gracefully.
            sys.stderr.write(f"Error connecting to MySQL: {e}\n")
            return None

    def fetch_links(self):
        """Fetches links from the siteslinks table."""
        connection = self.connect_to_db()
        if not connection:
            # leave self.links as empty list if DB can't be reached
            self.links = []
            return

        try:
            cursor = connection.cursor()
            # include the 'level' column so callers can filter by required level
            cursor.execute("SELECT title, link, comment, level FROM siteslinks")
            self.links = cursor.fetchall()
            cursor.close()
        except pymysql.MySQLError as e:
            sys.stderr.write(f"Error fetching links: {e}\n")
            self.links = []
        finally:
            try:
                connection.close()
            except Exception:
                pass

    def generate_html(self):
        """Generates the HTML page with links."""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.page_title}</title>
    <link rel="stylesheet" href="{self.css_file}">
</head>
<body>
    <h1>{self.page_title}</h1>
    <div class="link-container">
"""

        for title, link, comment in self.links:
            html += f"""
        <a href="{link}" title="{comment}">{title}</a><br>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def run(self):
        """
        Main method to fetch links and print the HTML output.
        This method adheres to the "one print statement" requirement.
        """
        self.fetch_links()
        if self.links:
            print("Content-Type: text/html")  # Crucial for web output
            print()
            print(self.generate_html())
        else:
            print("Content-Type: text/plain")
            print()
            print("Could not retrieve links from the database.")
            print("Failed to retrieve links. Check the database connection.")


if __name__ == "__main__":
    menu_generator = LinkMenuGenerator()
    menu_generator.run()
