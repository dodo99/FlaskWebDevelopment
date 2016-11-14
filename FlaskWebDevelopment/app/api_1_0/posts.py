#  HTTPie Example commands
#  GET command
#    .\env\Scripts\http --json --auth t@456.com:1111 GET http://127.0.0.1:5000/api/v1.0/posts/  (where 't@456.com' is the email address, '1111' is the password)
#  The same request can be issued by an anonymous user by sending an empty email and password as the following:
#    .\env\Scripts\http --json --auth : GET http://127.0.0.1:5000/api/v1.0/posts/
#  POST command
#    .\env\Scripts\http --auth t@456.com:1111 --json POST http://127.0.0.1:5000/api/v1.0/posts/ "body=I'm adding a post from the *command line*."
#  To use authentication tokens, a request to /api/v1.0/token is sent as follow:
#    .\env\Scripts\http --auth t@456.com:1111 --json GET http://127.0.0.1:5000/api/v1.0/token  
#    the returned result is like
#       {
#           "expiration": 3600,
#           "token": "eyJpYXQiOjEzODg4MjQ3MjcsImV4cCI6MTM4ODgyODMyNywiYWxnIjoiSFMy..."
#       }
#  And now the returned token can be used to make calls into the API for the next hour by passing it along with an empty password field as:
#    .\env\Scripts\http --json --auth eyJpYXQiOjE0NzkxMDIzODgsImV4cCI6MTQ3OTEwNTk4OCwiYWxnIjoiSFMyNTYifQ.eyJpZCI6N30.Ml4bLqXwB2smZ5gVjGjmuCFIwyQXA_jqwaNJrNbl7mo: GET http://127.0.0.1:5000/api/v1.0/posts/
#
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type = int)
    pagination = Post.query.paginate(
        page, 
        per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page = page - 1, _external = True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page = page + 1, _external = True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods = ['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id = post.id, _external = True)}


@api.route('/posts/<int:id>', methods = ['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
