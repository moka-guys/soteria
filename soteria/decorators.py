# soteria/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def check_confirmed(func):
    """ Checks whether the user has confirmed their account (checks database)"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.Confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function