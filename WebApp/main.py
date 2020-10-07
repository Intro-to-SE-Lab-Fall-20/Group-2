from flask import Flask, render_template
from flask import Flask, request
import smtplib, ssl #server library
import email
import imghdr
from email.message import EmailMessage
import poplib
from email import parser

app = Flask(__name__)

emailport = 465 #Gmail port

context = ssl.create_default_context() #idk what this does

port=5000

@app.route('/', methods=['GET', 'POST'])
def login():

	if request.method == 'POST': #renders login.html until form is submitted
		global userEmail	#when submitted takes in these values
		userEmail = request.form['email']
		global userPsswrd     #global because they are needed in another function
		userPsswrd = request.form['password']  #requests the object with name 'password'
		return login2(userEmail, userPsswrd)
	else:
		return render_template('login.html')

def login2(email, password):
	try:
		with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
			server.login(email, password) #connecting to server and logging in(checks creds)
			return inbox()
	except:
		return render_template('login.html')

@app.route('/', methods=['POST', 'GET'])
def inbox():
	return render_template('inbox.html') #when sendmail button is clicked it performs the action(sendmail)


@app.route('/sendmail', methods=['GET', 'POST']) #"/sendmail" is the action
def sendmail():
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
		return sendemail(newMessage)
	else:
		return render_template('sendmail.html')



def sendemail(newMessage):
	with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
		server.login(userEmail, userPsswrd)  #for somereason i had to log in again before sending
		server.send_message(newMessage)
	#print(toEmail, " ", subject, " ", msg) #prints to terminal
	return inbox() #goes back to inbox after sending



if __name__ == '__main__':
   app.run(host = '0.0.0.0')  # Launches server on main computer's ipv4 address:5000