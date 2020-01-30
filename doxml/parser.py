#!/bin/env python3

import xml.etree.ElementTree as ET
import os.path
from hugogen import *
from cppmodel import *

def non_empty(txt):
    return txt and txt.strip()

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

def add_if_not_empty(cnt, node, path=None, attr=None, tr=None, key=None):
    if tr is None:
        if attr is None:
            tr = lambda x: "".join(x.itertext())
        else:
            tr = lambda x: x
    if key is None:
        key = path
    if node and path:
        node = node.find(path)
    if empty_node(node):
        return
    if attr:
        node = node.get(attr)
    node = tr(node)
    try:
        cnt[key] = node
    except TypeError:
        try:
            cnt.append(node)
        except AttributeError:
            cnt.__setattr__(key, node)

def itertag(node, handlers=None, text_handler=(lambda t: None), catchall=None):
    if handlers is None:
        handlers = {}
    if node.text is not None:
        text_handler(node.text)
    for sn in node:
        try:
            (handlers[sn.tag])(sn)
        except KeyError:
            if catchall is not None:
                catchall(sn)
            else:
                raise AssertionError("Warning, unhandled tag: "+sn.tag)
        if sn.tail is not None:
            text_handler(sn.tail)
    
class Doxml:
    def __init__(self, file, imgpath=''):
        self.file = file
        self.tree = ET.parse(file)
        self.imgpath = imgpath
        self.images = []
        self.pages = {}
        self.root_namespace = Namespace()
        self.ids = {}
        for compounddef in self.tree.findall('compounddef[@kind="class"]'):
            self.parse_class(compounddef)
        for compounddef in self.tree.findall('compounddef[@kind="struct"]'):
            self.parse_class(compounddef)
        for compounddef in self.tree.findall('compounddef[@kind="union"]'):
            pass
        for compounddef in self.tree.findall('compounddef[@kind="type"]'):
            pass
        for compounddef in self.tree.findall('compounddef[@kind="namespace"]'):
            self.parse_namespace(compounddef)
        for compounddef in self.tree.findall('compounddef[@kind="group"]'):
            pass
        for compounddef in self.tree.findall('compounddef[@kind="example"]'):
            pass
        for compounddef in self.tree.findall('compounddef[@kind="page"]'):
            self.parse_page(compounddef)
        for compounddef in self.tree.findall('compounddef[@kind="dir"]'):
            pass
        for compounddef in self.tree.findall('compounddef[@kind="file"]'):
            pass

    def parse_namespace(self, node: ET.Element):
        result = Namespace.Definition(defined=self.root_namespace)
        for name in node.findtext('compoundname').split('::'):
            result = result.defined.namespaces.setdefault(name, Namespace.Definition(name, Namespace()))
        self.ids[node.get('id')] = result
        add_if_not_empty(result, node, 'location', 'file')
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'detaileddescription', tr=lambda n: self.description(n))
        for sn in node.findall('innerclass'):
            try:
                cl = self.ids[sn.get('refid')]
                del self.root_namespace.classes[cl.name]
                cl.name = cl.name[len(node.findtext('compoundname'))+2:]
                result.defined.classes[cl.name] = cl
            except KeyError:
                pass
        for sn in node.findall('sectiondef[@kind="typedef"]/memberdef'):
            td = self.parse_definition(sn, self.parse_typedef)
            result.defined.typedefs[td.name] = td
        for sn in node.findall('sectiondef[@kind="enum"]/memberdef'):
            en = self.parse_definition(sn, self.parse_enum)
            result.defined.enums[en.name] = en
        for sn in node.findall('sectiondef[@kind="func"]/memberdef'):
            fn = self.parse_definition(sn, self.parse_function)
            funclist = result.defined.functions.setdefault(fn.name, []).append(fn)
        for sn in node.findall('sectiondef[@kind="var"]/memberdef'):
            var = self.parse_definition(sn, self.parse_variable)
            result.defined.variables[var.name] = var

    def parse_definition(self, node: ET.Element, parse_defined):
        result = Namespace.Definition()
        result.name = node.findtext('name')
        self.ids[node.get('id')] = result
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'detaileddescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'location', 'file')
        result.defined = parse_defined(node)
        return result

    def parse_type(self, node: ET.Element):
        return "".join(node.itertext())

    def parse_typedef(self, node: ET.Element):
        return self.parse_type(node.find('type'))

    def parse_enum(self, node: ET.Element):
        result = Enum_()
        if node.get('strong') == 'yes':
            result.strongly_typed = True
        add_if_not_empty(result, node, 'type', tr=lambda n: "".join(n.itertext()))
        for sn in node.findall('enumvalue'):
            self.parse_enum_value(result, sn)
        return result

    def parse_enum_value(self, out, node: ET.Element):
        result = Namespace.Definition()
        result.name = node.findtext('name')
        out.values.append(result)
        self.ids[node.get('id')] = result
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'detaileddescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'location', 'file')
        result.defined=Variable()

    def parse_function(self, node: ET.Element):
        result = Function()
        result.result.type = self.parse_type(node.find('type'))
        for sn in node.findall('param'):
            par = self.parse_function_param(sn)
            result.parameters[par.name] = par
        for sn in node.findall('detaileddescription/para/parameterlist[@kind="param"]/parameteritem'):
            self.parse_function_param_desc(result.parameters, sn)
        add_if_not_empty(result.result, node, 'detaileddescription/para/simplesect[@kind="return"]', key='detaileddescription', tr=lambda n: self.description(n))
        return result

    def parse_function_param(self, node: ET.Element):
        result = Function.Parameter()
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'defname', key='name')
        add_if_not_empty(result, node, 'declname', key='name')
        result.defined = Function.Parameter()
        result.defined.type = self.parse_type(node.find('type'))
        return result

    def parse_function_param_desc(self, out, node: ET.Element):
        try:
            para = out[node.findtext('parameternamelist/parametername')]
        except KeyError:
            print("Warning: invalid parameter name: "+node.findtext('parameternamelist/parametername'), file=sys.stderr)
            return
        add_if_not_empty(para, node, 'parameterdescription', key='detaileddescription', tr=lambda n: self.description(n))

    def parse_variable(self, node: ET.Element):
        result = Variable()
        result.type = self.parse_type(node.find('type'))
        return result
    
    def parse_class(self, node: ET.Element):
        result = self.ids.setdefault(node.get('id'), Namespace.Definition(defined=Class_()))
        if result.name is None:
            result.name = node.findtext('compoundname')
            self.root_namespace.classes[result.name] = result
        for sn in node.findall('innerclass'):
            cl = self.ids.setdefault(sn.get('refid'), Class_.Definition())
            if cl.name is not None:
                del self.root_namespace.classes[cl.name]
                cl = Class_.Definition(defined=cl.defined)
            else:
                cl.defined = Class_()
            cl.name = self.parse_type(sn)[len(node.findtext('compoundname'))+2:]
            result.defined.classes[cl.name] = cl
        for sn in node.findall('sectiondef/memberdef[@kind="typedef"]'):
            td = self.parse_member_definition(sn, self.parse_typedef)
            result.defined.typedefs[td.name] = td
        for sn in node.findall('sectiondef/memberdef[@kind="enum"]'):
            en = self.parse_member_definition(sn, self.parse_enum)
            result.defined.enums[en.name] = en
        for sn in node.findall('sectiondef/memberdef[@kind="function"][@static="yes"]'):
            fn = self.parse_member_definition(sn, self.parse_function)
            result.defined.functions.setdefault(fn.name, []).append(fn)
        for sn in node.findall('sectiondef/memberdef[@kind="function"][@static="no"]'):
            fn = self.parse_member_definition(sn, self.parse_function)
            result.defined.functions.setdefault(fn.name, []).append(fn)
        for sn in node.findall('sectiondef/memberdef[@kind="variable"][@static="yes"]'):
            var = self.parse_member_definition(sn, self.parse_variable)
            result.defined.variables[var.name] = var
        for sn in node.findall('sectiondef/memberdef[@kind="variable"][@static="no"]'):
            var = self.parse_member_definition(sn, self.parse_variable)
            result.defined.variables[var.name] = var
    
    def parse_member_definition(self, node: ET.Element, parse_defined):
        result = Class_.Definition()
        result.name = node.findtext('name')
        self.ids[node.get('id')] = result
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'detaileddescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'location', 'file')
        result.visibility = node.get('prot')
        result.defined = parse_defined(node)
        return result

    def parse_member_function(self, node: ET.Element):
        result = Class_.MemberFunction()
        result.result.type = self.parse_type(node.find('type'))
        for sn in node.findall('param'):
            par = self.parse_function_param(sn)
            result.parameters[par.name] = par
        for sn in node.findall('detaileddescription/para/parameterlist[@kind="param"]/parameteritem'):
            self.parse_function_param_desc(result.parameters, sn)
        add_if_not_empty(result.result, node, 'detaileddescription/para/simplesect[@kind="return"]', key='detaileddescription', tr=lambda n: self.description(n))
        result.virtual = node.get('virtual')
        return result

    def parse_page(self, node: ET.Element):
        result = dict()
        add_if_not_empty(result, node, 'title')
        add_if_not_empty(result, node, 'briefdescription', tr=lambda n: self.description(n))
        add_if_not_empty(result, node, 'detaileddescription', tr=lambda n: self.description(n))
        self.pages[node.findtext('compoundname')] = result
    
    def description(self, node: ET.Element):
        result = BlockContainer()
        self.doc_sect(result, node, 0)
        if not result:
            result = None
        return result

    def doc_sect(self, out: BlockContainer, node, level):
        add_if_not_empty(out, node, path='title', tr=lambda n: Heading(level+1, [Text(n.text)]))
        itertag(node, {
            'title': lambda n: None,
            'internal': lambda n: None,
            'para': lambda n: self.doc_para(out, n),
            'sect'+str(level+1): lambda n: self.doc_sect(out, n, level+1),
            })

    def doc_para(self, out: BlockContainer, node: ET.Element):
        class ParagraphList:
            def __init__(self, block_container: BlockContainer):
                self._container = block_container
                self._current_paragraph = None
            
            def get_para(self):
                if self._current_paragraph is None:
                    self._current_paragraph = Paragraph()
                    self._container.append(self._current_paragraph)
                return self._current_paragraph
            
            def append(self, inline):
                self.get_para().append(inline)
                
            def extend(self, inlines):
                self.get_para().extend(inlines)
            
            def get_out(self):
                self._current_paragraph = None
                return self._container
        
        if node.find('parameterlist') or node.find('simplesect[@kind="return"]'):
            return
        
        subout = ParagraphList(out)
        itertag(node, {
            'hruler': lambda n: subout.get_out().append(ThematicBreak()),
            'image': lambda n: self.doc_image(subout.get_out(), n),
            'itemizedlist': lambda n: self.doc_list(subout.get_out(), n, ordered=False),
            'linebreak': lambda n: subout.get_out().append(LineBreak()),
            'orderedlist': lambda n: self.doc_list(subout.get_out(), n, ordered=True),
            'programlisting': lambda n: self.listing(subout.get_out(), n),
            'simplesect': lambda n: self.doc_simplesect(subout.get_out(), n),
            'table': lambda n: self.doc_table(subout.get_out(), n),
            'variablelist': lambda n: self.doc_variable_list(subout.get_out(), n),
            }, 
        text_handler=lambda t: out.append(Text(t)),
        catchall = lambda n: self.doc_title_cmd_group(subout.get_para(), n)
        )

    def doc_title_type(self, out: InlineContainer, node: ET.Element):
        itertag(node, text_handler = lambda t: out.append(Text(t)), catchall = lambda n: self.doc_title_cmd_group(out, n))

    def doc_title_cmd_group(self, out: InlineContainer, node: ET.Element):
        if node.tag == 'lsquo':
            out.append(Text("‘"))
        elif node.tag == 'rsquo':
            out.append(Text("’"))
        elif node.tag == 'lsquo':
            out.append(Text("‘"))
        elif node.tag == 'lsquo':
            out.append(Text("‘"))
        elif node.tag == 'lsquo':
            out.append(Text("‘"))
        elif node.tag == 'ulink':
            self.doc_url_link(out, node)
        elif node.tag == 'bold':
            subout = Strong()
            out.append(subout)
            self.doc_title_type(subout, node) #Warning: the doxygen xsd says doc_markup, but this seems difficult
        elif node.tag == 'emphasis':
            subout = Emph()
            out.append(subout)
            self.doc_title_type(subout, node) #Warning: the doxygen xsd says doc_markup, but this seems difficult
        elif node.tag == 'computeroutput':
            out.append(CodeSpan(("".join(node.itertext())))) #Warning: doxygen supports markup inside, MarkDown does not
        elif node.tag == 'ref':
            self.doc_ref_text(out, node)
        elif node.tag == 'anchor':
            pass #TODO: we might want to handle that...
        else:
            raise AssertionError('No such doc_title_cmd: '+node.tag)

    def doc_table(self, out: BlockContainer, node: ET.Element):
        subout = Table()
        out.append(subout)
        itertag(node, {
            'caption': lambda n: None, #TODO: handle in a figure
            'row': lambda n: self.doc_row(subout, n),
            })
        
    def doc_row(self, out: Table, node: ET.Element):
        subout = TableRow()
        out.append(subout)
        itertag(node, { 'entry': lambda n: self.doc_entry(subout, n) })
        
    def doc_entry(self, out: TableRow, node: ET.Element):
        if len(node.findall('para')) != 1:
            raise AssertionError("unhandled multi-line table cell")
        itertag(node, { 'para': lambda n: self.doc_para(out, n) })

    def doc_variable_list(self, out: BlockContainer, node: ET.Element):
        subout = DefinitionList()
        out.append(subout)
        itertag(node, {
            'varlistentry': lambda n: self.doc_var_list_entry(subout, n),
            'listitem': lambda n: self.doc_list_item(subout, n),
            })

    def doc_var_list_entry(self, out: DefinitionList, node: ET.Element):
        def term(node: ET.Element):
            subout = TermItem()
            out.append(subout)
            self.doc_title_type(subout, node)
        itertag(node, {'term': term})

    def doc_list_item(self, out: DefinitionList, node: ET.Element):
        subout = LooseDefinitionItem()
        out.append(subout)
        itertag(node, {'para': lambda n: self.doc_para(subout, n)})

    def doc_image(self, out: BlockContainer, node: ET.Element):
        #TODO: handle as a hugo figure
        para = Paragraph()
        out.append(para)
        self.images.append(node.get('name'))
        img = Image(url=self.imgpath+node.get('name'))
        para.append(img)
        itertag(node, text_handler = lambda t: out.append(Text(t)), catchall = lambda n: self.doc_title_cmd_group(img, n))
        
    def listing(self, out: BlockContainer, node: ET.Element):
        listing = []
        for codeline in node:
            line = ''
            for highlight in codeline:
                if non_empty(highlight.text):
                    line += highlight.text
                for hl in highlight:
                    if hl.tag == 'sp':
                        line += ' '
                    elif hl.tag == 'ref':
                        line += hl.text
                    if non_empty(hl.tail):
                        line += hl.tail
            line = re.sub(r'\s*$', '', line)
            listing.append(line)
        out.append(CodeBlock("\n".join(listing)))

    def doc_url_link(self, out: InlineContainer, node: ET.Element):
        subout = Link(node.get('url'))
        out.append(subout)
        itertag(node, text_handler = lambda t: out.append(Text(t)), catchall = lambda n: self.doc_title_cmd_group(subout, n))

    def doc_simplesect(self, out: BlockContainer, node: ET.Element):
        subout = Alert(node.get('title'))
        out.append(subout)
        itertag(node, { 'para': lambda n: self.doc_para(subout, n) })

    def doc_list(self, out: BlockContainer, node: ET.Element, ordered):
        if ordered:
            subout = OrderedList()
        else:
            subout = UnorderedList()
        out.append(subout)
        itertag(node, { 'listitem': lambda n: self.list_item(subout, n) })

    def list_item(self, out: List, node: ET.Element):
        subout = LooseItem()
        itertag(node, { 'para': lambda n: self.doc_para(subout, n) })
        if len(subout) > 1:
            out.append(subout)
        elif len(subout) > 0:
            out.append(subout[0])
    
    def doc_ref_text(self, out: InlineContainer, node: ET.Element):
        subout = Link(node.get('kindref').strip()+':'+node.get('refid').strip()) #TODO: replace by hugo
        out.append(subout)
        itertag(node, text_handler = lambda t: out.append(Text(t)), catchall = lambda n: self.doc_title_cmd_group(subout, n))

if __name__ == '__main__':
    import sys
    import yaml
    yaml.add_representer(BlockContainer, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data.render('').strip()+'\n', style=r'|'))
    if len(sys.argv) > 1:
        x = Doxml(sys.argv[1])
    else:
        x = Doxml("../data/combined.xml")
    yaml.dump(x.root_namespace, sys.stdout)
