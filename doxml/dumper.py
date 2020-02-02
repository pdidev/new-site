#!/bin/env python3

import os
import os.path
import re
import shutil
import yaml
from parser import Doxml
import cppmodel as cxx
import mdgen as md

def page_name(name):
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    if name == 'index':
        name='_index'
    return name.lower()+'.md'

def dump_class(outdir, path, cls):
    print("dumping "+cls.name)
    print("dumping "+cls.defined.kind+" "+cls.name)
    dir = os.path.join(outdir, *[re.sub(r'[^a-zA-Z0-9]', '_', n) for n in path])
    os.makedirs(dir, exist_ok=True)
    data = {
        'linkTitle': cls.name,
        'title': "the "+"::".join(path)+" "+cls.defined.kind,
    }
    with open(os.path.join(dir, '_index.md'), mode='w') as outfile:
        print("---", file=outfile)
        yaml.dump(data, outfile)
        print("---", file=outfile)
        print("{{% class \""+".".join(path)+"\" %}}", file=outfile)
    try:
        for sub_cls in cls.defined.types.values():
            dump_class(outdir, path+[sub_cls.name], sub_cls)
    except:
        pass

def dump_ns(outdir, path, ns):
    dir = os.path.join(outdir, *path)
    os.makedirs(dir, exist_ok=True)
    data = {
        'linkTitle': ns.name,
        'title': "the "+"::".join(path)+" namespace",
    }
    with open(os.path.join(dir, '_index.md'), mode='w') as outfile:
        print("---", file=outfile)
        yaml.dump(data, outfile)
        print("---", file=outfile)
        print("{{% namespace \""+".".join(path)+"\" %}}", file=outfile)
    for sub_ns in ns.defined.namespaces.values():
        dump_ns(outdir, path+[sub_ns.name], sub_ns)
    for sub_cls in ns.defined.types.values():
        dump_class(outdir, path+[sub_cls.name], sub_cls)

def dump_root_ns(outdir, ns):
    os.makedirs(outdir, exist_ok=True)
    data = {
        'title': "Reference",
    }
    with open(os.path.join(outdir, '_index.md'), mode='w') as outfile:
        print("---", file=outfile)
        yaml.dump(data, outfile)
        print("---", file=outfile)
        print("{{% namespace %}}", file=outfile)
    for sub_ns in ns.namespaces.values():
        dump_ns(outdir, [sub_ns.name], sub_ns)
    for sub_cls in ns.types.values():
        dump_class(outdir, [sub_cls.name], sub_cls)
    

def dump_page(name, page, outdir):
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

    with open(os.path.join(outdir, page_name(name)), mode='w') as outfile:
        print("---", file=outfile)
        yaml.dump(data, outfile)
        print("---", file=outfile)
        print(page['detaileddescription'].render(''), file=outfile)


def dump(doxfile, outdir):
    pagedstdir = os.path.join(outdir, "content/docs/")
    os.makedirs(pagedstdir, exist_ok=True)
    doxdata = Doxml(doxfile, '/docs/imgs/')
    for name, page in doxdata.pages.items():
        dump_page(name, page, pagedstdir)
    imgsrcdir = os.path.dirname(doxfile)
    imgdstdir = os.path.join(outdir, 'static/docs/imgs/')
    os.makedirs(imgdstdir, exist_ok=True)
    for img in doxdata.images:
        shutil.copy(os.path.join(imgsrcdir, img), os.path.join(imgdstdir, img))
    yaml.add_representer(md.BlockContainer, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data.render('').strip()+'\n', style=r'|'))
    dstdat = os.path.join(outdir, "data/docs/dox.yml")
    datadstdir = os.path.join(outdir, "data/docs/")
    os.makedirs(datadstdir, exist_ok=True)
    with open(os.path.join(datadstdir, 'doxdata.yml'), mode='w') as outf:
        yaml.dump(doxdata.root_namespace, outf)
    nsdstdir = os.path.join(outdir, "content/docs/ref/")
    os.makedirs(nsdstdir, exist_ok=True)
    dump_root_ns(nsdstdir, doxdata.root_namespace)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        dump("../dox/combined.xml", "..")
    else:
        dump(sys.argv[1], sys.argv[2])
