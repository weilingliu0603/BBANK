import flask
import sqlite3
from flask import jsonify

app = flask.Flask(__name__)

@app.route("/")
def index():
       return flask.render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    data = flask.request.form
    Email = data["Email"]
    Password = data["Password"]
    
    connection = sqlite3.connect("BBANK.db")
    cursor = connection.execute("SELECT * FROM Customer WHERE Email = ? AND Password = ?", (Email, Password)).fetchall()

    connection.close()
    
    if len(cursor) == 1:
        results = [{'status': 'success', 'message': 'if any'}]
        
    else:
        results = [{'status': 'fail', 'message': 'if any'}]

    return jsonify(results) 


if __name__ == "__main__":
    app.run(port=6789,debug=True)
