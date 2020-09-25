from flask import Flask, render_template
from flask import Flask, request

app = Flask(__name__)

port=5000

@app.route('/', methods=['GET', 'POST'])
def login():

	if request.method == 'POST':
		print(request.form['email'])
		return inbox()
	else:
		return render_template('login.html')

@app.route('/', methods=['POST', 'GET'])
def inbox():
	return render_template('inbox.html')


@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
	print("HERE4")
	if request.method == 'POST':
		print("HERE6")
		toEmail = request.form['toemail']
		subject = request.form['subject']
		msg = request.form['msgbody']
		print(toEmail, " ", subject, " ", msg)
		return sendemail(toEmail, subject, msg)
	else:
		print("HERE5")
		return render_template('sendmail.html')










def sendemail(toEmail, subject, msg):
	print(toEmail, " ", subject, " ", msg)
	return inbox()



if __name__ == '__main__':
   app.run(host = '0.0.0.0')  # Launches server on main computer's ipv4 address:5000