from datetime import datetime, timedelta
import hashlib
import json
import os
import re
import shutil

from PIL import ExifTags, Image

from photorganyze.lib import config
from photorganyze.lib import util


def store(path):
    print('|-', os.path.basename(path), end=' ')

    img_vars = get_image_vars(path)
    if img_vars is None:
        return

    img_hash = get_file_hash(path)
    img_exists = check_image_exists(img_hash, img_vars)
    if img_exists:
        return

    output_path = get_output_path(img_vars)
    print('->', output_path)

    create_directories(output_path)
    save_image_file(path, output_path)
    save_image_hash(img_hash, img_vars, output_path)


def get_image_vars(path):
    image_format_map = {'jpeg': 'jpg'}
    img_vars = dict(user=util.get_option('--user') or config.get('user', 'output'))

    try:
        img = Image.open(path, mode='r')
    except OSError:
        print('-> Not an image. Ignored')
        return None

    try:
        exif = get_exif(img)
    except AttributeError:
        print('-> No EXIF-data.', end=' ')
        exif = dict()

    try:
        date = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    except (KeyError, ValueError):
        try:
            date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
        except (KeyError, ValueError):
            try:
                date = get_date_from_filename(path)
            except ValueError:
                date = datetime.now().replace(year=1900, month=1, day=1)
    img_vars.update(get_date_vars(date))
    img_vars.update(get_date_vars(date + timedelta(hours=-5), '_'))

    img_vars['make'] = convert_to_filename(exif.get('Make', 'Unknown').split()[0])
    img_vars['model'] = convert_to_filename(exif.get('Model', 'Unknown model'))
    if not img_vars['model'].startswith(img_vars['make'] + '_'):
        img_vars['model'] = img_vars['make'] + '_' + img_vars['model']

    img_vars['base'] = get_original_image_name(path, date)
    img_vars['ext'] = image_format_map.get(img.format.lower(), img.format.lower())

    return img_vars


def get_file_hash(path):
    """

    http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    """
    return hash_bytestr_iter(file_as_blockiter(open(path, mode='rb')), hashlib.sha256(), True)


def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()


def file_as_blockiter(fid, blocksize=65536):
    with fid:
        block = fid.read(blocksize)
        while len(block) > 0:
            yield block
            block = fid.read(blocksize)


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
    ids = [''] + list('abcdefghijklmnopqrstuvwxyz')
    output_path = os.path.join(config.get_path('directory', 'output'), config.get('file_name', 'output'))

    while True:
        img_vars['id'] = ids.pop(0)
        path = output_path.format(**img_vars)
        if not os.path.exists(path):
            break

    return path


def get_exif(img):
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    if 'GPSInfo' in exif:
        exif.update({ExifTags.GPSTAGS[k]: v for k, v in exif['GPSInfo'].items() if k in ExifTags.GPSTAGS})

    return exif


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


def get_original_image_name(path, date):
    base_re = re.search(r'(dsc|img|sam)_?\d{4}.jpe?g', path, flags=re.IGNORECASE)

    if base_re is None:
        return date.strftime('%H%M%S')
    else:
        return os.path.splitext(base_re.group())[0]

def get_date_from_filename(path):
    filename = os.path.splitext(os.path.basename(path))[0]

    try:
        return datetime.strptime(filename[-19:], '%Y-%m-%d %H.%M.%S')
    except ValueError:
        return datetime.strptime(filename[-17:], '%d-%m-%y %H %M %S')
