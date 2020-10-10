from flask import Flask, request, render_template, redirect  # local hosting
import smtplib, ssl  # server library
import imghdr  # attachments
from email.message import EmailMessage  # creating a message to email
from datetime import datetime
import poplib  # inbox
import sys

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
    time = str(time)
    newMessage.set_content("Group 2 email server has started at " + time)
    sendEmail(newMessage)

    print("Checking if test email was received...")
    Mailbox = poplib.POP3_SSL('pop.googlemail.com', '995')
    Mailbox.user(userName)
    Mailbox.pass_(password)

    lastReceivedEmailTime = Mailbox.retr(1)[1][16] # metadata of email on what time it was sent
    if str(time) in str(lastReceivedEmailTime): # checking if times match up
        print("Server/function test finished. Ready to go live")

    Mailbox.quit()
    exit()


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
        loadInbox()
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

def loadInbox():
    htmlFile = open("templates/inbox.html", 'w')
    htmlFile.write(
"<!doctype html>\n"
"<html lang=\"en\">\n"
  "<head>\n"

    "<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">\n"
    
    "<title>Email Client</title>\n"

    "<!-- Bootstrap core CSS -->\n"
    "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\" integrity=\"sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z\" crossorigin=\"anonymous\">\n"

"<link rel= \"stylesheet\" type= \"text/css\" href= \"{{ url_for('static',filename='styles/styles.css') }}\">\n"

  "</head>\n"
  "<body class=\"text-center\">\n"
    "<div class=\"container\">\n"
      "<h1>Inbox</h1>\n"
    "<form class=\"form-inline d-flex justify-content-center md-form form-sm mt-0\"> \n"
     "<i class=\"fas fa-search\" aria-hidden=\"true\"></i> \n"
     "<input class=\"form-control form-control-sm ml-3 w-75\" type=\"text\" placeholder=\"Search Emails\" aria-label=\"Search\"> \n"
    "</form> \n"
      "<table class=\"table\">\n"
  "<thead class=\"thead-dark\">\n"
    "<tr>\n"
      "<th scope=\"col\">Sender</th>\n"
      "<th scope=\"col\">Subject</th>\n"
      "<th scope=\"col\">Time</th>\n"
    "</tr>\n"
  "</thead>\n"
  "<tbody>\n")
    htmlFile.close()

    Mailbox = poplib.POP3_SSL('pop.googlemail.com', '995')
    userEmail = "group2emailclient@gmail.com"
    userPassword = "Group2Test"
    Mailbox.user(userEmail)
    Mailbox.pass_(userPassword)
    numEmails = Mailbox.list()[1]
    htmlFile = open("templates/inbox.html", 'a')
    for email in numEmails:
        htmlFile.write(
            "<tr>\n"
            "<td>sender1</td>\n" #sender here
            "<td>subject1</td>\n" #subect here
            "<td>time1</td>\n" #time
            "<tr>\n")
    htmlFile.close()

    htmlFile = open("templates/inbox.html", 'a')
    htmlFile.write(
    "</tr>\n"
  "</tbody>\n"
"</table>\n"

"<table class=\"table\">\n"
  "<form action=\"sendmail\">\n"
      "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Send mail</button>\n"
    "</form>\n"
    "</div>\n"
  "</body>\n"
"</html>\n")


def sendEmail(newMessage):
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        server.login(userEmail, userPassword)
        server.send_message(newMessage)
    return redirect('/inbox')  # goes back to inbox after sending mail


# starting web app
if __name__ == '__main__':
    if len(sys.argv) == 2 and str(sys.argv[1]) == "travisTest":
        travisTest()

    app.run(host='0.0.0.0', debug=True)  # Launches server on main computer's ipv4 address:5000