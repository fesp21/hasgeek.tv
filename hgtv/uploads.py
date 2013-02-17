#! /usr/bin/env python

import Image
import os
from werkzeug import FileStorage
from StringIO import StringIO
from flask import current_app
from flask.ext.uploads import (UploadSet, configure_uploads,
     IMAGES, UploadNotAllowed)


thumbnails = UploadSet('thumbnails', IMAGES,
    default_dest=lambda app: os.path.join(app.static_folder, 'thumbnails'))


def configure(app):
    thumbnails_dir = os.path.join(app.static_folder, 'thumbnails')
    if not os.path.isdir(thumbnails_dir):
        os.mkdir(thumbnails_dir)
    configure_uploads(app, thumbnails)


def return_werkzeug_filestorage(request, filename):
    extension = request.headers['content-type'].split('/')[-1]
    if extension not in current_app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    new_filename = filename + '.' + extension
    try:
        tempfile = StringIO(buf=request.content)
    except AttributeError:
        tempfile = StringIO(buf=request.stream)
    tempfile.name = new_filename
    filestorage = FileStorage(tempfile,
        filename=new_filename,
        content_type=request.headers['content-type'])
    return filestorage


def resize_image(requestfile, maxsize=(180, 106)):
    fileext = requestfile.filename.split('.')[-1].lower()
    if fileext not in current_app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    img = Image.open(requestfile)
    img.load()
    if img.size[0] > maxsize[0] or img.size[1] > maxsize[1]:
        img.thumbnail(maxsize, Image.ANTIALIAS)
    boximg = Image.new('RGBA', (img.size[0], img.size[1]), (255, 255, 255, 0))
    boximg.paste(img, (0, 0))
    savefile = StringIO()
    savefile.name = requestfile.filename
    boximg.save(savefile)
    savefile.seek(0)
    return FileStorage(savefile,
        filename=requestfile.filename,
        content_type=requestfile.content_type)
