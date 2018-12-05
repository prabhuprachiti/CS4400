from flask import session, request

def logout():
    if request.method == 'GET' or request.method == 'POST':
        session.clear()
        return 'success'
    return 'error'
