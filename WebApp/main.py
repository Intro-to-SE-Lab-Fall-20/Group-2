from flask import Flask, request, render_template, redirect, session # local hosting
import smtplib, ssl  # server library
import imghdr  # to send certain attachments
from email.message import EmailMessage  # creating a message to email
from datetime import datetime
import imaplib
import email
import sys
import os
import shutil # removes directory of uploaded files
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import time
import socket
import email.utils
from cryptography.fernet import Fernet
import webbrowser
import os.path
from os import path


app = Flask(__name__)
emailport = 465  # Gmail port
context = ssl.create_default_context()

global key
key = Fernet.generate_key()
error = ''


def travisTest():  # sends email to itself to verify it works (for travis CI)

    print("Test 1: Login with wrong credentials.")
    userEmail = "wrongEmail@gmail.com"
    userPassword = "wrongPassword1"
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:  # sending email
        try:
            server.login(userEmail, userPassword)
            print("FAIL")
        except:
            print("PASS")

    print("Test 2: Login with correct credentials.")  # setting up email
    userEmail = "group2emailclient@gmail.com"
    userPassword = "Group2Test"

    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:  # sending email
        try:
            server.login(userEmail, userPassword)
            print("PASS")
        except:
            print("FAIL")

    print("Test 3: Create email with no sender, but includes a subject and body.")
    newMessage = EmailMessage()
    newMessage['To'] = ""
    newMessage['Subject'] = "TRAVIS CI TEST"
    newMessage['From'] = "Group 2"
    time = datetime.now()
    time = str(time)
    newMessage.set_content("Verification time: " + time)
    print("PASS")
    print("Test 4: Send test 3 email to itself.")
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            server.send_message(newMessage)
            print("FAIL")
        except:
            print("PASS")

    print("Test 5: Create email with sender, subject, and body.")
    newMessage = EmailMessage()
    newMessage['To'] = userEmail
    newMessage['Subject'] = "TRAVIS CI TEST"
    newMessage['From'] = "Group 2"
    time = datetime.now()
    time = str(time)
    newMessage.set_content("Verification time: " + time)
    print("PASS")
    print("Test 6: Send test 5 email to itself.")
    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:  # sending email
        server.login(userEmail, userPassword)
        server.send_message(newMessage)
        print("PASS")
    print("Test 7: Check if that exact previous email was recieved.")
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(userEmail, userPassword)
    imap.select('Inbox')
    type, messages = imap.search(None, 'ALL')
    numEmails = len(messages[0].split())
    typ, data = imap.fetch(str(numEmails).encode(), '(RFC822)') # reads most recent email
    msg = email.message_from_string(data[0][1].decode('latin1'))
    body = msg.get_payload()
    if time in body: # if email time is same as the time the test email was sent, test passes
        print("PASS")
    exit()

# Web Pages - first pages are commented, the rest follow similar functionality
@app.route('/', methods=['GET', 'POST'])
def login():
    global attempts
    global error
    global then
    now = time.time()
    if request.method == 'POST':  # when form is submitted, it collects the data and authenticates
        userEmail = request.form['email']  # requests the object with name 'email'
        userPassword = request.form['password']  # requests the object with name 'password'
        #userPassword = encrypt(userPassword.encode(), key)
        userInfoFile = open("userCredentials.txt", 'w')  # saving credentials for later use
        userInfoFile.write(userEmail + "\n")
        #userInfoFile = open("userCredentials.txt", 'ab')
        userInfoFile.write(userPassword + "\n")
        userInfoFile.close()

        if authenticate() and attempts > 0:  # check creds
            return redirect('/director')  # after login, go to inbox
        else:
            attempts -= 1
            error = "You have " + str(attempts) + " attempts left."
            if attempts == 0:
                error = "All attempts used."
                then = time.time()
                error += " Please try again in " + str(int((20 - (now - then)))) + " seconds."
                if (int(now - then) > 20):
                    attempts = 5
                    error = ''
            if attempts < 0:
                error = "All attempts used."
                error += " Please try again in " + str(int((20 - (now - then)))) + " seconds."
                if (int(now - then) > 20):
                    attempts = 5
                    error = ''


        return render_template('login.html', error=error)
    else:
        return render_template('login.html')  # renders login.html until form is submitted

@app.route('/director', methods=['POST', 'GET'])
def direct():
    if request.method == "POST":
        if "Notes" in request.form:
            return notes()
        if "Email" in request.form:
            return redirect('/inbox')

    else:
        return render_template('director.html')

