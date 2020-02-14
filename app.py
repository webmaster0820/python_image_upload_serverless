from chalice import Chalice
from chalice import Chalice, Response
from datetime import datetime
import urllib.request
import logging
from chalicelib.config import *
from chalicelib.module import *


app = Chalice(app_name='anton-test')
app.debug = True
app.log.setLevel(logging.DEBUG)

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

app.api.binary_types.append("multipart/form-data")


@app.route('/', cors=True)
def index():
    with open('./chalicelib/template.html', 'r') as f:
        template = f.read()
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})


@app.route('/upload/{file_name}', methods=['POST'], cors=True, content_types=['multipart/form-data'])
def upload_file(file_name):
    # Form data pare to file
    parsed_file_data = ''
    parsed_file_data = parse_form_data(
        app.current_request._body, app.current_request.to_dict()['headers']['content-type'])
    try:
        pass
    except:
        return Response(body={'error': 'Form Data parse error!'}, status_code=200)

    # # Check file type
    try:
        kind, parsed_file_data = get_mime_and_resize(parsed_file_data)
    except:
        return Response(body={'error': 'unknown file!'}, status_code=200)

    if kind.mime not in ['image/png', 'image/jpeg', 'image/bmp']:
        return Response(body={'Error': 'This is invalid image'}, status_code=200)

    # Upload file to S3
    file_key = f'uploaded_image/400x255/{file_name}'
    s3_client.put_object(Bucket=BUCKET, Key=file_key,
                         Body=parsed_file_data, ContentType=kind.mime)
    try:
        pass
    except:
        return Response(body={'error': 'Save file to S3 error!'}, status_code=500)

    # Get presigned url
    try:
        s3object_url = create_presigned_url(BUCKET, file_key, 1200)
        html = """
				<html>
                    <body style="background: black">
                    <div style="width:100%; text-align: center; margin-top: 100px"><img style="margin:auto" src="{}" alt="400 x 255 image">
				    </body>
                </html>
				""".format(s3object_url)
        return Response(body=html,
                        status_code=200,
                        headers={'Content-Type': 'text/html'})
    except:
        return Response(body={'error': 'Failed to get pre-signed url'}, status_code=500)
