from flask import Flask, render_template, request, redirect
import smtplib, ssl #server library

app = Flask(__name__)

emailport = 465 #Gmail port

context = ssl.create_default_context()

@app.route('/', methods=['GET', 'POST'])
def login():

	if request.method == 'POST': #when form is submitted, it collects the data and authenticates
		global userEmail, userPassword
		userEmail = request.form['email'] #requests the object with name 'email'
		userPassword = request.form['password'] #requests the object with name 'password'
		authenticate() #check creds
		return redirect('/inbox')  # after login, go to inbox

	else:
		return render_template('login.html')  #renders login.html until form is submitted


def authenticate():
	with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context=context) as server:
		server.login(userEmail, userPassword)  # connecting to server and logging in (checks creds)


@app.route('/inbox', methods=['POST', 'GET'])
def inbox():

	if request.method == 'POST': #when form is submitted, it performs the only action (going to send an email)
		return redirect('/sendmail')

	else:
		return render_template('inbox.html') #renders inbox.html until form is submitted


@app.route('/sendmail', methods=['GET', 'POST'])
def sendMail():
	if request.method == 'POST': #when form is submitted, email is sent
		toEmail = request.form['toemail']
		subject = request.form['subject'] #not really needed
		msg = request.form['msgbody']
		return sendMail(toEmail, subject, msg)
	else:
		return render_template('sendmail.html') #renders sendmail.html until form is submitted


def sendMail(toEmail, subject, msg):
	with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
		server.login(userEmail, userPassword)  #for somereason i had to log in again before sending
		server.sendmail(userEmail, toEmail, msg)
	print("To: ", toEmail, ";", "Subject: ", subject, ";", "Message: ", msg) #prints to terminal
	return redirect('/inbox') #goes back to inbox after sending


if __name__ == '__main__':
   app.run(host = '0.0.0.0')  #launches server on main computer's ipv4 address:5000