@app.route('/notes', methods=['POST', 'GET'])
def notes():
    text = """<!DOCTYPE html>\n
            <html lang="en">\n
            <head>\n
            <meta charset="utf-8">\n
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n
            <title>Email Client</title>\n
            <script src=\"//cdn.ckeditor.com/4.14.1/basic/ckeditor.js\">\n</script>\n
            <!-- Bootstrap core CSS -->\n
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">\n
          </head>\n
          <body class="text-center">\n
        <form action="logout">
        <button class="btn btn-primary" style="right: 0;" type="submit">Logout</button>\n
        </form>\n
          <div style="height: 600px; width: 125px; position: absolute; left: 50px; top: 100px;">\n"""

    if path.exists("notes.txt"):
        more = True
        body =''
        with open("notes.txt", "r") as notes:
            line = notes.readline()
            while "eon" not in line:
                print("this many times")
                if "T-" in line:
                    title = line[2:-1]
                    line = notes.readline()
                    body = line[2:-1]
                    print("Title: ", title)
                    print("Body: ", body)
                    line = notes.readline()
                    text += ("<button class=\"btn btn-lg btn-primary\" style=\"width: 125px; margin: 2.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;\" onclick=\""
                    "document.getElementById(\'Title\').value = \'" + title + "\';\n"
                    "CKEDITOR.instances.Message.setData(\'" + body + "\');\n"
                    "\">" + title + "</button>\n")
                if "eon" in line:
                    break

                
                line = notes.readline()


    text += """
          </div>
          <form action="savenote" method="POST" onreset="CKEDITOR.instances.Message.setData('');">\n
          <h1>Notes</h1>\n
          <div style="display: inline-block;">\n
          <input type="text" name="Title" id="Title" class="form-control" placeholder="Note Title" style="width: 600px;">\n
          <textarea name="Message" id="Message" class="form-control" placeholder="Note Message" style="width: 600px; height: 700px;"></textarea>\n
          <div style="display: block;">\n
          <button class="btn btn-lg btn-primary" type="submit" name="save">Save Note</button>\n
          <button class="btn btn-lg btn-primary" type="reset" name="newNote">New Note</button>\n
          </div>\n
          </div>\n
          <script>\n
          CKEDITOR.replace( 'Message', {height: 500, contentsCss: "body {font-size: 20px;}"});\n
          </script>\n"""
    text += """\t\t\t\t\t\t\t</form>\n
                </body>\n
                </html>\n"""
    html = open("templates/notes.html", 'w')
    html.write(text)
    html.close()
    return render_template('notes.html')

@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

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
    index = numEmails

    if request.form.get('search'):
        search = request.form.get('search')  # requests the object with name 'search'
        loadInbox(search, index)
        search = None

    else:
        loadInbox(None, index)
    return render_template('inbox.html')  # renders inbox.html until form is submitted

@app.route('/sendmail', methods=['GET', 'POST'])
def sendMail():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    if request.method == 'POST':
        newMessage = MIMEMultipart()
        newMessage['To'] = request.form['toemail']
        newMessage['Subject'] = request.form['subject']
        newMessage['From'] = userEmail
        newMessage['Reply-to'] = userEmail
        body = MIMEText(request.form['msgbody'], 'html', 'utf-8')
        body.add_header('Content-Disposition', 'text/html')

        newMessage.attach(body)

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
                att = MIMEApplication(fileData, _subtype="pdf")
                att.add_header('Content-Disposition', 'attachment', filename=image.filename)
                newMessage.attach(att)
            elif '.txt' in image.filename:
                att = MIMEText(fileData.decode())
                att.add_header('Content-Disposition', 'attachment', filename=image.filename)
                newMessage.attach(att)
                #newMessage.add_attachment(fileData)
            elif '.png' in image.filename or '.gif' in image.filename:
                print("png")
                image_type = imghdr.what(file.name)
                att = MIMEImage(fileData)
                att.add_header('Content-Disposition', 'attachment', filename=image.filename)
                newMessage.attach(att)
        return sendEmail(newMessage)
    else:
        return render_template("/sendmail.html")



