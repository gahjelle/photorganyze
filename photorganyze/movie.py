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
    vid_vars = get_video_vars(path)
    if vid_vars is None:
        return

    vid_hash = get_file_hash(path)
    vid_exists = check_video_exists(vid_hash, vid_vars)
    if vid_exists:
        return

    output_path = get_output_path(vid_vars)
    print('->', output_path)

    create_directories(output_path)
    save_video_file(path, output_path)
    save_video_hash(vid_hash, vid_vars, output_path)


def get_video_vars(path):
    video_format_map = {}
    vid_vars = dict(user=util.get_option('--user') or config.get('user', 'output'))

    try:
        date = get_date_from_filename(path)
    except ValueError:
        try:
            date = datetime.fromtimestamp(os.path.getctime(path))
        except StopIteration:
            date = datetime.now().replace(year=1900, month=1, day=1)
    vid_vars.update(get_date_vars(date))
    vid_vars.update(get_date_vars(date + timedelta(hours=-5), '_'))

    vid_vars['model'] = 'video'

    vid_vars['base'] = get_original_video_name(path, date)
    path_ext = path.rpartition('.')[-1]
    vid_vars['ext'] = video_format_map.get(path_ext.lower(), path_ext.lower())

    return vid_vars


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


def check_video_exists(vid_hash, vid_vars):
    check_path = os.path.join(config.get_path('directory', 'output'), config.get('checksum_file', 'output'))
    try:
        with open(check_path.format(**vid_vars), mode='r') as fid:
            vid_hashes = json.load(fid)
    except FileNotFoundError:
        return False

    if vid_hash in vid_hashes:
        print('-> Exists as {}'.format(vid_hashes[vid_hash]))
        return True

    return False


def get_output_path(vid_vars):
    ids = [''] + list('abcdefghijklmnopqrstuvwxyz')
    output_path = os.path.join(config.get_path('directory', 'output'), config.get('file_name', 'output'))

    while True:
        vid_vars['id'] = ids.pop(0)
        path = output_path.format(**vid_vars)
        if not os.path.exists(path):
            break

    return path


def create_directories(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)


def save_video_file(input_path, output_path):
    shutil.copy2(input_path, output_path)


def save_video_hash(vid_hash, vid_vars, output_path):
    check_path = os.path.join(config.get_path('directory', 'output'), config.get('checksum_file', 'output'))
    try:
        with open(check_path.format(**vid_vars), mode='r') as fid:
            vid_hashes = json.load(fid)
    except FileNotFoundError:
        vid_hashes = dict()

    vid_hashes[vid_hash] = output_path
    with open(check_path.format(**vid_vars), mode='w') as fid:
        json.dump(vid_hashes, fid)


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


def get_original_video_name(path, date):
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
