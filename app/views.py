# app/views.py
from app import app, decorators, forms, models, db, mail
import datetime
import os
import re
import subprocess
import sys
from flask import render_template, request, redirect, url_for, abort, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

@app.before_request
def before_request():
    """Sets session to permanent which uses lifetime specified in config"""
    session.permanent = True

@app.login_manager.user_loader
def load_user(UserID):
    """Returns user ID from the database"""
    return models.User.query.get(int(UserID))

# Register route
@app.route("/register/", methods=["GET", "POST"], strict_slashes=False)
def register():
    """Register route - registers user in database, sends confirmation email"""
    form = forms.RegisterForm(request.form)
    # print(form)
    # print(form.validate_on_submit())
    if request.method == 'POST' and form.validate_on_submit():
        try:
            newuser = models.User(
                FirstName=form.firstname.data,
                Surname=form.surname.data,
                Email=form.email.data,
                PHash=generate_password_hash(form.pwd.data),
                Confirmed=False
            )

            db.session.add(newuser)
            db.session.commit()

            login_user(newuser)

            send_email(create_confirmation_email(newuser.Email))
            flash('A confirmation email has been sent via email.', 'success')

        except Exception as e:
            flash(e, "danger")
        return redirect(url_for("unconfirmed"))

    return render_template("login.html", form=form, app_version=git_tag())


@app.route('/resend_confirmation')
@login_required
def resend_confirmation():
    """Resend email confirmation"""
    send_email(create_confirmation_email(current_user.Email))
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))


# registration confirmation using email link
@app.route('/confirm/<token>')
def confirm_email(token):
    """Confirm email using token generated by URLSafeTimedSerializer"""
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = models.User.query.filter_by(Email=email).first_or_404()
    if user.Confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.Confirmed = True
        user.ConfirmedOn = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Account has now been successfully created', 'success')
    return redirect(url_for('login'))


@app.route('/unconfirmed')
def unconfirmed():
    """Check if user is confirmed. If yes redirect to samplesheet_upload page, if no redirect to unconfirmed page"""
    if hasattr(current_user, 'Confirmed'):
        if current_user.Confirmed:
            return redirect(url_for('samplesheet_upload'))
    else:
        return redirect(url_for('login'))
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html', pp_version=git_tag(), user=get_username())


# Password reset request route
@app.route("/password_reset_request/", methods=["GET", "POST"], strict_slashes=False)
def password_reset_request():
    """Send password reset email"""
    if current_user.is_authenticated:
        return redirect(url_for('samplesheet_upload'))
    form = forms.ResetPasswordRequestForm(request.form)
    if form.validate_on_submit():
        user =  models.User.query.filter_by(Email=form.email.data).first()
        if user:
            send_email(create_password_reset_email(form.email.data))
            flash('Check your email for the instructions to reset your password', "success")
            return redirect(url_for('login'))
    return render_template("login.html", form=form, app_version=git_tag())


# Password reset route
@app.route("/password_reset/<token>", methods=["GET", "POST"], strict_slashes=False)
def password_reset(token):
    """Confirm email using URLSafeTimedSerializer then save new password to database. Send email confirmation"""
    email = confirm_token(token)
    form = forms.PasswordResetForm(request.form)
    if form.validate_on_submit():
        try:
            user =  models.User.query.filter_by(Email=email).first()
            # record the login in the database
            user.PHash = generate_password_hash(form.pwd.data)
            user.Confirmed = False
            db.session.add(user)
            db.session.commit()

            user = models.User.query.filter_by(Email=user.Email).first()
            send_email(create_confirmation_email(user.Email))
            flash('A confirmation email has been sent via email.', 'success')
            login_user(user)
        except Exception as e:
            flash(e, "danger")
        return redirect(url_for("unconfirmed"))

    return render_template("login.html", form=form, app_version=git_tag())


# login route (& home route)
@app.route('/', methods=['GET','POST'], strict_slashes=False)
def login():
    """Login page. Log in user and records login event in database table. Redirect to samplesheet_upload page."""
    form = forms.LoginForm(request.form)

    if current_user.is_authenticated:
        form.email.data = current_user.Email

    if request.method == 'GET' and current_user.is_authenticated:
        return redirect(url_for('samplesheet_upload'))

    if request.method == 'POST' and form.validate_on_submit():
            # Login and validate the user.
            try:
                # retrieves the user from the database and from this the hashed password can be accessed
                user = models.User.query.filter_by(Email=form.email.data).first()
                if not user:
                    flash("This email address is not registered. Please create an account.", "danger")
                else:
                    if check_password_hash(user.PHash, form.pwd.data):
                        login_user(user)
                        flash('Logged in successfully.', "success")

                        # record the login in the database
                        newlogin = models.Logins(UserID = current_user.UserID)
                        db.session.add(newlogin)
                        db.session.commit()

                        # redirects to samplesheet page upon login
                        return redirect(url_for('samplesheet_upload'))
                    else:
                        flash("Invalid Username or password!", "danger")
            except Exception as e:
                flash(e, "danger")
    # redirects to login page from base url
    return render_template('login.html', form=form, app_version=git_tag(), user=get_username())


# logout route
@app.route("/logout")
@login_required
@decorators.check_confirmed
def logout():
    """Logout user"""
    logout_user()
    flash('Logged out successfully.', "success")
    return redirect(url_for('login'))


