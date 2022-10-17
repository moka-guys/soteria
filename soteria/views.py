import imghdr
import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from . import app 

def validate_image(stream):
    """Your validation logic should go into a similar validation function"""
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    print('========')

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        valid_extension = file_ext in app.config['UPLOAD_EXTENSIONS']
        # if not valid_extension or file_ext != validate_image(uploaded_file.stream):
        #     abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        ## NSWHP demo
        validation_command = 'python3 .lint/validator/validate.py --samplesheet uploads/{0}'.format(filename)
        # try:
        #     validation_results = subprocess.run (
        #         [validation_command], shell=True
        #     )
        try:
            validation_results = subprocess.check_output (
                [validation_command], shell=True
            )
        except subprocess.CalledProcessError as e:
            return "An error occurred while trying to fetch task status updates."
            if e.output.startswith('error: {'):
                error = json.loads(e.output[7:]) # Skip "error: "
                print(error['code'])
                print(error['message'])
        return 'Samplesheet Validation: %s' %(validation_results)
    return redirect(url_for('index'))

@app.route('/validator', methods=['POST'])
def csv_validate():
    print('========')

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(filename)
    