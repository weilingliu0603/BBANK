import flask
import sqlite3
from flask import jsonify
import datetime as dt

app = flask.Flask(__name__)

@app.route("/")
def index():
       return flask.render_template("index.html")

#register user

@app.route("/login", methods = ["POST"])
def login(): 
    data = flask.request.form
    Email = data["Email"]
    Password = data["Password"]
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT * FROM Customer WHERE Email = ? AND Password = ?", (Email, Password)).fetchall()

    connection.close()
    
    if len(cursor) == 1:
        results = [{'status': 'success', 'message': 'if any'}]
        
    else:
        results = [{'status': 'fail', 'message': 'if any'}]

    return jsonify(results) 

#retrieve all saving accounts transactions
@app.route("/accounts_transactions/<Email>")
def accounts_transactions(Email): 
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CustomerID FROM Customer WHERE Email = ? ", (Email,)).fetchall()

    CustomerID = cursor[0][0]

    cursor = connection.execute("SELECT AccountNumber FROM Account WHERE CustomerID = ? AND AccountType = ?", (CustomerID, "Savings")).fetchall()

    dic = {}
    for account in cursor:
           dic[account[0]] = []
       
    for AccountNumber in dic:
           cursor = connection.execute("SELECT Date, Time, Amount, Description FROM AccountTransaction WHERE AccountNumber = ? ", (AccountNumber,)).fetchall()
           for record in cursor:
                  dic[AccountNumber].append(record)
    
    return jsonify(dic)

#retrieve transactions of one saving account

#retrieve all credit card transactions
@app.route("/cards_transactions/<Email>")
def cards_transactions(Email): 
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CustomerID FROM Customer WHERE Email = ? ", (Email,)).fetchall()

    CustomerID = cursor[0][0]

    cursor = connection.execute("SELECT CardNumber FROM CreditCard WHERE CustomerID = ? ", (CustomerID,)).fetchall()

    dic = {}
    for account in cursor:
           dic[account[0]] = []
       
    for CardNumber in dic:
           cursor = connection.execute("SELECT Date, Time, Amount, Category FROM CreditCardTransaction WHERE CardNumber = ? ", (CardNumber,)).fetchall()
           for record in cursor:
                  dic[CardNumber].append(record)
    
    return jsonify(dic)     

#retrieve credit card transactions of one card
@app.route("/card_transactions/<CardNumber>")
def card_transactions(CardNumber):
    dic = {CardNumber:[]}
    connection = sqlite3.connect("BBOOK.db")

    cursor = connection.execute("SELECT Date, Time, Amount, Category FROM CreditCardTransaction WHERE CardNumber = ? ", (CardNumber,)).fetchall()
    for record in cursor:
           dic[CardNumber].append(record)
    
    return jsonify(dic)

#retrieve info of each credit card (incl amount due)

#pay credit card amount due

#retrieve total monthly spending (credit cards)

#retrieve monthly spending by category (credit cards)

#transfer funds


if __name__ == "__main__":
    app.run(port=6789,debug=True)
