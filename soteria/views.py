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
    print(listdir)
    ss_dir = app.config['SS_DIR']
    automated_scripts = app.config['AUTOMATED_SCRIPTS']

    sys.path.append(automated_scripts)
    import samplesheet_verifier
    import automate_demultiplex_config


    # mount the automated scripts folder and the samplesheets folder
    # put the flask app within the docker container

    print('========')
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(type(uploaded_file))
    messages = []
    # assign empty variables so if 'submit' is clicked with no input file the webpage doesn't break
    if filename != '':
        samplesheet_path = os.path.join(ss_dir, filename)
        print("Filepath: " + samplesheet_path)
        # save the file to the samplesheet folder
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
        result = "No file provided"
        instructions = "Please upload a file"
        colour = "red"
    return render_template('index.html', result=result, instructions = instructions, messages=messages,
                           app_version=git_tag(), txt_colour=colour, uploaded_file=filename)