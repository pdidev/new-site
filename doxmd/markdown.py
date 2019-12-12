#!/bin/env python3

import os.path
import re

PNCT_RE = re.compile(r'([-\\!\[\]"#$%&\'\(\)*+,-./:;<=>?@^_`{|}~])')
SPS_RE = re.compile(r'\s+')
NL_RE = re.compile(r'\n')
BRCK_RE = re.compile(r'([<>])')
BLNK_RE = re.compile(r'^\s*$', re.MULTILINE)
BQS_RE = re.compile(r'`+')
DQ_RE = re.compile(r'"')

EXTRACT_SP_RE = re.compile(r'^(\s*)(.*[^\s])(\s*)$')

class BlockContainer:
    def __init__(self, blocks=None):
        if blocks is None:
            self._blocks = []
        else:
            self._blocks = blocks
        
    def append(self, block):
        self._blocks.append(block)
        
    def extend(self, blocks):
        self._blocks.extend(blocks)
    
    def render(self, indent):
        return "\n\n".join([re.sub(r'\s+$', '', b.render(indent)) for b in self._blocks])

class InlineContainer:
    def __init__(self, inlines=None):
        if inlines is None:
            self._inlines = []
        else:
            self._inlines = inlines
    
    def append(self, inline):
        self._inlines.append(inline)
        
    def extend(self, inlines):
        self._inlines.extend(inlines)
    
    def render(self, indent):
        return "".join([i.render(indent) for i in self._inlines])

class ItemContainer:
    def __init__(self, loose=False, items=None):
        if items is None:
            self._items = []
        else:
            self._items = items
        self._loose = loose
        
    def append(self, item):
        self._items.append(item)
    
    def render(self, prefix, indent):
        return indent+("\n\n"+indent if self._loose else "\n"+indent).join([prefix + i.render(' '*max(prefix+1, 4))[len(prefix):] for i in self._items])

class BlockQuote(BlockContainer):
    def render(self, indent):
        return super().render(' >' + indent)

class UnorderedList(ItemContainer):
    def render(self, indent):
        super().render('-', indent)

class OrderedList(ItemContainer):
    def __init__(self, start=1, loose=False, items=None):
        super().__init__(loose, items)
        self._start = start
    
    def render(self, indent):
        super().render(len(self._start)+'.', indent)

class ThematicBreak:
    def render(self, indent):
        return indent+'***'

class CodeBlock:
    def __init__(self, content, lang=''):
        self._content = content
        self._lang = content
    
    def render(self, indent):
        return ( indent + '```\n' +
            indent + NL_RE.sub(re.escape(indent), self._content) +
            indent + '```\n' )

class RawHTML:
    def __init__(self, content):
        self._content = content
    
    def render(self, indent):
        return indent+self._content

class Paragraph(InlineContainer):
    def render(self, indent):
        return indent + super().render(indent)

class Heading(InlineContainer):
    def __init__(self, level=1, inlines=None):
        super().__init__(inlines)
        self._level = level
    
    def render(self, indent):
        return indent + '#'*self._level +  ' ' + super().render(indent)

class Text:
    def __init__(self, content):
        self._content = content
    
    def render(self, indent):
        return PNCT_RE.sub(r'\\\1', SPS_RE.sub(' ', self._content))

class CodeSpan:
    def __init__(self, content):
        self._content = content
    
    def render(self, indent):
        nticks = max([len(s) for s in BQS_RE.findall(self._content)]) + 1
        return r'`'*nticks + ' ' + self._content + ' ' + r'`'*nticks

class Strong(InlineContainer):
    def render(self, indent):
        text = super().render(indent)
        match = EXTRACT_SP_RE.fullmatch(text)
        return match.group(1) + '**' + match.group(2) + '**' + match.group(3)

class Emph(InlineContainer):
    def render(self, indent):
        text = super().render(indent)
        match = EXTRACT_SP_RE.fullmatch(text)
        return match.group(1) + '*' + match.group(2) + '*' + match.group(3)

class Link(InlineContainer):
    def __init__(self, url, title=None, inlines=None):
        super().__init__(inlines)
        self._url = url
        self._title = title
        if title is not None and BLNK_RE.search(self._title):
            raise ValueError('no blank line allowed in link title')
        
    def render(self, indent):
        return (
            '[' + super().render(indent) + '](' +
            BRCK_RE.sub(r'\\\1', self._url) +
            ( ' "' + DQ_RE.sub(r'\\"', self._title) + '"' if self._title is not None else '' ) +
            ' )' )

class Image(InlineContainer):
    def __init__(self, url, title=None, inlines=None):
        super().__init__(inlines)
        self._url = url
        self._title = title
        if title is not None and BLNK_RE.search(self._title):
            raise ValueError('no blank line allowed in link title')
        
    def render(self, indent):
        return (
            '![' + super().render(indent) + '](' +
            BRCK_RE.sub(r'\\\1', self._url) +
            ( ' "' + DQ_RE.sub(r'\\"', self._title) + '"' if self._title is not None else '' ) +
            ' )' )

class LineBreak:
    def render(self, indent):
        return '    \n'+indent

if __name__ == '__main__':
    print(BlockContainer([
        Heading(1, [Text('Hello, world!')]),
        Paragraph([Text('coucou, '), Text('toi!')]),
        Paragraph([Text('Comment, '), Strong([Text(' tu ')]), Text('vas? Ou pas, pas de truc top   .. precis.')]),
    ]).render(''))
