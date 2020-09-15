# src/views/upload.py
from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, current_app)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from src.views.auth import login_required
from src.db import get_db
import os
import urllib.request
from src.fingerprint import gen_W, gen_fp, fp2text, text2fp
from src.validation import validate
import cv2

upload = Blueprint('upload', __name__)

#image serving
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload.route('/') #default structure just shows "the timeline"
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, image, body, created, cred, fingerprint, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index.html', posts=posts)

@upload.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == "POST":

        #Additional posting options BOOLEAN FLAGs
        post_option = request.form.get('post_option')
        if post_option is None:
            post_option = "None"

        #image upload
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image = filename #record proper information
            img_src = cv2.imread('src/static/images/'+filename)
            img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)

        body = request.form['body']

        #automatically generated
        cred = "Source: " + g.user['username']
        fingerprint = fp2text(gen_fp(img_src, 100, 1))

        error = None

        if not body:
            error = "Post requires text."

        #VALIDATION
        db = get_db()
        ticket = validate(text2fp(fingerprint), g.user['id'], db)
        if not bool(ticket[0]):
            error = ticket[1]

        if ticket[0] == "sponsor":
            error = None
            post_option = "sponsor"

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (author_id, image, body, cred, fingerprint, post_type)' #post_type: 'sponsor'
                ' VALUES (?,?,?,?,?,?)',
                (g.user['id'], image, body, cred, fingerprint, post_option)
            )
            db.commit()
            return redirect(url_for('upload.index'))

    return render_template('create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, author_id, image, created, body, cred, fingerprint, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@upload.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":

        body = request.form['body']
        error = None

        if not body:
            error = "Post requires text."

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'UPDATE post SET body = ?'
                ' WHERE id = ?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('upload.index'))

    return render_template('update.html', post=post)

@upload.route('/<int:id>/delete', methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('upload.index'))

@upload.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)
