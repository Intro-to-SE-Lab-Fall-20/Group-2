from flask import Flask, request, render_template, redirect  # local hosting
import smtplib, ssl  # server library
import imghdr  # to send certain attachments
from email.message import EmailMessage  # creating a message to email
from datetime import datetime
import imaplib
import email
import sys
import os
import shutil # removes directory of uploaded files


app = Flask(__name__)
emailport = 465  # Gmail port
context = ssl.create_default_context()


def travisTest():  # sends email to itself to verify it works (for travis CI)
    print("Sending test email...")  # setting up email
    userEmail = "group2emailclient@gmail.com"
    userPassword = "Group2Test"
    newMessage = EmailMessage()
    newMessage['To'] = userEmail
    newMessage['Subject'] = "TRAVIS CI TEST"
    newMessage['From'] = "Group 2"
    time = datetime.now()
    time = str(time)
    newMessage.set_content("Group 2 email server has started at " + time)

    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:  # sending email
        server.login(userEmail, userPassword)
        server.send_message(newMessage)

    print("Checking if test email was received...")
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    imap.login(userEmail, userPassword)
    imap.select('Inbox')
    type, messages = imap.search(None, 'ALL')
    numEmails = len(messages[0].split())

    typ, data = imap.fetch(str(numEmails).encode(), '(RFC822)')
    msg = email.message_from_string(data[0][1].decode('latin1'))
    body = msg.get_payload()
    if time in body:
        exit()


# Web Pages - first pages are commented, the rest follow similar functionality
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # when form is submitted, it collects the data and authenticates
        userEmail = request.form['email']  # requests the object with name 'email'
        userPassword = request.form['password']  # requests the object with name 'password'
        userInfoFile = open("userCredentials.txt", 'w')  # saving credentials for later use
        userInfoFile.write(userEmail + "\n")
        userInfoFile.write(userPassword + "\n")
        userInfoFile.close()

        authenticate()  # check creds
        return redirect('/inbox')  # after login, go to inbox

    else:
        return render_template('login.html')  # renders login.html until form is submitted


@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if request.method == 'POST':
        userSearch = request.form['search']  # requests the object with name 'search'

        print(userSearch)
        return render_template('/SearchResults.html')

    else:
        loadInbox()
        return render_template('inbox.html')  # renders inbox.html until form is submitted


@app.route('/sendmail', methods=['GET', 'POST'])
def sendMail():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    if request.method == 'POST':
        newMessage = EmailMessage()
        newMessage['To'] = request.form['toemail']
        newMessage['Subject'] = request.form['subject']
        newMessage['From'] = "Group 2"
        newMessage.set_content(request.form['msgbody'])

        image = request.files["attachment"]
        if image.filename != "":
            rootPath = os.path.dirname(os.path.abspath("main.py"))
            imageUploads = "imageUploads"
            uploadImagesPath = os.path.join(rootPath, imageUploads)
            if os.path.exists("imageUploads") == False:
                os.mkdir(uploadImagesPath)
            app.config["IMAGE_UPLOADS"] = uploadImagesPath
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            file = open(os.path.join(app.config["IMAGE_UPLOADS"], image.filename), "rb")
            fileData = file.read()
            if '.pdf' in image.filename:
                newMessage.add_attachment(fileData, maintype="application", subtype="pdf")
            elif '.txt' in image.filename:
                newMessage.add_attachment(fileData)
            elif '.png' in image.filename or '.gif' in image.filename:
                print("png")
                image_type = imghdr.what(file.name)
                newMessage.add_attachment(fileData, maintype='image', subtype=image_type)
        return sendEmail(newMessage)
    else:
        return render_template('sendmail.html')



@app.route('/logout')
def logout():
    os.remove('userCredentials.txt')
    file = open('userCredentials', 'w')
    file.write("")

    file = open('templates/inbox.html', 'w')
    file.write("")

    if os.path.exists("imageUploads") == True:
        shutil.rmtree('imageUploads')
    return redirect('/')


# Functions to help web pages
def authenticate():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        server.login(userEmail, userPassword)  # connecting to server and logging in (checks creds)


def loadInbox():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

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
        "<form action=\"logout\">"
        "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Logout</button>\n"
        "</form>\n"
        "<h1>Inbox</h1>\n"
        "<form class=\"inbox\" method=\"POST\">\n"
        "<label for=\"searchInbox\" class=\"sr-only\">Search Term</label>\n"
        "<input type=\"search\" name= \"search\" id=\"searchInbox\" class=\"form-control\" placeholder=\"Search Inbox\" required autofocus> \n"
        "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Search Inbox</button> \n"
        "</form>"
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

    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userEmail = userEmail[0:len(userEmail) - 1]
    userPassword = userPassword[0:len(userPassword) - 1]
    userInfoFile.close()

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(userEmail, userPassword)
    imap.select('Inbox')
    type, messages = imap.search(None, 'ALL')
    numEmails = len(messages[0].split())
    maxLoad = 10
    numLoaded = 0
    index = numEmails

    for messageNum in messages[0].split():  # iterating through all messages
        currentEmail = str(index).encode()
        typ, data = imap.fetch(currentEmail, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('latin1'))
                email_subject = msg['subject']
                email_from = msg['from']
                email_body = msg.get_payload()
                index-=1

        htmlFile = open("templates/inbox.html", 'a')  # appending sender, subject, and time to inbox.html file
        htmlFile.write(
            "<tr>\n"
            "<td>")
        htmlFile.close()

        htmlFile = open("templates/inbox.html", 'a')
        htmlFile.write(email_from)
        htmlFile.close()

        htmlFile = open("templates/inbox.html", 'a')
        htmlFile.write(
            "</td>\n"
            "<td>")
        htmlFile.close()

        if email_subject != None:
            htmlFile = open("templates/inbox.html", 'a')
            htmlFile.write(email_subject)
            htmlFile.close()

        htmlFile = open("templates/inbox.html", 'a')
        htmlFile.write("</td>\n"
                       "<td>")
        htmlFile.close()

        htmlFile = open("templates/inbox.html", 'a')
        htmlFile.write("time")
        htmlFile.close()

        htmlFile = open("templates/inbox.html", 'a')
        htmlFile.write("</td>\n"
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
        "</table> \n"
        "</div>\n"
        "</body>\n"
        "</html>\n")


def sendEmail(newMessage):
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:  # sending email
        server.login(userEmail, userPassword)
        server.send_message(newMessage)
    return redirect('/inbox')  # goes back to inbox after sending mail


# starting web app
if __name__ == '__main__':
    if len(sys.argv) == 2 and str(sys.argv[1]) == "travisTest":
        travisTest()

    app.run(host='0.0.0.0', debug=True)  # Launches server on main computer's ipv4 address:5000