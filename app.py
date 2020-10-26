import flask
import sqlite3
from flask import jsonify
from flask import request
import datetime as dt

app = flask.Flask(__name__)

@app.route("/")
def index():
       return flask.render_template("index.html")

#register user
@app.route("/registration") #set method to GET/POST
def registration(): 
##    data = flask.request.form
##    
##    Name = data["Name"]
##    Email = data["Email"]
##    Password = data["Password"]
##    Mobile = data["Mobile"]

    Name = "Liu Weiling"
    Email = "liu@gmail.com"
    Password = "liu123"
    Mobile = "98361234"

    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT * FROM Customer WHERE Email = ? ", (Email,)).fetchall()
    if len(cursor) > 0:
        results = [{'status': 'fail', 'message': 'email has been registered'}]
        connection.close()
        return jsonify(results)        
    else:
        results = [{'status': 'success', 'message': 'if any'}]
        cursor = connection.execute("SELECT seq FROM sqlite_sequence WHERE name = ? ", ("Customer",)).fetchall()
        nextID = int(cursor[0][0]) + 1
        
        cursor = connection.execute("INSERT INTO Customer VALUES (?,?,?,?,?)", (Name, Email, Password, Mobile, str(nextID)))
        connection.commit()
        connection.close()

        return jsonify(results)

#login
@app.route("/login", methods = ["POST"])
def login(): 
    #data = flask.request.form
    #Email = data["Email"]
    #Password = data["Password"]

    req_data = request.get_json()
    Email = req_data['Email']
    Password = req_data['Password']

    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CustomerID FROM Customer WHERE Email = ? AND Password = ?", (Email, Password)).fetchall()
    CustomerID = cursor[0][0]
    connection.close()
    
    if len(cursor) == 1:
        results = {'CustomerID': CustomerID, 'status': 'success', 'message': 'if any'}
        
    else:
        results = {'CustomerID''status': 'fail', 'message': 'if any'}

    return jsonify(results) 

#customer info
@app.route("/customer_info/<CustomerID>")
def customer_info(CustomerID):
       connection = sqlite3.connect("BBOOK.db")
       cursor = connection.execute("SELECT Name,Email,Mobile,ProfilePic FROM Customer WHERE CustomerID = ? ", (CustomerID,)).fetchall()
       Name = cursor[0][0]
       Email = cursor[0][1]
       Mobile = cursor[0][2]
       ProfilePic = cursor[0][3]
       cursor = connection.execute("SELECT SUM(Balance) FROM Account WHERE CustomerID = ? ", (CustomerID,)).fetchall()
       Deposit = cursor[0][0]
       cursor = connection.execute("SELECT SUM(AmountDue) FROM CreditCard WHERE CustomerID = ? ", (CustomerID,)).fetchall()
       Credit = cursor[0][0]
       connection.close()
       Bank = customer_banks(CustomerID)
       CreditCard = customer_creditcards(CustomerID)
       results = {'CreditCard': CreditCard, 'Bank': Bank, 'CustomerID': CustomerID, 'Name': Name, 'Email':Email, 'Mobile':Mobile, 'ProfilePic':ProfilePic, 'Deposit': Deposit, 'Credit': Credit}
       return results

#Return Customer BankAccounts
def customer_banks(CustomerID):
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Account.BankID,AccountType,AccountNumber,Balance,BankName FROM Account INNER JOIN BANK ON Account.BankID = BANK.BankID WHERE CustomerID = ? ", (CustomerID,)).fetchall()
    Bank = []
    for record in cursor:
           BankID = record[0]
           AccountType = record[1]
           AccountNumber = record[2]
           Balance = record[3]
           BankName = record[4]
           Bank.append({"BankID": BankID, "AccountType": AccountType, "AccountNumber": AccountNumber, "Balance": Balance, "BankName": BankName})
    return Bank

#Return Customer CreditCards
def customer_creditcards(CustomerID):
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CardID,CardNumber,CardType,ExpiryDate,CardName,AmountDue,BankName FROM CreditCard INNER JOIN BANK ON CreditCard.BankID = BANK.BankID WHERE CustomerID = ? ", (CustomerID,)).fetchall()
    CreditCard = []
    for record in cursor:
           CardID = record[0]
           CardNumber = record[1]
           CardType = record[2]
           ExpiryDate = record[3]
           CardName = record[4]
           AmountDue = record[5]
           BankName = record[6]
           CreditCard.append({"CardID": CardID, "CardNumber": CardNumber, "CardType": CardType, "ExpiryDate": ExpiryDate, "CardName": CardName, "AmountDue": AmountDue, "BankName": BankName})
    return CreditCard

#Transfer from Bank to Bank
@app.route("/bank_transfer", methods = ["POST"]) #set method to GET/POST
def bank_transfer(): 
##    data = flask.request.form
##    Sender = data["Account_Send"]
##    Receiver = data["Accound_Receive"]
##    Amount = data["Amount"]

    req_data = request.get_json()
    Sender = req_data['Sender']
    Receiver = req_data['Receiver']
    Amount = req_data['Amount']
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (Sender,)).fetchall()
    sender_balance = cursor[0][0]

    if sender_balance < Amount:
        results = {'status': 'fail', 'message': 'insufficient balance'}
        connection.close()
        return results         
    else:
        results = {'status': 'success', 'message': 'successfully transferred'}
        cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (Receiver,)).fetchall()
        receiver_balance = cursor[0][0]
    
        connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (sender_balance - Amount, Sender,))
        connection.commit()
        connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (receiver_balance + Amount, Receiver,))
        connection.commit()

    connection.close()
    return results 

