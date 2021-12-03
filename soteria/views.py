
import sys
import subprocess
import imghdr
import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from werkzeug.utils import secure_filename
from collections import OrderedDict
from . import app

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/', methods=['POST'])
def upload_files():
    """
    Uploads file to an upload directory, runs verification checks on the file and removes the file or moves it to a
    passed directory depending on the outputs of the checks. Outputs of checks displayed on the rendered template.
    """
    if app.config['TEST']:
        PASSED_PATH = app.config['TEST_PASSED_PATH']
        AUTOMATED_SCRIPTS = '/usr/local/src/mokaguys/development_area/automate_demultiplex'
    else:
        PASSED_PATH = app.config['LIVE_PASSED_PATH']
        AUTOMATED_SCRIPTS = '/usr/local/src/mokaguys/apps/automate_demultiplex/'

    sys.path.append(AUTOMATED_SCRIPTS)
    import samplesheet_verifier
    import automate_demultiplex_config

    print('========')
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(app.config['UPLOAD_PATH'])
    messages = []
    # assign empty variables so if 'submit' is clicked with no input file the webpage doesn't break
    if filename != '':
        filepath = os.path.join(app.config['APPLICATION_ROOT'], app.config['UPLOAD_PATH'], filename)
        print("Filepath: " + filepath)
        uploaded_file.save(filepath)
        ss_verification_results = samplesheet_verifier.run_ss_checks(filepath)
        if any(ss_verification_results[key][0]==False for key in ss_verification_results):
            result = "File failed checks (NOT uploaded):"
            instructions = "Please fix the below errors, then reupload the samplesheet!"
            os.remove(filepath)
            colour = "red"
        else:
            result = "File passed checks (uploaded):"
            instructions = "No further actions required"
            colour = "green"
            path = os.path.join(app.config['APPLICATION_ROOT'], PASSED_PATH)
            if not os.path.exists(path):
                os.mkdir(path)
            shutil.move(filepath, os.path.join(path, filename))
        for key in ss_verification_results:
            if not ss_verification_results[key][0]:
                messages.append({"ERROR": ss_verification_results[key][1]})
            else:
                messages.append({"Pass": ss_verification_results[key][1]})
    else:
        result = "No file provided"
        instructions = "Please upload a file"
        colour = "red"
    return render_template('index.html', result=result, instructions = instructions, messages=messages,
                           app_version=git_tag(), txt_colour=colour, uploaded_file=filename)