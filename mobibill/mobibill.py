# coding: utf-8
from flask import Flask, render_template,session, redirect, url_for, escape, request
from twilio.rest import Client
import time
import requests,json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = 'npsmarketday@fullstackninjas.in'
PASSWORD ='Pokemon2345!'
app = Flask(__name__)


def sendMail(customer,mobile,billcontent,billno,emailaddress):
    messagetxt = '<html>'
    messagetxt = messagetxt + '<p><br><strong>Bill number </strong>' + billno
    messagetxt = messagetxt + '<br><strong>Customer name </strong>' + customer
    messagetxt = messagetxt + '<br><strong>Customer mobile number </strong>' + mobile
    messagetxt = messagetxt + billcontent + '</html>'
    server = smtplib.SMTP('mail.gandi.net', 587)
    server.ehlo()
    server.starttls() #and this method to begin encryption of messages
    server.login(MY_ADDRESS, PASSWORD)
    msg = MIMEMultipart()
    msg['From']=MY_ADDRESS  
    msg['To']=emailaddress
    msg['Subject']="E-bill for your purchase at Market Day of NPS, Rajajinagar"
    msg.attach(MIMEText(messagetxt, 'html'))
    server.sendmail(MY_ADDRESS,emailaddress,msg.as_string())
    del msg
    server.quit()

def saveBill(billno,billcontent,customer,mobile):
    file = open('bills/' + billno + '.txt','w')
    file.write('<p><br>')
    file.write('<strong>Bill number </strong>' + billno)
    file.write('<br>')
    file.write('<strong>Customer name </strong>' + customer)
    file.write('<br>')
    file.write('<strong>Customer mobile number </strong>' + mobile)
    file.write('<br>')
    file.write(billcontent)
    file.close()

def getbill(billnumber):
    file = open('bills/' + billnumber + '.txt','r')
    bill = file.read()
    file.close()
    return bill

def valid_login(usrname,passwd):
    app.logger.debug("Inside valid_login")
    login = False
    with open("database/uspass.txt") as f:
        for line in f:
            app.logger.debug(line)
            newline = str(line)
            data = newline.split()
            if usrname == data[0] and passwd == data[1]:
                login = True
    app.logger.debug(login)
    return login

def loadProducts(user):
    if 'username' in session:
        itemNames = []
        with open("database/"+ user + '.txt') as f:
            for line in f:
                newline = str(line)
                data = newline.split()
                itemNames.append(data[0])
        return itemNames
    return 

def loadPrice(user):
    if 'username' in session:
        itemPrices = []
        with open("database/" + user + '.txt') as f:
            for line in f:
                newline = str(line)
                data = newline.split()
                itemPrices.append(data[1])
        return itemPrices
    return

def loadClassPhone(user):
    app.logger.debug('inside load classphone for ' + user)
    if 'username' in session:
        phoneNumber = ''
        with open('database/uspass.txt') as f:
            for line in f:
                newline = str(line)
                data = newline.split()
                app.logger.debug(data[0])
                if user == data[0]:
                    app.logger.debug('user name matched')
                    app.logger.debug('phone number is ' + phoneNumber)
                    phoneNumber = data[2]
                    return phoneNumber
    return

def load_catalog(user):
    itemNames = []
    itemCost = []
    with open("database/" + user + '.txt') as f:
        for line in f:
            newline = str(line)
            data = newline.split()
            itemNames.append(data[0])
            #itemCost.append(data[1])
    app.logger.debug(itemNames)
    #app.logger.debug(itemCost)
    session['catalogName'] = itemNames
    #session['catalogCost'] = itemCost

def sendSMS(customer,mobile_no,cost,bill,billno):
    account_sid = "ACe45ceb3c20717267d83f6839c4ad744f"
    auth_token  = "be8753893236cb5b9b73acb56f271025"
    billCode = str(time.time())
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    to= "+91"+ mobile_no, 
    from_="+12486483593 ",
    body="Dear " + customer + ', you have purchased items worth Rs ' + cost + " .Detailed  bill: " + bill + " .Thank you for your support. We hope you like our products - Team " + session['username'])
    app.logger.debug("Buddi Old Tester")
    classPhone = loadClassPhone(session['username'])
    message = client.messages.create(
        to= "+91"+ classPhone,
        from_="+12486483593 ",
        body="The customer " + customer + " has purchased items worth Rs " + cost + ". Bill no is: " + billno
    )
    app.logger.debug("Buddi New Tester")


@app.route('/')
def hello_mobibill():
    return render_template('loginpage.html')

