#! /usr/bin/env python
# xml2python script 1.0 beta
# release date April 6 2011

import sys
print "xml2matrix.py"
print "transform nodes and ties XML in a CSV square matrix"
if len(sys.argv) < 4:
	print ""
	print "Usage: python xml2matrix.py nodes.xml ties.xml matrix.csv"
	print ""
	sys.exit()
xmlNodePath = sys.argv[1]
xmlTiePath = sys.argv[2]
matrixPath = sys.argv[3]

## {{{ http://code.activestate.com/recipes/534109/ (r8)
import re
import xml.sax.handler

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return self._attrs.has_key(name)
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]
## end of http://code.activestate.com/recipes/534109/ }}}


nodes = xml2obj(open(xmlNodePath))
ties = xml2obj(open(xmlTiePath))

countNodes = len(nodes.node)

# compongo la prima riga CSV della matrice
f = open(matrixPath, 'w')
a=list()
a.append('FalsePivot;')
for node in nodes.node:
    a.append(node['ies'] + '_'+ node['cursSTR'] + '_' + node['idElem'] + ";")
a.append('\n')
f.write("".join(a))

# cerca le relazioni
c = 0;
block = 0;
import datetime
t1 = datetime.datetime.now()
for node in nodes.node:
    t0 = datetime.datetime.now()
    a=list()
    a.append(node['ies'] + "_" + node['cursSTR'] + "_" + node['idElem'] + ";")
    block = block + 1
    for node2 in nodes.node:
        if (node['idElem'] == node2['idElem']):
            a.append("D;")
        else:
            for tie in ties.node:
                tieBool = False
                if (node['idElem'] == tie['idA'] and node2['idElem'] == tie['idB']):
                    tieBool = True
                    a.append("1;")
                    c = c + 1
                    break
                else:
                    tieBool = False
            if (tieBool == False):
                a.append("0;")
    a.append("\n")
    f.write("".join(a))
    delta_t = datetime.datetime.now() - t0
    sys.stdout.write("estimated time "+str(delta_t * countNodes)+"\r")
    sys.stdout.flush()
    #if (block == 10):break
f.close()
delta_global = datetime.datetime.now() - t1
print "elaboration time "+str(delta_global)
print "found "+str(countNodes)+" nodes and "+str(c)+" ties"
node.kill
node2.kill
tie.kill
