from io import BytesIO
from django.core.files import File


def upload_file(file):
    buffer = BytesIO()
    for chunk in file.chunks():
        buffer.write(chunk)
    return File(buffer)
