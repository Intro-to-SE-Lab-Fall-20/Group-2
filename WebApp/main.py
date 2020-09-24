from flask import Flask, render_template

app = Flask(__name__)

port=5000

@app.route('/')
def login():
   return render_template('login.html')


@app.route('/inbox')
def inbox():
   return render_template('inbox.html')

if __name__ == '__main__':
   app.run(host = '0.0.0.0')  # Launches server on main computer's ipv4 address:5000