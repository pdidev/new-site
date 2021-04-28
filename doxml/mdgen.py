#!/bin/env python3

import re

PNCT_RE = re.compile(r'([-\\!\[\]"#$%&\'\(\)*+,-./:;<=>?@^_`{|}~])')
SPS_RE = re.compile(r'\s+')
NL_RE = re.compile(r'\n')
BRCK_RE = re.compile(r'([<>])')
BLNK_RE = re.compile(r'^\s*$', re.MULTILINE)
BQS_RE = re.compile(r'`+')
DQ_RE = re.compile(r'"')
END_SP_RE = re.compile(r'\s+$')

EXTRACT_SP_RE = re.compile(r'^(\s*)(.*[^\s])(\s*)$')

class BlockContainer(list):
    def __init__(self, blocks=None):
        if blocks is None:
            list.__init__(self)
        else:
            list.__init__(self, blocks)
    
    def render(self, indent):
        return ("\n\n").join([END_SP_RE.sub('', b.render(indent)) for b in self if b.render(indent).strip() != ''])

class InlineContainer(list):
    def __init__(self, inlines=None):
        if inlines is None:
            list.__init__(self)
        else:
            list.__init__(self, inlines)
    
    def render(self, indent):
        return "".join([i.render(indent) for i in self]).strip()

class List(BlockContainer):
    def render(self, prefix, indent):
        items = []
        for i in self:
            p = prefix()
            items.append(indent + p + i.render(' '*max(len(p)+1, 4))[len(p):])
        return "\n".join(items)

class BlockQuote(BlockContainer):
    def render(self, indent):
        return super().render(' >' + indent)

class UnorderedList(List):
    def render(self, indent):
        return super().render(lambda: '-', indent)

class OrderedList(List):
    def __init__(self, start=1, items=None):
        super().__init__(items)
        self._start = start
    
    def render(self, indent):
        val = self._start
        def prefix():
            nonlocal val
            res = str(val)+'.'
            val = val+1
            return res
        return super().render(prefix, indent)

class ThematicBreak:
    def render(self, indent):
        return indent+'***'

class CodeBlock:
    def __init__(self, content, lang=''):
        self._content = content
        self._lang = lang
    
    def render(self, indent):
        return ( indent + '```'+self._lang+'\n' +
            indent + NL_RE.sub('\n'+indent, self._content) +'\n'+
            indent + '```' )

class RawHTML:
    def __init__(self, content):
        self._content = content
    
    def render(self, indent):
        return indent+self._content

class Paragraph(InlineContainer):
    def render(self, indent):
        return indent + super().render(indent)

class LooseItem(BlockContainer):
    def render(self, indent):
        return super().render(indent)+'\n'

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
        nticks = max([len(s) for s in BQS_RE.findall(self._content)]+[0]) + 1
        return r'`'*nticks + ' ' + self._content + ' ' + r'`'*nticks

class Strong(InlineContainer):
    def render(self, indent):
        text = super().render(indent)
        match = EXTRACT_SP_RE.fullmatch(text)
        if match:
            return match.group(1) + '**' + match.group(2) + '**' + match.group(3)
        else:
            return ''

class Emph(InlineContainer):
    def render(self, indent):
        text = super().render(indent)
        match = EXTRACT_SP_RE.fullmatch(text)
        if match:
            return match.group(1) + '*' + match.group(2) + '*' + match.group(3)
        else:
            return ''

class Link(InlineContainer):
    def __init__(self, url=None, title=None, inlines=None):
        super().__init__(inlines)
        self._url = url
        self._title = title
        if title is not None and BLNK_RE.search(self._title):
            raise ValueError('no blank line allowed in link title')
        
    def render(self, indent):
        return (
            '[' + super().render(indent) + ']( ' +
            ( '<' + BRCK_RE.sub(r'\\\1', self._url) + '>' if self._url is not None else '' ) +
            ( ' "' + DQ_RE.sub(r'\\"', self._title) + '"' if self._title is not None else '' ) +
            ' )' )

class Image(InlineContainer):
    def __init__(self, url=None, title=None, inlines=None):
        super().__init__(inlines)
        self._url = url
        self._title = title
        if title is not None and BLNK_RE.search(self._title):
            raise ValueError('no blank line allowed in link title')
        
    def render(self, indent):
        return (
            '{{< figure title="' + super().render(indent) + '" src="' +
            BRCK_RE.sub(r'\\\1', self._url) +
            ( ' "' + DQ_RE.sub(r'\\"', self._title) + '"' if self._title is not None else '' ) +
            '" >}}' )

class LineBreak:
    def render(self, indent):
        return '    \n'+indent

if __name__ == '__main__':
    print(BlockContainer([
        Heading(1, [Text('Hello, world!')]),
        Paragraph([Text('coucou, '), Text('toi!')]),
        Paragraph([Text('Comment, '), Strong([Text(' tu ')]), Text('vas? Ou pas, pas de truc top   .. precis.')]),
    ]).render(''))
