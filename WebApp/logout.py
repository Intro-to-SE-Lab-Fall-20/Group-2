
import os

#copy and paste right above if __name__ ==
# in main.py
@app.route('/logout')
def logout():
    os.remove('userCredentials.txt')
    return redirect('/')


#copy and paste into line 149 in main.py
"<form action=\"logout\">"
"<button class=\"btn btn-lg btn-primary btn-block\" type=\"submit\">Logout</button>\n"
"</form>\n"