# samplesheet upload route
@app.route('/samplesheet_upload', methods=['GET','POST'])
@login_required
@decorators.check_confirmed
def samplesheet_upload():
    """
    Upload file to upload directory, runs verification checks on the file and removes the file if it fails the checks.
    Outputs of checks displayed on the rendered template.
    """
    if request.method == 'GET':
        return render_template('samplesheet_upload.html', app_version=git_tag(), user=get_username())
    elif request.method == 'POST':
        ss_dir = app.config['SS_DIR']
        uploaded_file = request.files['file']
        # returns a secure versio of the filename
        filename = secure_filename(uploaded_file.filename)
        messages = []
        # assign empty variables so if 'submit' is clicked with no input file the webpage doesn't break
        samplesheet_path = os.path.join(ss_dir, filename)

        # check if file supplied, file ends in .csv, and file doesn't already exist in samplesheet folder
        # if passes save to samplesheet folder
        file_selected = check_file_selected(filename)
        correct_file_ending = check_correct_file_ending(filename)
        new_file = check_new_file(samplesheet_path)

        if file_selected and correct_file_ending and new_file:
            uploaded_file.save(samplesheet_path)
            # collect results from samplesheet verification to pass to template
            result, instructions, colour, messages = verify_samplesheet(samplesheet_path, messages)

        else:
            colour = "red"
            if not file_selected:
                result = "No file provided"
                instructions = "Please upload a file"
            elif not correct_file_ending:
                result = "Incorrect file ending - must be .csv: "
                instructions = "Please upload a file in the correct format"
            elif not new_file:
                result = "Samplesheet already uploaded"
                instructions = "No further actions required"
    return render_template('samplesheet_upload.html', result=result, instructions=instructions, messages=messages,
                           app_version=git_tag(), txt_colour=colour, uploaded_file=filename,
                           user=get_username())


def verify_samplesheet(samplesheet_path, messages):
    """Perform samplesheet verification checks using samplesheet verifier script from the automated scripts. Logs
    upload in database. Returns result, user instructions, message colour and messages to display to user."""
    automated_scripts = app.config['AUTOMATED_SCRIPTS']

    sys.path.append(automated_scripts)
    import samplesheet_verifier
    import automate_demultiplex_config

    ss_verification_results = samplesheet_verifier.run_ss_checks(samplesheet_path)

    if any(ss_verification_results[key][0] == False for key in ss_verification_results):
        result = "File failed checks (NOT uploaded):"
        instructions = "Please fix the below errors, then reupload the samplesheet!"
        os.remove(samplesheet_path)
        #  "docker run --rm -v `pwd`:`pwd` -w `pwd` -it {}:{} python
        #  os.remove(samplesheet_path)".format(app.config['DOCKER_REPOSITORY'], app.config['DOCKER_TAG'])
        colour = "red"
    else:
        result = "File passed checks (uploaded):"
        instructions = "No further actions required"
        colour = "green"

        # record the upload in database
        newupload = models.FileUpload(
            FilePath=samplesheet_path,
            UserID=current_user.UserID
        )

        db.session.add(newupload)
        db.session.commit()

    # create detailed pass/error messages for webpage
    for key in ss_verification_results:
        if not ss_verification_results[key][0]:
            messages.append({"ERROR": ss_verification_results[key][1]})
            messages.append({"ERROR": ss_verification_results[key][1]})
        else:
            messages.append({"Pass": ss_verification_results[key][1]})
    return result, instructions, colour, messages


def check_file_selected(filename):
    """Checks file has been supplied"""
    if filename != '':
        return True


def check_correct_file_ending(filename):
    """Checks filename ends in csv"""
    if re.compile("^.*\.csv$").match(filename):
        return True


def check_new_file(samplesheet_path):
    """Checks samplesheet doesn't already exist"""
    if not os.path.exists(samplesheet_path):
        return True


def generate_token(email):
    """Generate email token using URLSafeTimedSerializer"""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=1800):
    """Deserializes email token using URLSafeTimedSerializer"""
    # token expires after 30 minutes
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(msg):
    """Send email"""
    mail.send(msg)


def create_password_reset_email(email):
    """Create password reset email using created token"""
    token = generate_token(email)
    password_reset_url = url_for('password_reset', token=token, _external=True)

    msg = Message()
    msg.subject = "Soteria password reset link"
    msg.recipients = [email]
    msg.sender = "moka.alerts@gstt.nhs.uk"
    msg.html = render_template('email.html', password_reset_url=password_reset_url)
    Thread(target=send_email, args=(app, msg)).start()
    return msg


def create_confirmation_email(email):
    """Create confirmation email using created token"""
    token = generate_token(email)
    confirm_url = url_for('confirm_email', token=token, _external=True)

    msg = Message()
    msg.subject = "Please confirm your email"
    msg.recipients = [email]
    msg.sender = 'moka.alerts@gstt.nhs.uk'
    msg.html = render_template('email.html', token=token, confirm_url=confirm_url)
    Thread(target=send_email, args=(app, msg)).start()
    return msg


def git_tag():
    """
    Return script release version number by reading directly from repository.
        :return: (str) returns version number of current script release
    Execute command via subprocess that prints git tags for git repository (e.g. v22-3-gccfd) and extracts version
    number (create array "a" using awk, split on "-" and print first element of array). Return standard out, removing
    newline characters
    """
    cmd = "git -C " + os.path.dirname(os.path.realpath(__file__)) + \
          " describe --tags | awk '{split($0,a,\"-\"); print a[1]}'"
    proc = subprocess.Popen([cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    return out.rstrip().decode('utf-8')


def get_username():
    """Return username for authenticated user, false for unauthenticated"""
    if current_user.is_authenticated:
        user = current_user.FirstName + " " + current_user.Surname
    else:
        user = False
    return user