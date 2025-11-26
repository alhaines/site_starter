
from flask import Blueprint, render_template, current_app, url_for, session, Response, request
from menu import LinkMenuGenerator

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/menu')
def show_menu():
    # Render the menu with robust error handling so DB issues don't cause a 500
    gen = LinkMenuGenerator()
    try:
        gen.fetch_links()
    except Exception as e:
        # Log and continue with an empty link list
        current_app.logger.exception('Error fetching menu links: %s', e)
        gen.links = []

    # Filter links by the currently logged-in user's level.
    # Default anonymous level is 0 (not logged in). Registered users have
    # their level stored in session['level'] (set at login).
    user_level = 0
    try:
        user_level = int(session.get('level', 0) or 0)
    except Exception:
        user_level = 0

    safe_links = []
    for item in gen.links or []:
        try:
            # Extract fields and the link's required level. Support dict rows
            # (some DB wrappers return dict rows) or sequence rows (tuples).
            if isinstance(item, dict):
                title = item.get('title') or item.get('Title') or 'Untitled'
                link = item.get('link') or item.get('Link') or '#'
                comment = item.get('comment') or item.get('Comment') or ''
                raw_level = item.get('level')
            else:
                # Expected shape now: (title, link, comment, level)
                # But be permissive: fall back if level missing.
                if len(item) >= 4:
                    title, link, comment, raw_level = item[0], item[1], item[2], item[3]
                elif len(item) >= 3:
                    title, link, comment = item[0], item[1], item[2]
                    raw_level = None
                elif len(item) == 2:
                    title, link = item[0], item[1]
                    comment = ''
                    raw_level = None
                else:
                    title = str(item)
                    link = '#'
                    comment = ''
                    raw_level = None

            # Normalize required level to int. If missing or invalid, assume 1.
            try:
                link_level = int(raw_level) if raw_level is not None else 1
            except Exception:
                link_level = 1

            # Only include the link if the user's level is >= required level
            if user_level >= link_level:
                safe_links.append((title, link, comment))
        except Exception as e:
            # skip malformed rows but keep processing
            current_app.logger.warning('Skipping malformed menu row: %r, error: %s', item, e)
            continue

    return render_template('menu.html', links=safe_links, page_title=gen.page_title)


@menu_bp.route('/gm')
def show_gm():
    # Simple route to serve the local gamepad test page for the menu
    return render_template('gm.html')


@menu_bp.route('/drwho')
def show_drwho():
    """Run the legacy CGI-style `list_dr_who.py` and return its HTML output.

    We capture stdout from the script (it was written as a CGI) and strip the
    leading Content-Type header so Flask can return a proper response.
    """
    try:
        # Import the refactored renderer and call it directly
        import importlib
        if 'list_dr_who' in globals():
            importlib.reload(list_dr_who)
        else:
            list_dr_who = importlib.import_module('list_dr_who')

        output = list_dr_who.render_drwho()
        return Response(output, content_type='text/html')
    except Exception as e:
        current_app.logger.exception('Error executing list_dr_who.render_drwho: %s', e)
        return Response(f'<h1>Error</h1><p>{e}</p>', status=500, content_type='text/html')


@menu_bp.route('/shopping', methods=['GET', 'POST'])
def show_shopping():
    """Serve the shopping list via the refactored renderer."""
    try:
        import importlib
        if 'shopping_list' in globals():
            importlib.reload(shopping_list)
        else:
            shopping_list = importlib.import_module('shopping_list')

        output = shopping_list.render_shoppinglist(form=request.form, base_action='/shopping')
        return Response(output, content_type='text/html')
    except Exception as e:
        current_app.logger.exception('Error executing shopping_list.render_shoppinglist: %s', e)
        return Response(f'<h1>Error</h1><p>{e}</p>', status=500, content_type='text/html')
