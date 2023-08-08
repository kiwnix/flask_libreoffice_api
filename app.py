import subprocess
import os
from pathlib import Path, PurePath
from uuid import uuid4
from shutil import rmtree

from flask import Flask, request, send_from_directory, g

import pdfkit

from embedhtml import make_html_images_inline



UPLOAD_DIRECTORY = str(PurePath(Path.home(),'uploads'))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 30)) #In Megabyte

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1000 * 1000


@app.route("/health", methods=['GET'])
def health():
    return {"message": "up like a murtherrrr "}, 200

@app.route("/", methods=['GET'])
def index():
    return {"message": "hello"}, 200

@app.route("/utils/libreoffice/convert-xlsx-to-pdf", methods=['POST'])
def conversion_view_xlsx_pdf_oo():
    #TODO: Manejo de errores
    file = request.files.get('files')
    if not file:
        return {"error": "ensure file is passing in the request"}, 422
    
    ext = file.filename.split('.')[-1]
    filename = uuid4().hex+'.'+ext
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    source_file = f'{UPLOAD_DIRECTORY}/{filename}'
    
    subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf:calc_pdf_Export:{"SinglePageSheets":{"type":"boolean","value":"true"}}', source_file, "--outdir", UPLOAD_DIRECTORY])
    
    Path(source_file).unlink(missing_ok=True)
    
    new_name = f"{filename.split('.')[0]}.pdf"
    
    g.dest_file = f'{UPLOAD_DIRECTORY}/{new_name}'
    
    return send_from_directory(app.config["UPLOAD_FOLDER"], new_name, as_attachment=True)


def convert_to_html(file, filename, TMP_UPLOAD_FOLDER):
    file.save(os.path.join(TMP_UPLOAD_FOLDER, filename))
    source_file = f'{TMP_UPLOAD_FOLDER}/{filename}'
    
    subprocess.call(['libreoffice', '--headless', '--convert-to', 'html', source_file, "--outdir", TMP_UPLOAD_FOLDER])
    Path(source_file).unlink(missing_ok=True)
    new_name = f"{filename.split('.')[0]}.html"
    embeded_new_name = new_name+"__emb.html"
    make_html_images_inline(str(PurePath(TMP_UPLOAD_FOLDER,new_name)),str(PurePath(TMP_UPLOAD_FOLDER,embeded_new_name)))
    Path(new_name).unlink(missing_ok=True)
    new_name=embeded_new_name

    return new_name

def convert_to_pdf(filename, TMP_UPLOAD_FOLDER, page_size='A3'):
    source_file = f'{TMP_UPLOAD_FOLDER}/{filename}'
    new_name = f"{filename.split('.')[0]}.pdf"
    dest_file = f'{TMP_UPLOAD_FOLDER}/{new_name}'

    pdfkit.from_file(source_file, dest_file , verbose=True, options={"enable-local-file-access": True, "disable-external-links" : True, "disable-internal-links" : True, "page-size": page_size})

    return new_name

@app.route("/utils/libreoffice/convert-to-embhtml", methods=['POST'])
def conversion_view_xlsx_html():
    file = request.files.get('files')
    if not file:
        return {"error": "ensure file is passing in the request"}, 422
    
    ext = file.filename.split('.')[-1]
    filename = uuid4().hex+'.'+ext
    TMP_UPLOAD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'], uuid4().hex)
    os.mkdir(TMP_UPLOAD_FOLDER)

    new_name = convert_to_html(file,filename,TMP_UPLOAD_FOLDER)

    g.dest_file = f'{TMP_UPLOAD_FOLDER}/{new_name}'
    g.dest_tmpdir = TMP_UPLOAD_FOLDER
    
    return send_from_directory(TMP_UPLOAD_FOLDER, new_name, as_attachment=True)

@app.route("/utils/libreoffice/convert-to-embpdf", methods=['POST'])
def conversion_view_xlsx_pdf():
    file = request.files.get('files')
    if not file:
        return {"error": "ensure file is passing in the request"}, 422
    
    pagesize = request.args.get('pagesize')
    if not pagesize:
        pagesize = 'A4'

    ext = file.filename.split('.')[-1]
    filename = uuid4().hex+'.'+ext
    TMP_UPLOAD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'], uuid4().hex)
    os.mkdir(TMP_UPLOAD_FOLDER)

    html_name = convert_to_html(file,filename,TMP_UPLOAD_FOLDER)
    new_name = convert_to_pdf(html_name,TMP_UPLOAD_FOLDER,pagesize)

    g.dest_file = f'{TMP_UPLOAD_FOLDER}/{new_name}'
    g.dest_tmpdir = TMP_UPLOAD_FOLDER
    
    return send_from_directory(TMP_UPLOAD_FOLDER, new_name, as_attachment=True)


@app.after_request
def after_request_func(response):
    if hasattr(g, 'dest_file'):
        Path(g.dest_file).unlink(missing_ok=True)
    if hasattr(g, 'dest_tmpdir'):
        rmtree(g.dest_tmpdir,ignore_errors=True)
    return response

if __name__ == '__main__':
    app.run()