@app.route('/logout')
def logout():
    file = open('userCredentials.txt', 'r+')
    file.truncate(0)
    file.close()
    #os.remove('userCredentials.txt')

    file = open('templates/inbox.html', 'r+')
    file.truncate(0)
    file.close()
    #os.remove('templates/inbox.html')


    if os.path.exists("imageUploads") == True:
        shutil.rmtree('imageUploads')

    if os.path.exists("notes.txt") == True:
        os.remove("notes.txt")

    if os.path.exists("templates/notes.html") == True:
        os.remove("templates/notes.html")
    print("loggin out for some reason")

    return redirect('/')


# Functions to help web pages
def authenticate():
    userInfoFile = open("userCredentials.txt", 'r')
    userEmail = userInfoFile.readline()
    userPassword = userInfoFile.readline()
    userInfoFile.close()

    with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
        try:
            server.login(userEmail, userPassword)  # connecting to server and logging in (checks creds)
            return True
        except:
            return False

def loadInbox(search, index):
    if search == None:
        search = ''
        maxLoad = 10
    else:
        maxLoad = 20
    text = (

        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"

        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">\n"

        "<title>Email Client</title>\n"

        "<!-- Bootstrap core CSS -->\n"
        "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\" integrity=\"sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z\" crossorigin=\"anonymous\">\n"
        "<link rel=\"stylesheet\" href=\"https://www.w3schools.com/w3css/4/w3.css\">"
        "<link rel= \"stylesheet\" type= \"text/css\" href= \"{{ url_for('static',filename='styles/styles.css') }}\">\n"

        "<script src=\"//cdn.ckeditor.com/4.14.1/basic/ckeditor.js\">\n"
        "</script>\n"
        "<style>\n"
        "tr:hover {background-color: DodgerBlue;}\n"
        "</style>\n"
        "</head>\n"
        "<body class=\"text-center\">\n"
        "<div class=\"container\">\n"
        "<form action=\"logout\">"
        "<button class=\"btn btn-primary\" style=\"right: 0;\" type=\"submit\">Logout</button>\n"
        "</form>\n"
        "<h1>Inbox</h1>\n"
        "<form action=\"inbox\"method=\"POST\">\n"
        "<input type=\"search\" name= \"search\" id=\"searchInbox\" class=\"form-control\" placeholder=\"Search Inbox\" required autofocus value=\"" + search + "\"> \n"

        "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Search Inbox</button> \n"
        "</form>")

    if request.form.get('search'):
        text += (
            "<form onsubmit=\"closeButton()\"action=\"inbox\" >\n"
            "<button class=\"btn btn-lg btn-primary btn-block\" id=\"cancel\" type=\"submit\">Cancel Search</button> \n"
            "</form>"
            )

    text += (

        "<table class=\"table\">\n"
        "<thead class=\"thead-dark\">\n"
        "<tr>\n"
        "<th scope=\"col\">Sender</th>\n"
        "<th scope=\"col\">Subject</th>\n"
        "<th scope=\"col\">Time</th>\n"
        "</tr>\n"
        "</thead>\n"
        #"</table>\n"
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

    toLoad = 0
    if numEmails > maxLoad:
        toLoad = maxLoad
    else:
        toLoad = numEmails
    print(search)

    index -= 0
    for messageNum in range(toLoad):  # iterating through all messages
        currentEmail = str(index).encode()
        typ, data = imap.fetch(currentEmail, '(RFC822)')
        email_att = ""
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                if email_subject != None and len(email_subject) > 25:
                    subject_display = email_subject[:25] + "..."
                email_from = msg['from']
                if len(email_from) > 35:
                    email_from = email_from[:35]
                email_date = email.utils.parsedate_to_datetime(msg['date'])
                email_date = email_date.strftime('%a, %d %b %y %I:%M%p')
                filename = ''
                if search != '':
                    if search.lower() in email_subject.lower() or search.lower() in email_from.lower():
                        if msg.is_multipart():

                            for part in msg.walk():
                                email_att = ""
                                ctype = part.get_content_type()
                                cdispo = str(part.get('Content-Disposition'))



                                if ctype == 'text/html' or 'application' in cdispo:
                                    email_body = part.get_payload(decode=True).decode('cp1252')

                                elif "attachment" in cdispo:
                                    filename = part.get_filename()
                                    if '.pdf' in filename:
                                        if not os.path.isdir('static'):
                                            os.mkdir('static')
                                        filepath = os.path.join('static', filename)
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                                        email_att += "<a href=\"static/" + filename + "\" target=\"_blank\">" + filename +"</a>\n"

                                    elif '.txt' in filename:
                                        if not os.path.isdir('static'):
                                            os.mkdir('static')
                                        filepath = os.path.join('static', filename)
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                                        email_att += (
                                            "<p><a href=\"static/" + filename + "\" download>\n"
                                            + filename + "</a></p>\n"
                                            )


                                    elif '.png' or '.jpg' or '.gif' in filename:
                                        if not os.path.isdir('static'):
                                            os.mkdir('static')
                                        filepath = os.path.join('static', filename)
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                                        email_att += (
                                            "<a href=\"static/" + filename + "\" download>\n"
                                            "<img onmouseover=\"style.opacity = .6;\" onmouseout=\"style.opacity = 1;\" src=\"static/" + filename + "\" width=\"75%\" height=\"125%\" style=\"bottom: 137%; border-radius: 8px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);\"alt=\"image\">\n"
                                            "</a>\n"
                                            )

                        else:
                            email_body = msg.get_payload(decode=True).decode()
                        match = True
                        continue

                    else:
                        match = False
                        continue

                else:
                    search = ''
                    match = True
                    if msg.is_multipart():

                        for part in msg.walk():
                            email_att = ""
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))


                            if ctype == 'text/html' or 'application' in cdispo:
                                email_body = part.get_payload(decode=True).decode('cp1252')

                            elif "attachment" in cdispo:
                                filename = part.get_filename()
                                #print(filename)
                                if '.pdf' in filename:
                                    if not os.path.isdir('static'):
                                        os.mkdir('static')
                                    filepath = os.path.join('static', filename)
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                                    email_att += "<a href=\"static/" + filename + "\" target=\"_blank\">" + filename +"</a>\n"

                                elif '.txt' in filename:
                                    if not os.path.isdir('static'):
                                        os.mkdir('static')
                                    filepath = os.path.join('static', filename)
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                                    email_att += (
                                        "<p><a href=\"static/" + filename + "\" download>\n"
                                        + filename + "</a></p>\n"
                                        )

                                elif '.png' or '.jpg' or '.gif' in filename:
                                    if not os.path.isdir('static'):
                                        os.mkdir('static')
                                    filepath = os.path.join('static', filename)
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                                    email_att += (
                                        "<a href=\"static/" + filename + "\" download>\n"
                                        "<img onmouseover=\"style.opacity = .6;\" onmouseout=\"style.opacity = 1;\" src=\"static/" + filename + "\" width=\"75%\" height=\"125%\" style=\"bottom: 137%; border-radius: 8px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);\"alt=\"image\">\n"
                                        "</a>\n"
                                        )

                    else:
                        email_body = msg.get_payload(decode=True).decode()

        index-=1
        #if filename :
            #print(filename)
        if match == False:
            continue
        if search == None:
            search = ''

        text += (  # appending sender, subject, and time to inbox.html file
            "<tr class=\"w3-animate-zoom\" onclick=\"openEmail")
        text += str(index+1) + ("();\">\n"
            "<td>"
            )

        text += email_from

        text += (
            "</td>\n"
            "<td>")

        if email_subject == None:
            text += subject_display
        else:
            text += email_subject

        text += (
            "</td>\n"
            "<td>")

        text += "<p>" + email_date + "</p>\n"

        text += (
            "<div style=\" display: none; position: fixed; padding-top: 200px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; margin: auto; background-color: rgba(0,0,255,.2);\" id=\"email")
        text += str(index+1) + "\">\n"
        text += (
            "<div class=\"text-left w3-container w3-animate-zoom\" style=\" word-wrap: break-word; position: relative; margin: auto; width: 600px; height: 700px; overflow: auto; background-color: white; padding: 10px; padding-bottom: 0px; padding-right: 0px; border: 10px outset #007bff;\">"
            "<div style=\"margin: auto; border: 3px solid #007bff;\">"
            "<h5>From: "
            )
        text += email_from + "<br>\n"
        text += "Subject: " + email_subject + "</h5>\n"
        text += "<h6>Date: " + email_date + "</h6></div><br>\n"
        text += "<div style=\"word-wrap: break-word; margin: auto; border: 3px solid #007bff; min-height: 700px; padding: 10px;\">"
        text += email_body.replace('\'', '').replace('<', '\n<')

        if '.pdf' in filename or '.txt' in filename:
            text += email_att
        text += "\n</div>\n"
        #else:
            #text += "</div>\n"

        text += ("<div style=\"bottom: 5%; left: 0; position: sticky; height: 85px; width: 175px;\">\n")
        if '.png' in filename or '.jpg' in filename or '.gif' in filename:
            text += email_att
        start = email_from.find('<') + len('<')
        end = email_from.find('>')
        sender = email_from[start:end]

        text +=(
            "<button class=\"btn btn-primary\"  type=\"button\" onclick=\'openForm(`Re: " + email_subject + "` , `\n" + email_body.replace('\'', '').replace('\"', '').replace('<', '\n<') + "` , ``, `" + sender +  "`)\' style=\"position: absolute; left: 165%; bottom: -30%; display: inline-block;\">Reply</button>\n"
            "<button class=\"btn btn-primary\"  type=\"button\" onclick=\'openForm(`\n" + email_subject + "` , `\n" + email_body.replace('\'', '').replace('\"', '').replace('<', '\n<') + "` , `\n" + email_att + "`)\' style=\"position: absolute; left: 210%; bottom: -30%; display: inline-block;\">Forward</button>\n"
            "<button class=\"btn btn-primary\" style=\"position: absolute; left: 265%; bottom: -30%; display: inline-block;\" type=\"button\" onclick=\"closeEmail"
            )
        text += str(index+1) + ("();event.stopPropagation()\">Cancel</button></div>\n")
        #if 'Forward' in email_body:
            #text += "</div>\n"
        text += (
            "</div>\n"
            "</div>\n"
            "<script>\n"
            "function openEmail")
        text += str(index+1) + ("(){\n"
            "document.getElementById(\"email")
        text += str(index+1) + ("\").style.display = \"block\";\n"
            "}\n"
            "function closeEmail")
        text += str(index+1) + ("() {\n"
            "document.getElementById(\"email")
        text += str(index+1) + ("\").style.display = \"none\";\n"
            "}\n"
            "</script>\n"
            )
        text += (
            "</td>\n"
            "</tr>\n"
            )

    text += (
        "</table>\n" 
        "<br>")

    text += (
        "<button class=\"btn btn-lg btn-primary\" id=\"rev\" onclick=\"Rev()\"><- Page</button>\n"
        )

    text += (
        "<button class=\"btn btn-lg btn-primary\" id=\"tab\" onclick=\"Tab()\">Page -></button>\n"

        "<form style=\"display: inline-block;\" onsubmit=\"Page()\" action=\"pageforward\" method=\"POST\" >\n"
        "<button class=\"btn btn-lg btn-primary\" id=\"page\" name=\"page\" value=\"" + str(index) + "\">Page -></button>\n"
        "</form><br>\n"
        )

    text += (
        "<br><button class=\"btn btn-lg btn-primary btn-block\" onclick=\"openForm('','', '', '')\" id=\"sendmail\" value=\"sendMail\">Send mail</button>\n"
        "<div  style=\" display: none; position: fixed; padding-top: 100px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; margin: auto; background-color: rgba(0,0,255,.2);\" id=\"myForm\">\n"
        "<form class=\"w3-container w3-center w3-animate-zoom\" action=\"sendmail\" style=\" position: relative; margin: auto; width: 800px; background-color: white; padding: 10px; border: 10px outset #007bff;\" method=\"POST\" enctype=\"multipart/form-data\">\n"
        "<h1>Email Client</h1>\n"
        "<h1 class=\"h3 mb-3 font-weight-normal\">Send Email</h1>\n"
        "<label for=\"sendto\" class=\"sr-only\">To:</label>\n"
        "<input type=\"email\" name= \"toemail\" id=\"sendto\" class=\"form-control\" placeholder=\"To\" required autofocus>\n"
        "<label for=\"subject\" class=\"sr-only\">Subject</label>\n"
        "<input type=\"text\" name=\"subject\" id=\"subject\" class=\"form-control\" placeholder=\"Subject\" required>\n"


        "<label for=\"msgbody\" class=\"sr-only\">Message Body</label>\n"
        "<textarea name=\"msgbody\" id=\"msgbody\" placeholder=\"Message Body\" required rows=\"10\" cols=\"10\"><script></script></textarea>\n"

        "<label for=\"attachment\" class=\"sr-only\">Attachment</label>\n"
        "<input type=\"file\" name=\"attachment\" id=\"attachment\" class=\"form-control\" placeholder=\"Attachment (optional)\">\n"
        "<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Send</button>\n"
        "<button class=\"btn btn-lg btn-primary btn-block\" type=\"button\" onclick=\"closeForm()\">Cancel</button>\n"
        "</form>\n"
        "</div>\n"
        "</div>\n"
        "<script>\n")

    text += """
if(sessionStorage.tab == 0){
document.getElementById("rev").style.display = "none";
}
if(sessionStorage.tab == sessionStorage.page){
document.getElementById("tab").style.display = "none";
document.getElementById("page").style.display = "inline-block";
}
if (sessionStorage.tab > 0){
document.getElementById("rev").style.display = "inline-block";
}
if(sessionStorage.tab < sessionStorage.page){
document.getElementById("page").style.display = "none";
document.getElementById("tab").style.display = "inline-block";
}
function Page() {
  sessionStorage.page = Number(sessionStorage.page)+1;
  sessionStorage.tab = Number(sessionStorage.tab)+1;
}
function Rev(){
    
  sessionStorage.tab = Number(sessionStorage.tab)-1;
  window.history.back();
}
function Tab(){
  sessionStorage.tab = Number(sessionStorage.tab)+1;
  window.history.forward();
  
}
function Reset(){
    sessionStorage['page'] = 0;
    sessionStorage['tab'] = 0;
}\n
"""

    text += (
        "function openForm(s, b, a, r){\n"
        "CKEDITOR.replace( 'msgbody', {height: 500, contentsCss: \"body {font-size: 20px;}\"});\n"
        "CKEDITOR.config.readOnly = false;\n"
        "CKEDITOR.config.allowedContent = 'img a h1 h2 h3 p blockquote strong em div{margin-left, padding, background-color};' + 'a[!href];' + 'img(left,right)[!src,alt,width,height];' + 'div[!contenteditable, !style];' + 'p[!contenteditable];';\n"
        "if ((s || b || a) && !r){\n"
        "var forward = '--------- Forwarded message ---------- <br>';\n"
        "var date = 'Date: " + email_date + "<br>';\n"
        "var from = 'From: " + email_from + "<br>';\n"
        "var subject = 'Subject: " + email_subject + "<br>';\n"
        "var to = 'To: " + userEmail + "<br>';\n"
        "var att = a;\n"
        "var forward = forward.concat(from, date, subject, to, b, a);\n"
        "CKEDITOR.instances.msgbody.setData(forward);\n"
        "document.getElementById(\"subject\").value = s; \n"
        "}\n"
        "if(r){\n"
        "var reply = `<p contenteditable='false'> On " + email_date + " " + email_from + " wrote: </p><div contenteditable='false' style=\"margin-left: 20px; padding: 10px; background-color: rgba(0,0,220,.1);\">` + b + `</div><br>`;\n"
        "document.getElementById(\"sendto\").value = \'" + userEmail + "\'; \n"
        "document.getElementById(\"subject\").value = s; \n"
        "CKEDITOR.instances.msgbody.setData(reply);\n"
        "}\n"
        "document.getElementById(\"myForm\").style.display = \"block\";\n"
        "b = '';\n"
        "}\n"
        "function closeForm() {\n"
        
        "document.getElementById(\"myForm\").style.display = \"none\";\n"
        "}\n"

        )



    text += (
        "</script>\n"
        "</body>\n"
        "</html>\n")
    htmlFile = open("templates/inbox.html", 'w+')
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

