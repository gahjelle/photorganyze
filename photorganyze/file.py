import os

import magic

from photorganyze import movie
from photorganyze import photo

HANDLERS = dict(
    video=movie.store,
    image=photo.store,
)


def store(path):
    mimetype = magic.from_file(path, mime=True).split('/')[0]
    print('|- {} ({})'.format(os.path.basename(path), mimetype), end=' ')

    if mimetype in HANDLERS:
        return HANDLERS[mimetype](path)
    else:
        print("-> Ignored")
        return None
