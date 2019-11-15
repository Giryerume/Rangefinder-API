import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from rangefinder_api import *
import cv2

UPLOAD_FOLDER = 'imgs/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
TARGET_HEIGHT = MARKER_1_HEIGHT
CAL_DIST = 1000

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        TARGET_HEIGHT = request.form['height']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "raw.jpg"))
            return redirect('/calculate')
    return '''
    <!doctype html>
    <title>Rangefinder</title>
    <h1>Rangefinder</h1>
    <form method=post enctype=multipart/form-data>
        <h3>Upload image</h3>
        <input type=file name=file>
        <h3>Target height (mm)</h3>
        <input type=text name=height style="width:48px;">
        <input type=submit value=Upload>
    </form>
    '''

@app.route('/calibrate', methods=['GET', 'POST'])
def calibration():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        TARGET_HEIGHT = request.form['height']
        CAL_DIST = request.form['distance']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "cal.jpg"))
            return redirect('/')
    return '''
    <!doctype html>
    <title>Rangefinder</title>
    <h1>Rangefinder - Calibration</h1>
    <form method=post enctype=multipart/form-data>
        <h3>Upload calibration image</h3>
        <input type=file name=file>
        <h3>Target known distance (mm)</h3>
        <input type=text name=distance style="width:108px;">
        <h3>Target height (mm)</h3>
        <input type=text name=height style="width:48px;">
        <input type=submit value=Upload>
    </form>
    '''

from flask import send_from_directory

@app.route('/calculate')
def calculate():
    im = cv2.imread('imgs/uploads/raw.jpg')
    im = resize(im, 20)
    cal = cv2.imread('imgs/uploads/cal.jpg')
    cal = resize(cal, 20)
    r = rangefinder(im, TARGET_HEIGHT, calibrate(cal, CAL_DIST, TARGET_HEIGHT))
    cv2.imwrite('imgs/uploads/prcssd.jpg', r, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return send_from_directory(app.config['UPLOAD_FOLDER'], "prcssd.jpg")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True,use_reloader=True)
