from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from modules.pdf_processing.processor import extract_images_from_pdf, images_to_pdf, categorize_images
import os
import configparser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'modules/pdf_processing/input/'
app.config['OUTPUT_FOLDER'] = 'modules/pdf_processing/output/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

config = configparser.ConfigParser()
config.read('modules/pdf_processing/config.cfg')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
        #filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
def home():
    print("Home")
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("Upload")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            config.set('Files', 'INPUT', filepath)
            with open('modules/pdf_processing/config.cfg', 'w') as configfile:
                config.write(configfile)

            pdf_path = config['Files']['INPUT']
            output_path = config['Files']['OUTPUT']
            # images_folder_path = config['Files']['IMAGES']
            print(f'pdf_path: {pdf_path} output_path: {output_path} ')
            images = extract_images_from_pdf(pdf_path)
            print(f"Extracted {len(images)} images from {pdf_path}")
            
            categorized_images = categorize_images(images, config)

            for category, imgs in categorized_images.items():
                output_pdf_path = f"{output_path}/{filename}_{category}.pdf"
                images_to_pdf(imgs, output_pdf_path)
                print(f"Generated PDF for {category} at {output_pdf_path}")
    return render_template('index.html')


@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)