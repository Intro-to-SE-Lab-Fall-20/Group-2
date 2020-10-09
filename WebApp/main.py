from flask import Flask, request, render_template, redirect  # local hosting
import smtplib, ssl  # server library
import imghdr  # attachments
from email.message import EmailMessage  # creating a message to email
from datetime import datetime
import poplib  # inbox
import email

app = Flask(__name__)
emailport = 465  # Gmail port
context = ssl.create_default_context()


def travisTest():  # sends email to itself to verify it works (for travis CI)
    print("Sending test email...")
    userName = "group2emailclient@gmail.com"
    password = "Group2Test"
    newMessage = EmailMessage()
    newMessage['To'] = "group2emailclient@gmail.com"
    newMessage['Subject'] = "1 SERVER STARTED"
    newMessage['From'] = "Group 2"
    time = datetime.now()
    newMessage.set_content("Group 2 email server has started at " + str(time))
    sendEmail(newMessage, userName, password)

    print("Checking if test email was received...")
    Mailbox = poplib.POP3_SSL('pop.googlemail.com', '995')
    Mailbox.user(userName)
    Mailbox.pass_(password)

    numMessages = len(Mailbox.list()[1])

    for i in range(numMessages):
        for j in Mailbox.retr(i+1)[1]:
            print(Mailbox.retr(i+1)[1][16]) 

    Mailbox.quit()


# Web Pages - first pages are commented, the rest follow similar functionality
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # when form is submitted, it collects the data and authenticates
        global userEmail, userPassword
        userEmail = request.form['email']  # requests the object with name 'email'
        userPassword = request.form['password']  # requests the object with name 'password'
        authenticate()  # check creds
        return redirect('/inbox')  # after login, go to inbox

    else:
        return render_template('login.html')  # renders login.html until form is submitted


@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if request.method == 'POST':  # when form is submitted, it performs the only action (going to send an email)
        return redirect('/sendmail')

    else:
        return render_template('inbox.html')  # renders inbox.html until form is submitted


@app.route('/sendmail', methods=['GET', 'POST'])
def sendMail():
    if request.method == 'POST':
        newMessage = EmailMessage()
        newMessage['To'] = request.form['toemail']
        newMessage['Subject'] = request.form['subject']
        newMessage['From'] = userEmail
        newMessage.set_content(request.form['msgbody'])
        att = request.form['attachment']
        if '.pdf' in att:
            file = open(request.form['attachment'], "rb")
            file_data = file.read()
            newMessage.add_attachment(file_data, maintype="application", subtype="pdf")
        elif '.txt' in att:
            file = open(request.form['attachment'], "r")
            file_data = file.read()
            newMessage.add_attachment(file_data)
        elif '.png' in att or '.gif' in att:
            file = open(request.form['attachment'], "rb")
            image = file.read()
            image_type = imghdr.what(file.name)
            newMessage.add_attachment(image, maintype='image', subtype=image_type)
        return sendEmail(newMessage)
    else:
        return render_template('sendmail.html')


# Functions to help web pages
def authenticate():
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        server.login(userEmail, userPassword)  # connecting to server and logging in (checks creds)


def sendEmail(newMessage, userEmail, userPassword):
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        server.login(userEmail, userPassword)
        server.send_message(newMessage)
    return redirect('/inbox')  # goes back to inbox after sending mail


# starting web app
if __name__ == '__main__':
    travisTest()
    app.run(host='0.0.0.0')  # Launches server on main computer's ipv4 address:5000