#pay credit card amount due
@app.route("/pay_creditcard", methods = ["POST"]) #set method to GET/POST
def pay_creditcard(): 
##    data = flask.request.form
##    CardNumber = data["CardNumber"]
##    AccountNum = data["AccountNum"]
##    AmountPaid = data["AmountPaid"]

    req_data = request.get_json()
    BankAccount = req_data['BankAccount']
    CardNumber = req_data['CardNumber']
    PayAmount = req_data['PayAmount']
    
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Balance FROM Account WHERE AccountNumber = ? ", (BankAccount,)).fetchall()
    balance = cursor[0][0]

    cursor = connection.execute("SELECT AmountDue FROM CreditCard WHERE CardNumber = ? ", (CardNumber,)).fetchall()
    AmountDue = cursor[0][0]
    
    if balance < AmountDue:
        results = [{'status': 'fail', 'message': 'insufficient balance'}]
        connection.close()
        return jsonify(results)         
    else:
        results = [{'status': 'success', 'message': 'successfully paid'}]
        connection.execute("UPDATE Account SET Balance = ? WHERE AccountNumber = ? ", (balance - PayAmount, BankAccount,))
        connection.commit()
        newamount = AmountDue - PayAmount
        connection.execute("UPDATE CreditCard SET AmountDue = ? WHERE CardNumber = ? ", (newamount, CardNumber,))
        connection.commit()

    connection.close()
    return jsonify(results) 


#Returns list of QuickPayees
@app.route("/list_quickpay/<CustomerID>")
def list_quickpay(CustomerID):
       connection = sqlite3.connect("BBOOK.db")
       cursor = connection.execute("SELECT Customer.Name, Customer.ProfilePic, X.AccountNumber FROM QuickPay INNER JOIN Customer ON QuickPay.PayeeID = Customer.CustomerID INNER JOIN (Select CustomerID, AccountNumber from Account Where AccountType='Savings' Group by CustomerID) as X ON QuickPay.PayeeID = X.CustomerID Where QuickPay.CustomerID = ? ", (CustomerID,)).fetchall()
       connection.close()
       quickPayee = []
       for record in cursor:
           Name = record[0]
           ProfilePic = record[1]
           AccountNumber = record[2]
           quickPayee.append({"Name":Name, "ProfilePic":ProfilePic, "AccountNumber":AccountNumber})
       return jsonify(quickPayee)


#Retrieve Transactions By CardNumber
#@app.route("/get_cardtransactions/<CardNumber>")
def get_cardtransactions(CardNumber):
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT Date, Time, Amount, Category, Month FROM CreditCardTransaction WHERE CardNumber = ? ", (CardNumber,)).fetchall()
    connection.close()
    transactions = []
    for record in cursor:
           Date = record[0]
           Time = record[1]
           Amount = record[2]
           Category = record[3]
           Month = record[4]
           transactions.append({"Date":Date, "Time":Time, "Amount":Amount, "Category":Category, "Month":Month})
    return transactions

#Retrieve Credit Card Info including transactions
@app.route("/get_cardinfo/<CardNumber>")
def get_cardinfo(CardNumber):
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("SELECT CardNumber,CardType,ExpiryDate,CardName,AmountDue,BankName FROM CreditCard INNER JOIN BANK ON CreditCard.BankID = BANK.BankID Where CardNumber = ? ", (CardNumber,)).fetchall()
    connection.close()
    CardNumber = cursor[0][0]
    CardType = cursor[0][1]
    ExpiryDate = cursor[0][2]
    CardName = cursor[0][3]
    AmountDue = cursor[0][4]
    BankName = cursor[0][5]
    dic = {"CardNumber":CardNumber, "CardType":CardType, "ExpiryDate":ExpiryDate, "CardName":CardName, "AmountDue":AmountDue, "BankName":BankName, "Transactions":get_cardtransactions(CardNumber)}
    return dic

#Retrieve Spending Insights By Month
@app.route("/get_insights", methods = ["POST"])
def get_insights():
    req_data = request.get_json()
    CustomerID = req_data['CustomerID']
    Month = req_data['Month']
    connection = sqlite3.connect("BBOOK.db")
    cursor = connection.execute("select Category, Sum(amount) from CreditCardTransaction  where month = ? and CardNumber IN (Select CardNumber from CreditCard where CustomerID = ?) group by category", (Month,CustomerID,)).fetchall()

    Food = 0
    Bill = 0
    Medical = 0
    Shopping = 0
    Transport = 0
    Uncategorised = 0

    for record in cursor:
        if record[0] == 'Food & Drinks':
            Food += record[1]
        if record[0] == 'Bills & Utilites':
            Bill += record[1]
        if record[0] == 'Medical & Personal Care':
            Medical += record[1]
        if record[0] == 'Shopping':
            Shopping += record[1]
        if record[0] == 'Transport':
            Transport += record[1]
        if record[0] == 'Uncategorised':
            Uncategorised += record[1]

    return {"CustomerID": CustomerID, "Month": Month, "Food":round(Food,2), "Bill": round(Bill,2), "Medical":round(Medical,2), "Shopping":round(Shopping,2), "Transport":round(Transport,2), "Uncategorised":round(Uncategorised,2)}



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
    

if __name__ == "__main__":
    app.run(port=6789,debug=True)
