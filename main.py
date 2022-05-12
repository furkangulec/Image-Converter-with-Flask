from pandas import wide_to_long
from regex import B
import requests

from flask import Flask, Response, send_file, render_template, request, redirect, abort, flash, url_for, make_response, session, escape
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
import os


#region Flask settings

app = Flask(__name__)
app.config['ENV'] = "development"
app.config['DEBUG'] = True

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'dib'}

#endregion Flask settings

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#region Download image from url
def downloadImage(url):
    resp = requests.get(url)
    return Image.open(BytesIO(resp.content))
#endregion Download image from url

#region Draw text on the image
def drawText(image, text, width):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("static/fonts/arialbd.ttf", int(width/40))
    draw.text((0, 0), text, (255, 0, 0), font=font)
    return image
#endregion Draw text on the image


def converter(img, convert_to):

    rendered_image = img.convert("RGB")
 
    #Draw text on the image
    drawText(rendered_image, "FURKANGULEC", width=rendered_image.width)

    buffer = BytesIO()
    rendered_image.save(buffer, format=convert_to)
    buffer.seek(0)
    path = base64.b64encode(buffer.getvalue())

    return path, buffer


@app.route('/render/<path:url>', methods=['POST', 'GET'])
def render(url):

    try:
        if session['convert_to'] != "":
            convert_to = session['convert_to']
    except Exception as ex:
         print(f"Session Error [{render.__name__}]: ", ex)
         convert_to = "jpeg"

    try:
        img = downloadImage(url)
    except Exception as e:
        try:
            if session["uploaded"] == True:
                print("There is a file")
                session.pop('uploaded', None)
                img = Image.open("static/upload/" + url)

        except Exception as ex:
            print("There is no file")
            error_message = "Please make sure that URL is correct and image is available!"
            return render_template("/homepage.html", error_message = error_message, converted = False)

    path, buffer = converter(img, convert_to)

    if request.method == "POST":
        return send_file(buffer, mimetype='image/' + convert_to)
    else:
        return render_template("/homepage.html", path = path.decode('ascii'), converted = True, url = url)







@app.route('/render', methods=['POST', 'GET'])
def r():
 
    #If someone comes to page with POST method
    if request.method == "POST":   
        #If someone click convert button
        if request.form['process'] == 'Convert':
            convert_to = request.form.get('convert_to')
            session['convert_to'] = convert_to
            url = request.form.get('url')
            
            #If url exists
            if url:
                return redirect(url_for('render', url = url))
              
            #If url does not exist
            if 'file' in request.files:
                        
                image = request.files['file']
                if allowed_file(image.filename):
                    filename = "uploaded." + convert_to
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    error_message = "Disallowed file extension!"
                    return render_template("/homepage.html", error_message = error_message , converted = False)

                image = Image.open("static/upload/" + filename)


                path, buffer = converter(image, convert_to)
                
                session["uploaded"] = True
                return render_template("/homepage.html", path = path.decode('ascii'), url = filename, converted = True)
    else:
        #If someone comes to page with GET method, we will redirect to index page
        return redirect(url_for('index'))

@app.route('/' , methods=['POST', 'GET'])
def index():
    return render_template("/homepage.html")

#region app.run
if __name__ == "__main__":
   app.run(debug=True)
#endregion app.run