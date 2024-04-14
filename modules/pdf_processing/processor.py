import PyPDF2
import io
from PIL import Image
import easyocr
import numpy as np
import configparser
import os

def extract_images_from_pdf(pdf_path):
    images = []
    pdf_document = PyPDF2.PdfFileReader(pdf_path)
    for current_page_number in range(pdf_document.getNumPages()):
        current_page = pdf_document.getPage(current_page_number)
        if "/XObject" in current_page["/Resources"]:
            x_object = current_page["/Resources"]["/XObject"].getObject()
            for obj in x_object:
                if x_object[obj]["/Subtype"] == "/Image":
                    image = x_object[obj]
                    image_bytes = image._data
                    images.append(Image.open(io.BytesIO(image_bytes)))
    return images

def images_to_pdf(images, output_pdf):
    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])

def categorize_images(images, config):
    reader = easyocr.Reader(["en"])
    ocr_location = config['OCR']['Loc1'].split(',')
    x1, y1, x2, y2 = map(int, ocr_location)

    categorized_images = {
        "Complaint": [],
        "Summons": [],
        "Appearance": []
    }
    current_category = None

    for image in images:
        cropped_image = image.crop((x1, y1, x2, y2))
        results = reader.readtext(np.array(cropped_image))
        for result in results:
            text = result[1].upper()
            print(f"Detected OCR Text: {text}")  # Debugging aid
            if "COMPLAINT" in text:
                current_category = "Complaint"
                break
            elif "SUMMONS" in text:
                current_category = "Summons"
                break
            elif "APPEARANCE" in text:
                current_category = "Appearance"
                break

        if current_category:
            categorized_images[current_category].append(image)

    return categorized_images

# if __name__ == "__main__":
#     config = configparser.ConfigParser()
#     config.read('config.cfg')  # Assume the configuration file path is correct

#     pdf_path = config['Files']['INPUT']
#     output_path = config['Files']['OUTPUT']

#     images = extract_images_from_pdf(pdf_path)
#     print(f"Extracted {len(images)} images from {pdf_path}")

#     categorized_images = categorize_images(images, config)

#     base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

#     for category, imgs in categorized_images.items():
#         output_pdf_path = f"{output_path}/{base_filename}_{category}.pdf"
#         images_to_pdf(imgs, output_pdf_path)
#         print(f"Generated PDF for {category} at {output_pdf_path}")




