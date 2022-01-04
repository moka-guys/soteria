import sys
import subprocess
import imghdr
import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from collections import OrderedDict
import functools
from . import forms
from . import app

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

@app.route('/', methods=['GET'])
def index():
    # redirects to login page from base url
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = forms.LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return abort(400)
        # redirects to samplesheet page upon login
        return redirect(next or url_for('samplesheet_page'))
    return render_template('login.html', form=form)

@app.route('/samplesheet_upload', methods=['GET'])
@login_required
def samplesheet_page():
    return render_template('samplesheet_upload.html')

@app.route('/samplesheet_upload', methods=['POST'])
@login_required
def samplesheet_upload():
    """
    Uploads file to an upload directory, runs verification checks on the file and removes the file or moves it to a
    passed directory depending on the outputs of the checks. Outputs of checks displayed on the rendered template.
    """
    ss_dir = app.config['SS_DIR']
    automated_scripts = app.config['AUTOMATED_SCRIPTS']

    sys.path.append(automated_scripts)
    import samplesheet_verifier
    import automate_demultiplex_config


    # mount the automated scripts folder and the samplesheets folder
    # put the flask app within the docker container

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    messages = []
    # assign empty variables so if 'submit' is clicked with no input file the webpage doesn't break
    samplesheet_path = os.path.join(ss_dir, filename)
    # if file has been supplied and file doesn't already exist in samplesheet folder, save to folder
    if filename != '' and not os.path.exists(samplesheet_path):
        uploaded_file.save(samplesheet_path)

        ss_verification_results = samplesheet_verifier.run_ss_checks(samplesheet_path)
        if any(ss_verification_results[key][0]==False for key in ss_verification_results):
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
        for key in ss_verification_results:
            if not ss_verification_results[key][0]:
                messages.append({"ERROR": ss_verification_results[key][1]})
            else:
                messages.append({"Pass": ss_verification_results[key][1]})
    else:
        if filename=='':
            result = "No file provided"
            instructions = "Please upload a file"
        elif os.path.exists(samplesheet_path):
            result = "Samplesheet already uploaded"
            instructions = "No further actions required"
        colour = "red"
    return render_template('samplesheet_upload.html', result=result, instructions = instructions, messages=messages,
                           app_version=git_tag(), txt_colour=colour, uploaded_file=filename)