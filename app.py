import fitz
from flask import Flask, request, jsonify
from flask_restful import reqparse, Api, abort, Resource
import re
import os
from flask_cors import CORS, cross_origin
from utility import read_hpi,extract_data_nsdl
import preprocess_image
import cv2
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'
custom_oem_psm_config = r'-c preserve_interword_spaces=0 --oem 3 --psm 6 -l eng'
result=''

# Initialize Flask app
app = Flask(__name__)
api = Api(app)

def tessaract(path, page_count):
    global result

    data = pytesseract.image_to_string(Image.open(path), config=custom_oem_psm_config) + '\n'
    result += data + '\n'
    global count
    count += 1
    print(result)
    print('total count : ', count)
    if count == page_count:
        return extract_data()


@app.route('/upload', methods=['POST', 'GET'])
@cross_origin()
def func():
    response_code = '0'
    server_message = 'Error'
    data = {}
    pdf_path = './src/file.pdf'
    page_count = 0
    page_no = 0

    mPdfFile = request.files['pdf_file']
    parser.add_argument('password', type=str)
    parser.add_argument('page_no')
    args = parser.parse_args()
    password = format(args['password'])
    page_no = format(args['page_no'])
    if request.method == 'POST' or request.method == 'GET':
        if mPdfFile is None:
            print('No pdf file received')
            server_message = 'pdf file is required.'
        else:
            try:
                page_num = int(page_no)
                mPdfFile.save(pdf_path)
                page_list = []
                pdf_file = fitz.open(pdf_path, filetype='pdf')
                pdf_file.authenticate(password)
                page_count = pdf_file.pageCount
                print('pages : ', page_count)
                page = pdf_file.loadPage(page_num - 1)
                zoom = 3   # zoom factor
                mat = fitz.Matrix(zoom, zoom)
                pix = page.getPixmap(mat)
                pix.writePNG('page_'+str(page_num)+'.png')
                #page_list.append('page_'+str(x)+'.png')
                #data = tessaract('page_'+str(x)+'.png', page_count)
                data = tessaract('page_'+str(page_no)+'.png', page_no)

            except Exception as e:
                #os.remove(pdf_path)
                print('Exception raised : '+str(e))
                server_message = 'Exception raised : '+str(e)
                return jsonify({'response_code':response_code,
                                'server_message':server_message,
                                u'page_count':page_no})
    else:
        server_message = 'Wrong method'
        #os.remove(pdf_path)
        return jsonify({'response_code':response_code,
                        'server_message':server_message})
    print('data : '+str(data))
    #os.remove(pdf_path)
    server_message = 'Success!'
    global result
    result = ''
    print('must be empty :- ', result)
    return jsonify({u'response_code':'200',
                        u'server_message':server_message,
                        u'data':data,
                        u'total_pages':page_count,
                        u'current_page':page_no})

if __name__ == "__main__":
    text=re.sub(r'\s\s+','\n',result)
    preprocess_text=read_hpi(text.split('\n'))
    data=extract_data_nsdl(preprocess_text)
    app.run()