@app.route('/newdbill',methods=['POST','GET'])
def newdbill():
    if request.method == 'POST':
        app.logger.debug(request.form)
        totalcost = 0
        billcode = session['username'] + str(int(time.time()))
        app.logger.debug(billcode)
        billtext = 'Date ' + str(time.asctime( time.localtime(time.time()) )) + '\n'
        billHTML = '<p><strong>Detailed Bill<table><tr><th>Product</th><th>Cost</th><th>Quantity</th><th>Discount/Unit</th></tr>'
        billtext =  billtext + 'Product Cost Qty Discount/Unit'
        billtext =  billtext + '\n-----------------------------------'
        itemCount = int(request.form['itemCount'])
        app.logger.debug("Count is" + str(itemCount))
        for item in range(itemCount):
            itemName= request.form['Item_' + str(item)]
            itemCost= request.form['Price_' + str(item)]
            itemQty=  request.form['Qty_' + str(item)]
            itemDsc=  request.form['Dsc_' + str(item)]
            billtext = billtext + '\n' + itemName + ' ' + itemCost + ' '
            billHTML = billHTML + '<tr><td>' + itemName + '</td><td>' +  itemCost + '</td> '
            billtext = billtext + itemQty
            billHTML = billHTML + '<td>' + itemQty + '</td> '
            discount =  (int(itemQty)*int(itemDsc))
            billtext = billtext + ' ' + str(discount)
            billHTML = billHTML + '<td>' + str(discount) + '</td></tr>'
            totalcost = totalcost + (int(itemQty)*int(itemCost)) - discount
        billtext = billtext + '\n-----------------------------------\n'
        billtext = billtext + 'Total cost = Rs ' + str(totalcost)
        billHTML = billHTML + '</table><br>Total cost is Rs ' + str(totalcost) + '</p>'
        app.logger.debug(billtext)
        return render_template('confirmbill.html',mobile=request.form['mobile'],name=request.form['customer'],cost=totalcost,bill=billtext,bilhtml=billHTML,billnumber=billcode,email=request.form['email'])
        

@app.route('/newbill',methods=['POST','GET'])
def newbill():
    if request.method == 'POST':
        app.logger.debug(request)
        itemslist = []
        totalcost = 0
        totaldiscount = 0
        discount = 0
        app.logger.debug(session['catalogName'])
        itemslist = loadProducts(session['username'])
        itemsCost = loadPrice(session['username'])
        index = 0
        billcode = session['username'] + str(int(time.time()))
        app.logger.debug(billcode)
        billtext = 'Date ' + str(time.asctime( time.localtime(time.time()) )) + '\n'
        billHTML = '<p><strong>Detailed Bill<table><tr><th>Product</th><th>Cost</th><th>Quantity</th><th>Discount/Unit</th></tr>'
        billtext =  billtext + 'Product Cost Qty Discount/Unit'
        billtext =  billtext + '\n-----------------------------------'
        for it in itemslist:
            billtext = billtext + '\n' + it + ' ' + itemsCost[index] + ' '
            billHTML = billHTML + '<tr><td>' + it + '</td><td>' +  itemsCost[index] + '</td> '
            itemquantity = request.form[it]
            billtext = billtext + itemquantity
            billHTML = billHTML + '<td>' + itemquantity + '</td> '
            itemdiscount = request.form[it+'_discount']
            app.logger.debug(itemdiscount)
            discount =  (int(itemquantity)*int(itemdiscount))
            billtext = billtext + ' ' + str(discount)
            billHTML = billHTML + '<td>' + str(discount) + '</td></tr>'
            totalcost = totalcost + (int(itemquantity)*int(itemsCost[index])) - discount
            index = index + 1
            app.logger.debug(itemquantity)
        app.logger.debug(totalcost)
        billtext = billtext + '\n-----------------------------------\n'
        billtext = billtext + 'Total cost = Rs ' + str(totalcost)
        billHTML = billHTML + '</table><br>Total cost is Rs ' + str(totalcost) + '</p>'
        app.logger.debug(billtext)
        return render_template('confirmbill.html',mobile=request.form['mobile'],name=request.form['customer'],cost=totalcost,bill=billtext,bilhtml=billHTML,billnumber=billcode,email=request.form['email'])
    if 'username' in session:
        app.logger.debug('Logged in as %s' % escape(session['username']))
        return render_template('bill_layout.html',itemNames=loadProducts(session['username']),itemCost=loadPrice(session['username']))
    return 'You are not logged in'

@app.route('/confirmbill',methods=['POST','GET'])
def sendBill():
    if request.method == 'POST':
        app.logger.debug(request.form['mobile'])
        sendSMS(request.form['customer'],request.form['mobile'],request.form['cost'],request.form['bill'],request.form['billnumber'])
        sendMail(request.form['customer'],request.form['mobile'],request.form['bilhtml'],request.form['billnumber'],request.form['email'])
        saveBill(request.form['billnumber'],request.form['bilhtml'],request.form['customer'],request.form['mobile'])
        url_for('static',filename='rainbow_txt.css')
        return render_template('home_page.html')
    return 'you are sending bill'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('loginpage.html')

@app.route('/dbill')
def dbill():
    url_for('static',filename='add_item.jpg')
    return render_template('dynamic_bill.html',itemNames=loadProducts(session['username']))

@app.route('/home')
def home():
    if 'username' in session:
        app.logger.debug('Logged in as %s' % escape(session['username']))
        url_for('static',filename='rainbow_txt.css')
        return render_template('home_page.html')
    return 'You are not logged in'

@app.route('/viewbill',methods=['POST','GET'])
def viewbill():
    if request.method == 'POST':
        if 'username' in session:
             app.logger.debug('Logged in as %s' % escape(session['username']))
             billcontent = getbill(request.form['billnumber'])
             return render_template('printbill.html',bill=billcontent)
    if 'username' in session:
        app.logger.debug('Logged in as %s' % escape(session['username']))
        url_for('static',filename='rainbow_txt.css')
        return render_template('viewbill.html')
    return 'You are not logged in'

@app.route('/login',methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        app.logger.debug("Inside login POST")
        if valid_login(request.form['username'],
                       request.form['password']):
            session['username'] = request.form['username']
            load_catalog(request.form['username'])
            return redirect(url_for('home'))
        else:
            error = 'Invalid username/password'
    return render_template('loginpage.html', error=error)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'