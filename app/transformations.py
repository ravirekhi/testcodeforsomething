from __future__ import print_function
from wand.image import Image
from app.utils import upload_to_s3

def transform_and_upload(file,imgObj):
    with Image(blob=file) as img:
        upload_to_s3(imgObj['key1'], img.make_blob())
        with img.clone() as flipped:
            flipped.flip()
            upload_to_s3(imgObj['key2'],flipped.make_blob())
        with img.clone() as blurred:
            blurred.gaussian_blur(5,3)
            upload_to_s3(imgObj['key3'],blurred.make_blob())
        with img.clone() as resized:
            resized.transform(resize='50%')
            upload_to_s3(imgObj['key4'],resized.make_blob())


