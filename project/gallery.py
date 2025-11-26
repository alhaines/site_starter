from flask import Blueprint, render_template, current_app, send_from_directory, abort, url_for
import os
from PIL import Image
from werkzeug.utils import secure_filename

gallery_bp = Blueprint('gallery', __name__, url_prefix='/gallery')

# Config: path to gallery root relative to project
GALLERY_ROOT = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
THUMBS_DIR = os.path.join(GALLERY_ROOT, 'thumbs')

os.makedirs(THUMBS_DIR, exist_ok=True)

def list_galleries(db):
    # If you want to use the DB table:
    # return db.get_data("SELECT * FROM galleries WHERE public=1 ORDER BY id ASC")
    # For now example returns None (we'll wire DB in app)
    return None

def get_gallery_folder(slug):
    # safe folder path
    folder = os.path.join(GALLERY_ROOT, slug)
    if os.path.isdir(folder):
        return folder
    return None

def make_thumbnail(image_path, thumb_path, size=(240,240)):
    try:
        with Image.open(image_path) as im:
            im.thumbnail(size)
            im.save(thumb_path)
            return True
    except Exception as e:
        current_app.logger.exception("thumb failed: %s", e)
        return False

@gallery_bp.route('/')
def index():
    # Query the galleries table via app's db if desired
    db = current_app.config.get('DB')  # we'll set this in app.py after init
    galleries = []
    if db:
        galleries = db.get_data("SELECT id, title, slug, folder, description FROM galleries WHERE public=1 ORDER BY id ASC")
    return render_template('gallery_list.html', galleries=galleries)

@gallery_bp.route('/<slug>/')
def show_gallery(slug):
    folder = get_gallery_folder(slug)
    if not folder:
        abort(404)
    # list images (filter common image extensions)
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.jpg','.jpeg','.png','.gif','webp'))])
    # build thumb URLs, create thumbnails if missing
    thumbs = []
    for fname in files:
        src = os.path.join(folder, fname)
        thumb_name = f"{slug}__{fname}"
        thumb_path = os.path.join(THUMBS_DIR, thumb_name)
        if not os.path.exists(thumb_path):
            make_thumbnail(src, thumb_path)
        thumbs.append({
            'file': fname,
            'url': url_for('gallery.serve_image', slug=slug, filename=fname),
            'thumb_url': url_for('gallery.serve_thumb', filename=thumb_name)
        })
    return render_template('gallery_grid.html', slug=slug, images=thumbs, title=slug)

@gallery_bp.route('/<slug>/image/<path:filename>')
def serve_image(slug, filename):
    folder = get_gallery_folder(slug)
    if not folder:
        abort(404)
    # secure filename, avoid path traversal
    safe = secure_filename(filename)
    return send_from_directory(folder, safe)

@gallery_bp.route('/thumbs/<path:filename>')
def serve_thumb(filename):
    return send_from_directory(THUMBS_DIR, filename)
