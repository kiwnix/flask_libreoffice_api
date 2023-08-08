# LibreOffice REST API

Basado en https://github.com/jesseinit/flask_libreoffice_api

# Getting Started

1. Ensure you have docker running and enough resources(atleast 2GB RAM) allocated to it.
2. Build image with `docker build -t libreoffice_rest .`
3. Start container with `docker run --name libreoffice_rest --rm -p 3000:3000 libreoffice_rest`

# Accessing Endpoints

There are three endpoint exposed on the project and they are as follows

- GET `/health` - Returns a message on how so uppp we are..lol
- GET `/` - Returns a greeting message..hehe
- POST `/utils/libreoffice/convert-xlsx-to-pdf` - Takes a multipart form request and returns the converted file directly converted to pdf by libreoffice (only xlsx)
- POST `/utils/libreoffice/convert-to-embhtml` - Takes a multipart form request and returns the converted file converted by libreoffice and embedding the images (base64 datalinks), using BeautifulSoup
- POST `/utils/libreoffice/convert-to-embpdf` - Takes a multipart form request and returns the converted file converted to html, embedding the images and converting to pdf using pdfkit/wkhtmltopdf. it accepts a parameter pagesize= to specify a pagesize (A4,A0,Letter, etc (passed as option to wkhtmltopdf))


  Example Requests

  ```curl
  curl --location --request POST 'http://127.0.0.1:3000/utils/libreoffice/convert-to-embpdf?pagesize=A4' --form 'files=@1.xlsx' -o 1.pdf

  curl --location --request POST 'http://127.0.0.1:3000/utils/libreoffice/convert-to-embhtml' --form 'files=@1.xlsx' -o 1.html
  ```

## Todo

Feel free to open an issue or a PR for any of the todos below or other improvements.

- [x] Implement non-root user in the docker image
- [ ] Support other document type conversion
- [ ] Reduce docker image size
- [ ] Optimise how the subprocess is called
- [ ] Add logging and increased granularity
- [ ] Miscellaneous Gunicorn configuration fine-tunning
