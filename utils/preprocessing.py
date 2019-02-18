# coding: utf-8
from __future__ import print_function
import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, SRC_DIR)

from config import Config

# [(input_file, output_file), ...]
TEMPLATE_FILES = [
    ('../app.service.template', '../%s' % Config.APP_SRV_FILE),
]

def preprocess_dirs():
    for infile, outfile in TEMPLATE_FILES:
        print('preprocessing ...', os.path.abspath(outfile))
        temp_str = ''

        with open(infile) as f:
            temp_str = f.read()

        with open(outfile, 'w') as f:
            f.write(temp_str % Config.to_dict())

    print('Preprocessing OK.')


def main():
    os.chdir(os.path.dirname(__file__))
    preprocess_dirs()

if __name__ == '__main__':
    main()
