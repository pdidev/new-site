#!/bin/env python3

import os.path
import shutil
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
import yaml
from markdown import *

def non_empty(node):
    return node is not None and node.strip() != ''

def empty_node(node):
    if node is None:
        return True
    if non_empty(node.text):
        return False
    if len(node.keys()) > 0:
        return False
    for subnode in node:
        if subnode.tail is not None and subnode.tail.strip() != '':
            return False
        if not empty_node(subnode):
            return False
    return True

class MyEmitter(yaml.emitter.Emitter):
    def analyze_scalar(self, scalar):
        result = super().analyze_scalar(scalar)
        result.allow_block = True
        return result
        #if len(scalar) > 0 and scalar[-1] not in '\n 

yaml.add_representer(BlockContainer, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data.render('').strip()+'\n', style=r'|'))

class DoxmlParser:

    def __init__(self, file):
        self._file = file
        self._tree = ET.parse(file)
        self._parsed = dict()
        for compounddef in self._tree.getroot():
            if compounddef.get('kind') != 'page':
                continue
            parsed_compounddef = self.compounddef(compounddef)
            compoundname = parsed_compounddef['compoundname']
            del parsed_compounddef['compoundname']
            self._parsed[compoundname] = parsed_compounddef
        self._tree = None

    def parsed(self):
        return self._parsed

    def dump(self, **kwargs):
        return yaml.dump(**kwargs)

    @staticmethod
    def add_if_not_empty(dict_, node, path=None, tr=None, attr=None, key=None):
        if tr is None:
            if attr is None:
                tr = lambda x: x.text
            else:
                tr = lambda x: x
        if key is None:
            key = path
        if node is not None and path is not None:
            node = node.find(path)
        if empty_node(node):
            return
        if attr is not None:
            node = node.get(attr)
        node = tr(node)
        dict_[key] = node
    
    def compounddef(self, node):
        result = dict()
        DoxmlParser.add_if_not_empty(result, node, 'compoundname')
        DoxmlParser.add_if_not_empty(result, node, 'title')
        DoxmlParser.add_if_not_empty(result, node, 'briefdescription', tr=self.description)
        DoxmlParser.add_if_not_empty(result, node, 'detaileddescription', tr=self.description)
        return result

    def description(self, node):
        result = BlockContainer()
        if not empty_node(node.find('title')):
            result.append(Heading(1, [Text(node.findtext('title'))]))
        for para in node.findall('para'):
            result.append(self.para(para))
        for sect1 in node.findall('sect1'):
            result.extend(self.sect1(sect1))
        return result
    
    def sect1(self, node):
        result = []
        if not empty_node(node.find('title')):
            result.append(Heading(2, [Text(node.findtext('title'))]))
        for para in node.findall('para'):
            result.append(self.para(para))
        for sect2 in node.findall('sect2'):
            result.extend(self.sect2(sect2))
        return result
    
    def sect2(self, node):
        result = []
        if not empty_node(node.find('title')):
            result.append(Heading(3, [Text(node.findtext('title'))]))
        for para in node.findall('para'):
            result.append(self.para(para))
        for sect3 in node.findall('sect3'):
            result.extend(self.sect3(sect3))
        return result
    
    def sect3(self, node):
        result = []
        if not empty_node(node.find('title')):
            result.append(Heading(4, [Text(node.findtext('title'))]))
        for para in node.findall('para'):
            result.append(self.para(para))
        for sect4 in node.findall('sect4'):
            result.extend(self.sect4(sect4))
        return result
    
    def sect4(self, node):
        result = []
        if not empty_node(node.find('title')):
            result.append(Heading(5, [Text(node.findtext('title'))]))
        for para in node.findall('para'):
            result.append(self.para(para))
        return result
    
    def para(self, node):
        result = Paragraph ()
        if non_empty(node.text):
            result.append(Text(node.text))
        for content in node:
            result.extend(self.doc_cmd_group(content))
            if non_empty(content.tail):
                result.append(Text(content.tail))
        return result
    
    def doc_title_cmd_group(self, node):
        if node.tag == 'ref':
            return [] # TODO self.doc_ref_text(node)
        if node.tag == 'emphasis':
            return [] # TODO
        if node.tag == 'bold':
            return [] # TODO
        if node.tag == 'ulink':
            return [] # TODO
        if node.tag == 'computeroutput':
            return [] # TODO
        raise KeyError('No such doc_title_cmd: '+node.tag)
    
    def doc_cmd_group(self, node):
        if node.tag == 'hruler':
            return [] # TODO
        if node.tag == 'itemizedlist':
            return [] # TODO
        if node.tag == 'orderedlist':
            return [] # TODO
        if node.tag == 'variablelist':
            return [] # TODO
        if node.tag == 'table':
            return [] # TODO
        if node.tag == 'simplesect':
            return [] # TODO
        if node.tag == 'image':
            return [] # TODO
        if node.tag == 'programlisting':
            return [] # TODO
        try:
            return self.doc_title_cmd_group(node)
        except KeyError:
            raise KeyError('No such doc_cmd: '+node.tag)
    
    def doc_ref_text(self, node):
        result = Link(node.get('refid') )
        if non_empty(node.text):
            result.append(Text(node.text))
        for content in node:
            result.extend(self.doc_cmd_group(content))
            if non_empty(content.tail):
                result.append(Text(content.tail))
        return [ result ]        

if __name__ == '__main__':
    p = DoxmlParser(sys.argv[1])
    yaml.dump(p.parsed(), sys.stdout)



