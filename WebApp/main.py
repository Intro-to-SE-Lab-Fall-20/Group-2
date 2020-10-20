from flask import Flask, request, render_template, redirect  # local hosting
import smtplib, ssl  # server library
import imghdr  # to send certain attachments
from email.message import EmailMessage  # creating a message to email
from datetime import datetime
import imaplib
import email
import sys
import os
import shutil  # removes directory of uploaded files

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

    typ, data = imap.fetch(str(numEmails).encode(), '(RFC822)')  # reads most recent email
    msg = email.message_from_string(data[0][1].decode('latin1'))
    body = msg.get_payload()
    if time in body:  # if email time is same as the time the test email was sent, test passes
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
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    if request.method == 'POST':
        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login(userEmail, userPassword)
        imap.select('Inbox')

        if request.form.get('search'):
            userSearch = request.form.get('search')  # requests the object with name 'search'

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
    print("Inside sendmail route")

    if request.method == 'POST':
        newMessage = EmailMessage()
        newMessage['To'] = request.form['toemail']
        newMessage['Subject'] = request.form['subject']
        newMessage['From'] = userEmail
        newMessage.add_alternative(request.form['msgbody'], subtype='html')

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
        return render_template('/sendmail.html')

@app.route('/logout')
def logout():
    file = open('userCredentials.txt', 'w')
    file.write("")
    os.remove('userCredentials.txt')

    file = open('templates/inbox.html', 'w')
    file.write("")
    os.remove('templates/inbox.html')

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

    text = (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"

        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">\n"

        "<title>Email Client</title>\n"

        "<!-- Bootstrap core CSS -->\n"
        "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\" integrity=\"sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z\" crossorigin=\"anonymous\">\n"

        "<link rel= \"stylesheet\" type= \"text/css\" href= \"{{ url_for('static',filename='styles/styles.css') }}\">\n"

        "<script src=\"//cdn.ckeditor.com/4.14.1/basic/ckeditor.js\"></script>\n"
        "</head>\n"
        "<body class=\"text-center\">\n"
        "<div class=\"container\">\n"
        "<form action=\"logout\">"
        "<button class=\"btn btn-primary\" style=\"right: 0;\" type=\"submit\">Logout</button>\n"
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
    )

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
    maxLoad = 25
    toLoad = 0
    if numEmails > maxLoad:
        toLoad = maxLoad
    else:
        toLoad = numEmails
    index = numEmails

    for messageNum in range(toLoad):  # iterating through all messages
        currentEmail = str(index).encode()
        typ, data = imap.fetch(currentEmail, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('latin1'))
                email_subject = msg['subject']
                if email_subject != None and len(email_subject) > 25:
                    email_subject = email_subject[:25] + "..."
                email_from = msg['from']
                if len(email_from) > 35:
                    email_from = email_from[:35] + "..."
                email_date = msg['date']
                # email_body = str(msg.get_payload(decode=True))
                if msg.is_multipart():
                    for part in msg.get_payload():
                        email_body = part.get_payload()
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))

                        '''if ctype == 'text/plain' or 'application' not in cdispo:
                            email_body = "text/plain"'''
                        '''elif "attachment" in cdispo:
                            filename = part.get_filename()
                            if filename:
                                if not os.path.isdir(email_subject):
                                    os.mkdir(email_subject)
                                filepath = os.path.join(email_subject, filename)
                                open(filepath, "wb").write(part.get_payload(decode=True))'''

                else:
                    # ctype = part.get_content_type()
                    print(index)
                    email_body = msg.get_payload(decode=True)
                    '''if ctype == "text/plain":
                        print(msg_body)'''

                index -= 1

        text += (  # appending sender, subject, and time to inbox.html file
            # "<table class=\"table\">\n"
            "<tr onclick=\"openEmail")
        text += str(index + 1) + ("();\">\n"
                                  "<td>")

        text += email_from

        text += (
            "</td>\n"
            "<td>")

        text += email_subject

        text += (
            "</td>\n"
            "<td>")

        text += email_date
        text += (
            "</td>\n")
        text += (  # add div here
            "<div class=\"text-left\" style=\" overflow: auto; display: none; position: absolute; width: 50%; height: 50%; left: 25%; background-color: white; padding: 10px; border-style: outset; border-color: blue;\" id=\"email")
        text += str(index + 1) + "\">\n"

        text += (
            "<h5>From: ")

        text += email_from + "</h5><br>\n"
        text += "<h5>Subject: " + email_subject + "</h5>\n"
        text += "<h6>Date: " + email_date + "</h6><br>\n"
        text += "<h6>" + str(email_body) + "</h6><br>\n"
        text += (
            "<button class=\"btn btn-primary\" style=\"position: absolute; right: 0; bottom: 0; margin: 5px;\" type=\"button\" onclick=\"closeEmail"
        )
        text += str(index + 1) + ("()\">Cancel</button>\n"
                                  "<button class=\"btn btn-primary\" style=\"position: absolute; right: 80px; bottom: 0; margin: 5px\" type=\"button\" onclick=\"openForm('" + email_subject + "' , `" + str(email_body) + "`);\">Forward</button>\n"
                                                                                                                                                                                                                      "</div>\n")
        text += (
            "<script>\n"
            "function openEmail")
        text += str(index + 1) + ("(){\n"
                                  "document.getElementById(\"email")
        text += str(index + 1) + ("\").style.display = \"block\";\n"
                                  "}\n"
                                  "function closeEmail")
        text += str(index + 1) + ("() {\n"
                                  "document.getElementById(\"email")
        text += str(index + 1) + ("\").style.display = \"none\";\n"
                                  "}\n"
                                  "</script>\n")
        text += (
            "</tr>\n"

        )

    text += (

            "</table>\n"
            "<br><br>"
            "<button class=\"btn btn-lg btn-primary btn-block\" name=\"sendMail\" onclick=\"openForm(\'\',\'\')\" value=\"sendMail\">Send mail</button>\n"
            "<div style=\"  bottom: 500px; display: none; position: relative; align-items: center;\" id=\"myForm\">\n"
            "<form action=\"sendmail\" style=\" margin: auto; width: 800px; background-color: white; padding: 10px; border-style: outset; border-color: blue;\" method=\"POST\" enctype=\"multipart/form-data\">\n"
            "<h1>Email Client</h1>\n"
            "<h1 class=\"h3 mb-3 font-weight-normal\">Send Email</h1>\n"
            "<label for=\"sendto\" class=\"sr-only\">To:</label>\n"
            "<input type=\"email\" name= \"toemail\" id=\"sendto\" class=\"form-control\" placeholder=\"To\" required autofocus>\n"
            "<label for=\"subject\" class=\"sr-only\">Subject</label>\n"
            "<input type=\"text\" name=\"subject\" id=\"subject\" class=\"form-control\" placeholder=\"Subject\" required>\n"


            "<label for=\"msgbody\" class=\"sr-only\">Message Body</label>\n"
            "<textarea name=\"msgbody\" id=\"msgbody\" placeholder=\"Message Body\" required rows=\"10\" cols=\"10\"></textarea>\n"

            "<label for=\"attachment\" class=\"sr-only\">Attachment</label>\n"
            "<input type=\"file\" name=\"attachment\" id=\"attachment\" class=\"form-control\" placeholder=\"Attachment (optional)\">\n"
            "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Send</button>\n"
            "<button class=\"btn btn-lg btn-primary btn-block\" type=\"button\" onclick=\"closeForm()\">Cancel</button>\n"
            "</form>\n"
            "</div>\n"
            "<script>\n"

            "function openForm(s, b){\n"
            "var editor = CKEDITOR.replace( 'msgbody', {height: 500, contentsCss: \"body {font-size: 20px;}\"});\n"
            "if (b != ''){\n"
            "CKEDITOR.config.readOnly = true;\n"
            "var forward = 'From: " + email_from + "<br>';\n"
                                                   "var forward = forward.concat(b);\n"
                                                   "}\n"

                                                   "CKEDITOR.instances.msgbody.setData(forward);\n"
                                                   "document.getElementById(\"subject\").value = s; \n"
                                                   "document.getElementById(\"myForm\").style.display = \"block\";\n"
                                                   "b = null;\n"

                                                   "}\n"
                                                   "function closeForm() {\n"
                                                   "document.getElementById(\"myForm\").style.display = \"none\";\n"
                                                   "}\n"
                                                   "</script>\n"
                                                   "</body>\n"
                                                   "</html>\n")

    htmlFile = open("templates/inbox.html", 'w')
    htmlFile.write(text)


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
