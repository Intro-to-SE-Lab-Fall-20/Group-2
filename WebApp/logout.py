@app.route('/logout')
def logout():
    os.remove('userCredentials.txt')
    return redirect('/')