@app.route('/pageforward', methods=['GET', 'POST'])
def pageforward():
    index = request.form['page']
    search = None
    index = int(index)

    loadInbox(search, index)
    return render_template('inbox.html')

def encrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(token)

@app.route('/savenote', methods=['POST', 'GET'])
def savenote():
    if request.method == 'POST':
        title = request.form.get('Title')
        message = request.form.get('Message')
        if path.exists("notes.txt"):
            note = open("notes.txt", "r")
            lines = note.readlines()
            note.close()

            note = open("notes.txt", "w")
            for line in lines:
                if line.strip("\n") != "eon":
                    note.write(line)

            note.close()


        note = open("notes.txt", "a")
        note.write("T-" + title)
        note.write("\n")
        note.write("B-" + message + "\n")
        note.write("eon")
        note.write("\n\n")
        note.close()
        return redirect('/notes')



# starting web app
if __name__ == '__main__':
    if len(sys.argv) == 2 and str(sys.argv[1]) == "travisTest":
        travisTest()

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    #os.system("start \"\" http://" + ip_address + ":5000")
    attempts = 5

        #webbrowser.open('http://localhost:5000')
    app.secret_key = b'THISisGROUP2//\\\\'
    app.run(host='0.0.0.0', debug=True)  # Launches server on main computer's ipv4 address:5000
