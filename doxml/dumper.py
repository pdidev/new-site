#!/bin/env python3

import os
import os.path
import re
import shutil
import yaml
from parser import Doxml

def page_name(name):
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    if name == 'index':
        name='_index'
    return name.lower()+'.md'
    

def dump(doxfile, outdir):
    pagedstdir = os.path.join(outdir, "content/docs/")
    os.makedirs(pagedstdir, exist_ok=True)
    doxdata = Doxml(doxfile, '/docs/imgs/')
    for name, page in doxdata.pages.items():
        data = dict()
        try:
            data['title'] = page['title']
        except KeyError:
            data['title'] = name
        try:
            data['description'] = page['briefdescription']
        except KeyError:
            pass
        if name == 'index':
            data['linkTitle'] = "Documentation"
            data['weight'] = 20
            data['menu'] = { 'main': { 'weight': 20 } }

        with open(os.path.join(pagedstdir, page_name(name)), mode='w') as outfile:
            print("---", file=outfile)
            yaml.dump(data, outfile)
            print("---", file=outfile)
            print(page['detaileddescription'].render(''), file=outfile)
    
    imgsrcdir = os.path.dirname(doxfile)
    imgdstdir = os.path.join(outdir, 'static/docs/imgs/')
    os.makedirs(imgdstdir, exist_ok=True)
    for img in doxdata.images:
        shutil.copy(os.path.join(imgsrcdir, img), os.path.join(imgdstdir, img))

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        dump("../data/combined.xml", "..")
    else:
        dump(sys.argv[1], sys.argv[2])
