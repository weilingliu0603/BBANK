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

#account details
@app.route("/account")
def account(): 
       return "Hello World"

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
@app.route("/account_transactions/<AccountNumber>")
def account_transactions(AccountNumber):
    dic = {AccountNumber:[]}
    connection = sqlite3.connect("BBOOK.db")

    cursor = connection.execute("SELECT Date, Time, Amount, Description FROM AccountTransaction WHERE AccountNumber = ? ", (AccountNumber,)).fetchall()
    for record in cursor:
           dic[AccountNumber].append(record)
    
    return jsonify(dic)

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
@app.route("/card_info/<CardNumber>")
def card_info(CardNumber):
    connection = sqlite3.connect("BBOOK.db")

    cursor = connection.execute("SELECT * FROM CreditCard WHERE CardNumber = ? ", (CardNumber,)).fetchall()
    cursor1 = connection.execute("SELECT Name FROM Customer WHERE CustomerID = ? ", (cursor[0][5],)).fetchall()


    dic = {"CardNumber":cursor[0][0], "Name":cursor1[0][0], "CardType":cursor[0][1], "ExpiryDate":cursor[0][3], "CardName":cursor[0][4], "AmountDue":cursor[0][6]}
    
    return jsonify(dic)


#retrieve historical total monthly spending (credit cards)
@app.route("/total_spending/<Email>")
def total_spending(Email):
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CustomerID FROM Customer WHERE Email = ? ", (Email,)).fetchall()

    CustomerID = cursor[0][0]

    cursor = connection.execute("SELECT CardNumber FROM CreditCard WHERE CustomerID = ? ", (CustomerID,)).fetchall()

    creditcards = []
    for record in cursor:
           creditcards.append(record)

    dic = {}

    for card in creditcards:
           if card not in dic:
                  dic[card[0]] = {}

           for card in dic:
                  cursor = connection.execute("SELECT Amount, Month FROM CreditCardTransaction WHERE CardNumber = ? ", (card,)).fetchall()
                  for record in cursor:
                         if record[1] not in dic[card]:
                                dic[card][record[1]] = record[0]
                         else:
                                dic[card][record[1]] += record[0]
                  
    return jsonify(dic)
       

#retrieve this month's spending by category (credit cards)
@app.route("/category_spending/<Email>")
def category_spending(Email):
    today = dt.datetime.now()
    month = today.month
    months = ["Jan","Feb","Mar","April","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    thismonth = months[month-1]
    
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CustomerID FROM Customer WHERE Email = ? ", (Email,)).fetchall()

    CustomerID = cursor[0][0]

    cursor = connection.execute("SELECT CardNumber FROM CreditCard WHERE CustomerID = ? ", (CustomerID,)).fetchall()

    creditcards = []
    for record in cursor:
           creditcards.append(record)

    dic = {}

    for card in creditcards:
           if card not in dic:
                  dic[card[0]] = {}

           for card in dic:
                  cursor = connection.execute("SELECT Amount, Category FROM CreditCardTransaction WHERE CardNumber = ? AND Month = ?", (card, thismonth)).fetchall()
                  for record in cursor:
                         if record[1] not in dic[card]:
                                dic[card][record[1]] = round(record[0],2)
                         else:
                                dic[card][record[1]] += round(record[0],2)
                  
    return jsonify(dic)
       
#pay credit card amount due
@app.route("/pay_cc") #set method to GET/POST
def pay_cc(): 
##    data = flask.request.form
##    CardNumber = data["CardNumber"]
##    AccountNum = data["AccountNum"]
##    AmountPaid = data["AmountPaid"]

    CardNumber = 4335666755550000 #to be removed, for testing only
    AccountNum = 123244500 #to be removed, for testing only
    AmountPaid = 500 #to be removed, for testing only
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (AccountNum,)).fetchall()
    balance = cursor[0][0]

    cursor = connection.execute("SELECT AmountDue FROM CreditCard WHERE CardNumber = ? ", (CardNumber,)).fetchall()
    AmountDue = cursor[0][0]
    
    if balance < AmountDue:
        results = [{'status': 'fail', 'message': 'if any'}]
        connection.close()
        return jsonify(results)         
    else:
        results = [{'status': 'success', 'message': 'if any'}]
        cursor = connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (balance - AmountPaid, AccountNum,)).fetchall()
        connection.commit()
        newamount = AmountDue + AmountPaid
        cursor = connection.execute("UPDATE CreditCard SET AmountDue = ? WHERE CardNumber = ? ", (newamount, CardNumber,)).fetchall()
        connection.commit()

    connection.close()

    return jsonify(results) 

#transfer funds
@app.route("/transfer_funds") #set method to GET/POST
def transfer_funds(): 
##    data = flask.request.form
##    Sender = data["Account_Send"]
##    Receiver = data["Accound_Receive"]
##    Amount = data["Amount"]

    Sender = 112244537 #to be removed, for testing only
    Receiver = 123244500 #to be removed, for testing only
    Amount = 500 #to be removed, for testing only
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (Sender,)).fetchall()
    sender_balance = cursor[0][0]

    if sender_balance < Amount:
        results = [{'status': 'fail', 'message': 'if any'}]
        connection.close()
        return jsonify(results)         
    else:
        results = [{'status': 'success', 'message': 'if any'}]
        cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (Receiver,)).fetchall()
        receiver_balance = cursor[0][0]
    
        connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (sender_balance - Amount, Sender,)).commit()
        connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (receiver_balance + Amount, Receiver,)).commit()

    connection.close()

    return jsonify(results) 

if __name__ == "__main__":
    app.run(port=6789,debug=True)
