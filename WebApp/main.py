from flask import Flask, render_template
from flask import Flask, request
import smtplib, ssl #server library

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
	with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
		server.login(email, password) #connecting to server and logging in(checks creds)
		return inbox()

@app.route('/', methods=['POST', 'GET'])
def inbox():
	return render_template('inbox.html') #when sendmail button is clicked it performs the action(sendmail)


@app.route('/sendmail', methods=['GET', 'POST']) #"/sendmail" is the action
def sendmail():
	if request.method == 'POST':
		toEmail = request.form['toemail']
		subject = request.form['subject'] #not really needed
		msg = request.form['msgbody']
		return sendemail(toEmail, subject, msg)
	else:
		return render_template('sendmail.html')


def sendemail(toEmail, subject, msg):
	with smtplib.SMTP_SSL("smtp.gmail.com", emailport, context = context) as server:
		server.login(userEmail, userPsswrd)  #for somereason i had to log in again before sending
		server.sendmail(userEmail, toEmail, msg)
	print(toEmail, " ", subject, " ", msg) #prints to terminal
	return inbox() #goes back to inbox after sending



if __name__ == '__main__':
   app.run(host = '0.0.0.0')  # Launches server on main computer's ipv4 address:5000