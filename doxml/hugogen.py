#!/bin/env python3

from mdgen import *

class Alert(BlockContainer):
    def __init__(self, title=None, color=None, blocks=None):
        BlockContainer.__init__(self, blocks)
        self._title = title
        self._color = color
    
    def render(self, indent):
        return (
            '{{% alert ' + 
            ('title="'+self._title + '" ' if self._title is not None else '') +
            ('color="'+self._color + '" ' if self._color is not None else '') +
            '%}}\n' +
            super().render(indent) +
            '\n{{% /alert %}}'
            )

class DefinitionList(BlockContainer):
    def render(self, indent):
        return ("\n").join([END_SP_RE.sub('', b.render(indent)) for b in self if b.render(indent).strip() != ''])

class TermItem(Paragraph):
    pass
    
class LooseDefinitionItem(BlockContainer):
    def render(self, indent):
        return ':' + super().render('    '+indent)[1:]

class CompactDefinitionItem(Paragraph):
    def render(self, indent):
        return ':' + super().render('    '+indent)[1:]

class Table(BlockContainer):
    def __init__(self, aligns=None, blocks=None):
        BlockContainer.__init__(self, blocks=blocks)
        if aligns is None:
            self.aligns = []
        else:
            self.aligns = aligns
    
    def render(self, indent):
        while len(self.aligns) < len(self[0]):
            self.aligns.append('')
        return (
            self[0].render(indent) + '\n'
          + indent+'| '+ ' | '.join([
              ':--' if a == 'l' else
              ':-:' if a == 'c' else
              '--:' if a == 'r' else
              '---'
              for a in self.aligns
            ]) + ' |\n'
          + '\n'.join([
              r.render(indent)
              for r in self[1:]
            ])
          )

class TableRow(BlockContainer):
    def render(self, indent):
        return indent+'| '+ ' | '.join([b.render('') for b in self]) + ' |'
