import cgi
from io import BytesIO
import boto3
import time
import os
import urllib.request
from chalicelib.config import *
import filetype
from PIL import Image
from resizeimage import resizeimage
import base64

def resize_image(image_path, width=400, height=255):
    with open(image_path, 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [width, height])
            print(cover)
            result_path = f'{image_path}.tmp'
            cover.save(result_path, image.format)
            with open(result_path, 'r+b') as f:
                res = f.read()
                return res

def parse_form_data(request_body, content_type_obj):
    if isinstance(request_body, str):
        request_body = base64.b64decode(request_body)
    content_type, property_dict = cgi.parse_header(content_type_obj)
    property_dict['boundary'] = property_dict['boundary'].encode('utf-8')
    property_dict['CONTENT-LENGTH'] = 123450000
    form_data = cgi.parse_multipart(BytesIO(request_body), property_dict)
    return form_data['file'][0]


def save_file_to_temp(file_data, file_name):
    full_path = '/tmp/{}'.format(file_name)
    with open(full_path, 'wb+') as f:
        f.write(file_data)
    return full_path


def create_presigned_url(bucket_name, object_name, expiration=3600):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration)
    return response

def get_mime_and_resize(blob_data):
    # # Save file to tmp folder
    tmp_file_path = save_file_to_temp(blob_data, 'temp.dmp')
    # # Get file type
    kind = filetype.guess(tmp_file_path)
    # # Resize image
    resized_image = resize_image(tmp_file_path)
    return [kind, resized_image]
