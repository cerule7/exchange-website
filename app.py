#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
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
    return render_template('pages/register.html')

@app.route('/view_students', methods=['POST', 'GET'])
def students():
    rows = db.inventory.find({})
    rowslist = []
    for r in rows:
        llist = r['ll1']
        if(r['ll2'] != 'None'):
            llist += ", " + r['ll2']
            if(r['ll3'] != 'None'):
                llist += ", " + r['ll3']
        slist = r['sl1']
        if(r['sl2'] != 'None'):
            slist += ", " + r['sl2']
            if(r['sl3'] != 'None'):
                slist += ", " + r['sl3']
        has_p = 'Yes'
        if(r['prevp'] == 'did_not'):
            has_p = 'No'
        student = {
        'name': r['name'],
        'year' : r['year'],
        'email': r['email'],
        'learn_langs': llist,
        'share_langs': slist,
        'prev_p': has_p
        }
        rowslist.append(student)
    return render_template('pages/students.html', rows=rowslist)

@app.route('/make_pairs', methods=['POST', 'GET'])
def make():
    if request.method == 'POST':
        print(request)
        names = request.split('&')
        s1 = names[0]
        s2 = names[1]
        db.inventory.update_one(
           {"name": s1},
           {"$set": {"partner": s2}}
        )
        db.inventory.update_one(
           {"name": s2},
           {"$set": {"partner": s1}}
        )
    return render_template('pages/pairs.html', pairs=make_pairs())

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


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
