from datetime import datetime, timedelta
import json
import os
import shutil

from PIL import ExifTags, Image
import imagehash

from photorganyze.lib import config


def store(path):
    print('|-', os.path.basename(path), end=' ')

    img, img_vars = get_image_vars(path)
    if img_vars is None:
        return

    img_hash = get_image_hash(img)
    img_exists = check_image_exists(img_hash, img_vars)
    if img_exists:
        return

    output_path = get_output_path(img_vars)
    print('->', output_path)

    create_directories(output_path)
    save_image_file(path, output_path)
    save_image_hash(img_hash, img_vars, output_path)


def get_image_vars(path):
    img_vars = dict(user=config.get('user', 'output'), ext=os.path.splitext(path)[-1].lower())
    try:
        img = Image.open(path, mode='r')
    except OSError:
        print('-> Not an image. Ignored')
        return None, None

    try:
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    except AttributeError:
        print('-> No EXIF-data. Ignored')
        return img, None

    try:
        date = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    except KeyError:
        try:
            date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
        except KeyError:
            date = datetime.now().replace(year=1900, month=1, day=1)
    img_vars.update(get_date_vars(date))
    img_vars.update(get_date_vars(date + timedelta(hours=-6), '_'))

    img_vars['make'] = convert_to_filename(exif.get('Make', 'Unknown').split()[0])
    img_vars['model'] = convert_to_filename(exif.get('Model', 'Unknown model'))
    if not img_vars['model'].startswith(img_vars['make'] + '_'):
        img_vars['model'] = img_vars['make'] + '_' + img_vars['model']

    return img, img_vars


def get_image_hash(img):
    return str(imagehash.average_hash(img)) + str(imagehash.dhash(img)) + str(imagehash.dhash_vertical(img))


def check_image_exists(img_hash, img_vars):
    check_path = os.path.join(config.get_path('directory', 'output'), config.get('checksum_file', 'output'))
    try:
        with open(check_path.format(**img_vars), mode='r') as fid:
            img_hashes = json.load(fid)
    except FileNotFoundError:
        return False

    if img_hash in img_hashes:
        print('-> Already exists as {}'.format(img_hashes[img_hash]))
        return True

    return False


def get_output_path(img_vars):
    ids = list('abcdefghijklmnopqrstuvwxyz')
    output_path = os.path.join(config.get_path('directory', 'output'), config.get('file_name', 'output'))

    while True:
        img_vars['id'] = ids.pop(0)
        path = output_path.format(**img_vars)
        if not os.path.exists(path):
            break

    return path


def create_directories(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)


def save_image_file(input_path, output_path):
    shutil.copy2(input_path, output_path)


def save_image_hash(img_hash, img_vars, output_path):
    check_path = os.path.join(config.get_path('directory', 'output'), config.get('checksum_file', 'output'))
    try:
        with open(check_path.format(**img_vars), mode='r') as fid:
            img_hashes = json.load(fid)
    except FileNotFoundError:
        img_hashes = dict()

    img_hashes[img_hash] = output_path
    with open(check_path.format(**img_vars), mode='w') as fid:
        json.dump(img_hashes, fid)


def get_date_vars(date, suffix=''):
    date_vars = dict(yyyy=date.strftime('%Y'),
                     ce=date.strftime('%Y')[:2],
                     yy=date.strftime('%y'),
                     m=str(date.month),
                     mm=date.strftime('%m'),
                     mmm=date.strftime('%b').lower(),
                     MMM=date.strftime('%b').upper(),
                     d=str(date.day),
                     dd=date.strftime('%d'),
                     doy=date.strftime('%j'),
                     dow=date.strftime('%w'),
                     HH=date.strftime('%H'),
                     MM=date.strftime('%M'),
                     SS=date.strftime('%S'),
                    )

    return {k + suffix: v for k, v in date_vars.items()}


def convert_to_filename(s):
    return s.lower().strip().replace(' ', '_').replace('\x00', '')
