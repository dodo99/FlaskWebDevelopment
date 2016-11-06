"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
import os
from threading import Thread


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:3622@localhost:5432/flaskwebdev'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USERNAME'] = 'tonyltang'
app.config['MAIL_PASSWORD'] = 'tt4853622'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
#app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_ADMIN'] = 'tonyltang'


manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender = app.config['FLASKY_MAIL_SENDER'],
                  recipients= [to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target = send_async_email, args = [app, msg])
    thr.start()
    return thr


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],
                           'New User',
                           'mail/new_user',
                           user = user)
        else:
            session['known']= True

        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',
                           form = form,
                           name = session.get('name'),
                           known = session.get('known', False))

#@app.route('/user/<name>')
#def user(name):
#    return render_template('user.html', name=name)

if __name__ == '__main__':
    #import os
    #HOST = os.environ.get('SERVER_HOST', 'localhost')
    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5555'))
    #except ValueError:
    #    PORT = 5555
    #app.run(HOST, PORT)

    # this will run at http://localhost:5000
    #app.run(debug=True)

    #run from the virtual environment as .\env\Scripts\python.exe manage.py runserver --host 127.0.0.1
    manager.run()