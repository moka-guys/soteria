import datetime
import forms
import models
import os
import re
from soteria import db, login_manager, mail, create_app
import subprocess
import sys
from decorators import check_confirmed
from flask import render_template, request, redirect, url_for, abort, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

soteria = create_app()

@soteria.before_request
def before_request():
    session.permanent = True

@login_manager.user_loader
def load_user(UserID):
    return models.User.query.get(int(UserID)) # Fetch the user from the database

# Register route
@soteria.route("/register/", methods=["GET", "POST"], strict_slashes=False)
def register():
    form = forms.register_form()
    if form.validate_on_submit():
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


@soteria.route('/resend_confirmation')
@login_required
def resend_confirmation():
    send_email(create_confirmation_email(current_user.Email))
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))


# registration confirmation using email link
@soteria.route('/confirm/<token>')
def confirm_email(token):
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


@soteria.route('/unconfirmed')
def unconfirmed():
    if current_user.Confirmed:
        return redirect(url_for('samplesheet_upload'))
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html', pp_version=git_tag(), user=get_username())

# Password reset request route
@soteria.route("/password_reset_request/", methods=["GET", "POST"], strict_slashes=False)
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('samplesheet_upload'))
    form = forms.ResetPasswordRequestForm()
    if form.validate_on_submit():
        user =  models.User.query.filter_by(Email=form.email.data).first()
        if user:
            send_email(create_password_reset_email(form.email.data))
            flash('Check your email for the instructions to reset your password', "success")
            return redirect(url_for('login'))
    return render_template("login.html", form=form, app_version=git_tag())


# Password reset route
@soteria.route("/password_reset/<token>", methods=["GET", "POST"], strict_slashes=False)
def password_reset(token):
    email = confirm_token(token)
    form = forms.password_reset_form()
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
@soteria.route('/', methods=['GET','POST'], strict_slashes=False)
def login():
    form = forms.login_form()

    if current_user.is_authenticated:
        form.email.data = current_user.Email

    if request.method == 'GET' and current_user.is_authenticated:
        return redirect(url_for('samplesheet_upload'))

    if request.method == 'POST':
        if form.validate_on_submit():
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
                        newlogin = models.Logins(
                            UserID = current_user.UserID
                        )
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
@soteria.route("/logout")
@login_required
@check_confirmed
def logout():
    logout_user()
    flash('Logged out successfully.', "success")
    return redirect(url_for('login'))


# samplesheet upload route
@soteria.route('/samplesheet_upload', methods=['GET','POST'])
@login_required
@check_confirmed
def samplesheet_upload():
    """
    Uploads file to an upload directory, runs verification checks on the file and removes the file or moves it to a
    passed directory depending on the outputs of the checks. Outputs of checks displayed on the rendered template.
    """
    if request.method == 'GET':
        return render_template('samplesheet_upload.html', app_version=git_tag(), user=get_username())
    elif request.method == 'POST':
        ss_dir = soteria.config['SS_DIR']

        # mount the automated scripts folder and the samplesheets folder
        # put the flask app within the docker container

        uploaded_file = request.files['file']
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

    automated_scripts = soteria.config['AUTOMATED_SCRIPTS']

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
        else:
            messages.append({"Pass": ss_verification_results[key][1]})
    return result, instructions, colour, messages

def check_file_selected(filename):
    if filename != '':
        return True

def check_correct_file_ending(filename):
    if re.compile("^.*\.csv$").match(filename):
        return True

def check_new_file(samplesheet_path):
    if not os.path.exists(samplesheet_path):
        return True



def generate_token(email):
    serializer = URLSafeTimedSerializer(soteria.config['SECRET_KEY'])
    return serializer.dumps(email, salt=soteria.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=1800):
    # token expires after 30 minutes
    serializer = URLSafeTimedSerializer(soteria.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=soteria.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_email(msg):
    mail.send(msg)

def create_password_reset_email(email):
    token = generate_token(email)
    password_reset_url = url_for('password_reset', token=token, _external=True)

    msg = Message()
    msg.subject = "Soteria password reset link"
    msg.recipients = [email]
    msg.sender = "moka.alerts@gstt.nhs.uk"
    msg.html = render_template('email.html', password_reset_url=password_reset_url)
    Thread(target=send_email, args=(soteria, msg)).start()
    return msg

def create_confirmation_email(email):
    token = generate_token(email)
    confirm_url = url_for('confirm_email', token=token, _external=True)

    msg = Message()
    msg.subject = "Please confirm your email"
    msg.recipients = [email]
    msg.sender = 'moka.alerts@gstt.nhs.uk'
    msg.html = render_template('email.html', token=token, confirm_url=confirm_url)
    Thread(target=send_email, args=(soteria, msg)).start()
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
    if current_user.is_authenticated:
        user = current_user.FirstName + " " + current_user.Surname
    else:
        user = False
    return user


if __name__ == "__main__":
    soteria.debug = True
    soteria.run(host='0.0.0.0', port=3333)