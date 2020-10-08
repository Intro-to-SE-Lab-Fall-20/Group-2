from flask import Flask, request, render_template, redirect # local hosting
import smtplib, ssl # server library
import imghdr
from email.message import EmailMessage


app = Flask(__name__)
emailport = 465 #Gmail port
context = ssl.create_default_context()


def travisTest():
    newMessage = EmailMessage()
    newMessage['To'] = "elichartnett@gmail.com"
    newMessage['Subject'] = "subject"
    newMessage['From'] = "group2emailclient@gmail.com"
    newMessage.set_content("test body")

    sendEmail(newMessage, "group2emailclient@gmail.com", "Group2Test")


# Web Pages - first pages are commented, the rest follow similar functionality
@app.route('/', methods=['GET', 'POST'])
def login():
    travisTest()

    if request.method == 'POST':  #when form is submitted, it collects the data and authenticates
        global userEmail, userPassword
        userEmail = request.form['email']  #requests the object with name 'email'
        userPassword = request.form['password']  #requests the object with name 'password'
        authenticate()  # check creds
        return redirect('/inbox')  #after login, go to inbox

    else:
        return render_template('login.html')  #renders login.html until form is submitted

@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if request.method == 'POST':  #when form is submitted, it performs the only action (going to send an email)
        return redirect('/sendmail')

    else:
        return render_template('inbox.html')  #renders inbox.html until form is submitted

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


#Functions to help web pages
def authenticate():
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        server.login(userEmail, userPassword)  # connecting to server and logging in (checks creds)

def sendEmail(newMessage, userEmail, userPassword):
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
        server.login(userEmail, userPassword)
        server.send_message(newMessage)
    return redirect('/inbox') #goes back to inbox after sending mail


#starting web app
if __name__ == '__main__':
    app.run(host = '0.0.0.0')  # Launches server on main computer's ipv4 address:5000
