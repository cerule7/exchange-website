#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from pymongo import MongoClient
from alg import *

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
app.config['BASIC_AUTH_USERNAME'] = 'langadmin'
app.config['BASIC_AUTH_PASSWORD'] = 'rutgers4'

basic_auth = BasicAuth(app)

#open mongodb connection
client = MongoClient("mongodb+srv://admin:rutgers1@studentinfo-eoita.azure.mongodb.net/test?retryWrites=true")
db = client.test

#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST': #successful form post
        results = request.get_json()
        db.inventory.insert(results) #load form results into mongodb
        update()
    return render_template('pages/register.html')

@app.route('/view_students', methods=['GET', 'PUT'])
@basic_auth.required
def students():
    if request.method == 'PUT':
        results = request.get_json()
        header = results.pop(0)
        if header['status'] == 'remove':
            for r in results:
                db.inventory.update(
                   {"name": r['name']},
                   {"$set": {"partner": "None"}}
                )
        if header['status'] == 'correct':
            for r in results:
                db.inventory.update(
                   {"name": r['name']},
                   {"$set": {"placement": "Correct"}}
                )
        if header['status'] == 'incorrect':
            for r in results:
                db.inventory.update(
                   {"name": r['name']},
                   {"$set": {"placement": "Incorrect"}}
                )
        if header['status'] == 'delete':
            for r in results:
                db.inventory.delete_one(
                   {"name": r['name']}
                )
    update()
    rows = db.inventory.find({})
    rowslist = []
    for r in rows:
        llist = [r['ll1'], r['ll2'], r['ll3']]
        llist[:] =  [x for x in llist if x != 'None']
        llist.sort()
        slist = [r['sl1'], r['sl2'], r['sl3']]
        slist[:] =  [x for x in slist if x != 'None']
        slist.sort()
        student = {
        'name': r['name'],
        'year': r['year'],
        'ruid': r['ruid'],
        'learn_langs': make_string(llist),
        'share_langs': make_string(slist),
        'partner': r['partner'],
        'placement': r['placement']
        }
        rowslist.append(student)
    return render_template('pages/students.html', rows=rowslist)

def make_string(langs):
    res = ''
    for i in range(len(langs)):
        if(i + 1 < len(langs)):
            res += langs[i] + ', '
        else:
            res += langs[i]
    return res

@app.route('/make_pairs', methods=['POST', 'GET'])
@basic_auth.required
def make():
    if request.method == 'POST':
        results = request.get_json()
        for r in results:
            names = r['names'].split('&')
            s1 = names[0][:(len(names[0])-1)]
            s2 = names[1][1:]
            db.inventory.update(
               {"name": s1},
               {"$set": {"partner": s2}}
            )
            db.inventory.update(
               {"name": s2},
               {"$set": {"partner": s1}}
            )
    pairlist = []
    pairs = make_pairs()
    for pair in pairs:
        langs = pair.language1 + " & " + pair.language2
        names = pair.student1.name + " & " + pair.student2.name
        p = {
            'languages' : langs,
            'names' : names
        }
        pairlist.append(p)
    return render_template('pages/pairs.html', pairs=pairlist)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)

@app.route('/login', methods=['GET'])
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

def update():
    db.inventory.update_many(
    {"$or" : [
    {"ll2": {"$exists": False}},
    {"ll2": None},
    ]},
    {"$set": {"ll2": "None", "lp2": "None", "ll3": "None", "lp3": "None"}}
    )

    db.inventory.update_many(
    {"$or" : [
    {"ll3": {"$exists": False}},
    {"ll3": None},
    ]},
    {"$set": {"ll3": "None", "lp3": "None"}}
    )

    db.inventory.update_many(
    {"$or" : [
    {"sl2": {"$exists": False}},
    {"sl2": None},
    ]},
    {"$set": {"sl2": "None", "sp2": "None", "sl3": "None", "sp3": "None"}}
    )

    db.inventory.update_many(
    {"$or" : [
    {"sl3": {"$exists": False}},
    {"sl3": None},
    ]},
    {"$set": {"sl3": "None", "sp3": "None"}}
    )

    db.inventory.update_many(
    {"$or" : [
        {"partner": {"$exists": False}},
        {"partner": None},
    ]},
    {"$set": {"partner": "None"}}
    )

    db.inventory.update_many(
    {"$or" : [
        {"rate1": {"$exists": False}},
        {"rate1": None},
    ]},
    {"$set": {"rate1": "3"}}
    )

    db.inventory.update_many(
    {"$or" : [
        {"rate2": {"$exists": False}},
        {"rate2": None},
    ]},
    {"$set": {"rate2": "3"}}
    )

    db.inventory.update_many(
    {"$or" : [
        {"placement": {"$exists": False}},
        {"placement": None},
    ]},
    {"$set": {"placement": "Unverified"}}
    )

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
