import PyPDF2
import os
from PIL import Image
import io
import easyocr
import numpy as np
import configparser

final={}

def extract_images_from_pdf(pdf_path, output_path):
    pdf_document = PyPDF2.PdfFileReader(pdf_path)
    for current_page_number in range(pdf_document.getNumPages()):
        current_page = pdf_document.getPage(current_page_number)
        if "/XObject" in current_page["/Resources"]:
            x_object = current_page["/Resources"]["/XObject"].getObject()
            for obj in x_object:
                if x_object[obj]["/Subtype"] == "/Image":
                    image = x_object[obj]
                    image_bytes = image._data
                    image = Image.open(io.BytesIO(image_bytes))
                    image.save(os.path.join(output_path, f"{current_page_number}.png"))

# def images_to_pdf(folder_path, output_pdf):
#     image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
#     images = [Image.open(image) for image in image_paths]
#     images[0].save(output_pdf, save_all=True, append_images=images[1:])

def images_to_pdf(folder_path, output_pdf):
    # List all image files in the folder and sort them by their file names
    image_paths = sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg'))],
        key=lambda x: int(os.path.splitext(os.path.basename(x))[0])  # Sort by converting the file names (sans extension) to integers
    )
    # Open images
    images = [Image.open(image) for image in image_paths]
    # Save all images into one PDF file
    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])

def ocr_on_images(images_folder_path, config):
    reader = easyocr.Reader(["en"])
    
    complaint_output = config['Files']['COMPLAINT_OUTPUT']
    summons_output = config['Files']['SUMMONS_OUTPUT']
    appearance_output = config['Files']['APPEARANCE_OUTPUT']
    
    ocr_location = config['OCR']['Loc1'].split(',')
    x1, y1, x2, y2 = map(int, ocr_location)
    
    for image_name in os.listdir(images_folder_path):
        image_path = os.path.join(images_folder_path, image_name)
        image = Image.open(image_path)

        # Crop the image based on the OCR location provided in the configuration file
        image = image.crop((x1, y1, x2, y2))
        image = np.array(image)
        result = reader.readtext(image)

        if result == []:
            print(image_name[0], "No text found")
        else:
            print(image_name[0], result[0][1])

        final[image_name[0]] = "No text found" if result == [] else result[0][1]

    print(f'Final: {final}')
    # Sort the dictionary according to keys
    key_list = sorted(final.keys())
    sorted_dict = {}
    for key in key_list:
        sorted_dict[key] = final[key]

    flg = 0

    for key in sorted_dict:
        if sorted_dict[key] == "COMPLAINT":
            # Store {key}.png in complaint folder
            image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
            image.save(os.path.join(complaint_output, f"{key}.png"))
            flg = 1

        elif sorted_dict[key] == "SUMMONS":
            # Store {key}.png in summons folder
            image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
            image.save(os.path.join(summons_output, f"{key}.png"))
            flg = 2

        elif sorted_dict[key] == "Appearance By Attorney In Civil Case":
            # Store {key}.png in appearance folder
            image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
            image.save(os.path.join(appearance_output, f"{key}.png"))
            flg = 3

        else:
            if flg == 1:
                image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
                image.save(os.path.join(complaint_output, f"{key}.png"))

            elif flg == 2:
                image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
                image.save(os.path.join(summons_output, f"{key}.png"))

            elif flg == 3:
                image = Image.open(os.path.join(images_folder_path, f"{key}.png"))
                image.save(os.path.join(appearance_output, f"{key}.png"))


if __name__ == "__main__":
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.cfg')  # Replace 'config.cfg' with the path to your configuration file
    
    # Extract input and output paths from the configuration file
    pdf_path = config['Files']['INPUT']
    print(pdf_path)
    images_folder_path = config['Files']['IMAGES']
    output_path = config['Files']['OUTPUT']
    
    # Create the output directory if it doesn't exist
    # if not os.path.exists(output_path):
    #     os.makedirs(output_path)
    
    # Extract images from PDF
    extract_images_from_pdf(pdf_path, images_folder_path)
    print(f"Images extracted from {pdf_path} and saved in {output_path} folder")
    
    # Perform OCR on images
    ocr_on_images(images_folder_path, config)

    # Convert separated images to PDFs for each category
    for folder, output_folder in [("complaint", config['Files']['COMPLAINT_OUTPUT']), 
                                  ("summons", config['Files']['SUMMONS_OUTPUT']), 
                                  ("appearance", config['Files']['APPEARANCE_OUTPUT'])]:
        output_pdf = os.path.join(output_path, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_{folder}.pdf")
        images_to_pdf(output_folder, output_pdf)

