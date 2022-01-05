import sys
import re
import subprocess
import os
import imghdr
import shutil
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, login_user, logout_user, current_user
from is_safe_url import is_safe_url
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from collections import OrderedDict
import functools
import soteria
import forms
import models
from soteria import db, login_manager

soteria = soteria.create_app()

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
        user = current_user.firstname + " " + current_user.surname
    else:
        user = False
    return user


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id)) # Fetch the user from the database

# Register route
@soteria.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = forms.register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            firstname = form.firstname.data
            surname = form.surname.data

            newuser = models.User(
                firstname=firstname,
                surname=surname,
                email=email,
                pwd=generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash("Account Succesfully created", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(e, "danger")

    return render_template("login.html", form=form, app_version=git_tag())

# login route (& home route)
@soteria.route('/', methods=['GET','POST'], strict_slashes=False)
def login():
    form = forms.login_form()
    user = get_username()

    if current_user.is_authenticated:
        form.email.data = current_user.email

    if request.method == 'GET' and current_user.is_authenticated:
        return redirect(url_for('samplesheet_upload'))

    if request.method == 'POST':
        if form.validate_on_submit():
        # Login and validate the user.
             try:
                # retrieves the user from the database and from this the hashed password can be accessed
                user = models.User.query.filter_by(email=form.email.data).first()
                if check_password_hash(user.pwd, form.pwd.data):
                    login_user(user)
                    flash('Logged in successfully.')

                    # record the login in the database
                    newlogin = models.Logins(
                        user_email=form.email.data
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
    return render_template('login.html', form=form, app_version=git_tag(), user=user)

# logout route
@soteria.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# samplesheet upload route
@soteria.route('/samplesheet_upload', methods=['GET','POST'])
@login_required
def samplesheet_upload():
    """
    Uploads file to an upload directory, runs verification checks on the file and removes the file or moves it to a
    passed directory depending on the outputs of the checks. Outputs of checks displayed on the rendered template.
    """
    user = get_username()
    if request.method == 'GET':
        return render_template('samplesheet_upload.html', app_version=git_tag(), user=user)
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
                           user=user)

def check_file_selected(filename):
    if filename != '':
        return True

def check_correct_file_ending(filename):
    if re.compile("^.*\.csv$").match(filename):
        return True

def check_new_file(samplesheet_path):
    if not os.path.exists(samplesheet_path):
        return True

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
        newupload = models.File_upload(
            user_email=current_user.email,
            file=samplesheet_path
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


if __name__ == "__main__":
    soteria.debug = True
    soteria.run(host='0.0.0.0', port=3333)