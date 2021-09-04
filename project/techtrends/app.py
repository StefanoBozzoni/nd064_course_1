import logging
import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, session
from werkzeug.exceptions import abort
from flask.logging import default_handler

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    if not "counter" in session:
        session["counter"]=0
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    session["counter"]+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get posts count
def get_postCount():
    connection = get_db_connection()
    postCount = connection.execute('SELECT COUNT(*) AS PostCounter FROM posts').fetchone()
    connection.close()
    return postCount["PostCounter"]

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config.from_object(__name__)

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    
    if post is None:
      mylog("trying to access a non existing article")  
      return render_template('404.html'), 404
    else:
      mylog("existing article retrieved: %s"%(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    mylog("about page retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            mylog("article created: %s"%(title))
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healtz', methods=["GET"])
def healtcheck():
    response = app.response_class(
        response = json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/metrics', methods=["GET"])
def metrics():
    if not "counter" in session: 
        connectionsCount = 0
    else:
        connectionsCount = session["counter"]
    postsCount = get_postCount()
    response = app.response_class(
        response = json.dumps({"db_connection_count":connectionsCount, "post_count":postsCount}),
        status=200,
        mimetype='application/json'
    )
    mylog('metrics')
    return response  


def mylog(message):   
    logger.debug(" - "+ message)

# start the application on port 3111
if __name__ == "__main__":
   
   logger = logging.getLogger(__name__)
   logger.setLevel(logging.DEBUG)
   h1=logging.StreamHandler(sys.stdout)
   h1.setFormatter(logging.Formatter(fmt = '%(levelname)s:%(name)s:%(asctime)s - %(message)s',datefmt="%d/%b/%Y %H:%M:%S"))
   h2=logging.StreamHandler(sys.stderr)
   h2.setFormatter(logging.Formatter(fmt = '%(levelname)s:%(name)s:%(asctime)s - %(message)s',datefmt="%d/%b/%Y %H:%M:%S"))
   logger.handlers=[h1,h2] 

   log = logging.getLogger('werkzeug')
   handler = logging.StreamHandler(sys.stdout)
   handler.setFormatter(logging.Formatter(fmt = '%(levelname)s:%(name)s - %(message)s',datefmt="%d/%b/%Y %H:%M:%S"))
   log.setLevel(logging.DEBUG)
   log.addHandler(handler)
   #app.logger.removeHandler(default_handler)
   #app.logger.disabled = False
   
   app.run(host='0.0.0.0', port='3111', debug=True)

