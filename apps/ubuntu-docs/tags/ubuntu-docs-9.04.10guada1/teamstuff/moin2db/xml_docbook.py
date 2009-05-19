# -*- coding: utf-8 -*-
"""
    MoinMoin - docbook Formatter

    @copyright: 2005 by Mikko Virkkil�<mvirkkil@cc.hut.fi>
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.formatter.base import FormatterBase
from MoinMoin import wikiutil, i18n, config
from xml.sax import saxutils

class Formatter(FormatterBase):
    """
        Send plain text data.
    """

    hardspace = u'###CRAP###'

    section_should_break = ["abstract",'para', 'emphasis']

    def __init__(self, request, **kw):
        '''We should use this for creating the doc'''
        apply(FormatterBase.__init__, (self, request), kw)
        from xml.dom import getDOMImplementation
        dom = getDOMImplementation( "4DOM" ) 
        self.doc = dom.createDocument(None, "article", dom.createDocumentType("article","-//OASIS//DTD DocBook V4.3//EN","http://www.docbook.org/xml/4.3/docbookx.dtd" ))
        self.root = self.doc.documentElement
        self.realdepth=1

    def startDocument(self, pagename):
        info = self.doc.createElement("articleinfo")
        title = self.doc.createElement("title")
        title.appendChild( self.doc.createTextNode(pagename) )
        info.appendChild(title)
        self.root.appendChild(info)
        return ""

    def startContent(self, content_id="content", **kwargs):
        self.cur=self.root
        return ""


    def endDocument(self):
        from xml.dom.ext import PrettyPrint
        import StringIO
        txt=""
        a=StringIO.StringIO(txt)
        PrettyPrint(self.doc,a)
        txt=a.getvalue()
        a.close()
        return txt

    def text(self, text):
        self.cur.appendChild( self.doc.createTextNode(text) )
        return ""



    def heading(self, on, depth, **kw):
        while self.cur.nodeName in self.section_should_break:
            self.cur=self.cur.parentNode
               
        if on:
            if depth <= self.realdepth:
                for i in range(depth, self.realdepth):
                    while(self.cur.nodeName!="section"):
                        self.cur=self.cur.parentNode
                    
                    if len(self.cur.childNodes)<3:
                        self._addEmptyNode("para")

                    self.cur=self.cur.parentNode
                self.realdepth=depth

            section = self.doc.createElement("section")
            self.cur.appendChild(section)
            self.cur=section

            title=self.doc.createElement("title")
            self.cur.appendChild(title)
            self.cur=title
            self.curdepth=depth
            self.realdepth+=1
        else:
            self.cur=self.cur.parentNode


        return ""
            


    def paragraph(self, on):
        FormatterBase.paragraph(self, on)
        if on:
            para=self.doc.createElement("para")
            self.cur.appendChild(para)
            self.cur=para
        else:
            self.cur=self.cur.parentNode
        return ""

    def linebreak(self, preformatted=1):
        if preformatted:
            self.text('\\n')
        else:
            self.text('CRAP')
        return ""


    def _handleNode(self, name, on, attributes=()):
        if on:
            node=self.doc.createElement(name)
            self.cur.appendChild(node)
            if len(attributes)>0:
                for (name,value) in attributes:
                    node.setAttribute(name,value)
            self.cur=node
        else:
            self.cur=self.cur.parentNode
        return ""

    def _addEmptyNode(self,name, attributes=()):
        node=self.doc.createElement(name)
        self.cur.appendChild(node)
        if len(attributes)>0:
            for (name,value) in attributes:
                node.setAttribute(name,value)

### Inline ##########################################################

    def _handleFormatting(self,name, on, attributes=()):
        #We add all the elements we create to the list of elements that should not contain a section        
        if name not in self.section_should_break:
            self.section_should_break.append(name)

        return self._handleNode(name,on,attributes)

    def strong(self, on):
        return self._handleFormatting("emphasis",on , [['role','bold']] )

    def emphasis(self, on):
        return self._handleFormatting("emphasis",on)

    def underline(self, on):
        return self._handleFormatting("emphasis",on , [['role','underline']] )

    def highlight(self, on):
        return self._handleFormatting("emphasis",on , [['role','highlight']] )

    def sup(self, on):
        return self._handleFormatting("superscript",on)

    def sub(self, on):
        return self._handleFormatting("subscript",on)

    def code(self, on):
        return self._handleFormatting("code",on)

    def preformatted(self, on):
        return self._handleFormatting("screen",on)


### Lists ###########################################################

    def number_list(self, on, type=None, start=None):
        docbook_ol_types={  '1':"arabic", 
                            'a':"loweralpha", 
                            'A':"upperalpha",
                            'i':"lowerroman",
                            'I':"upperroman" }

        if type and docbook_ol_types.has_key(type):
            attrs=[("numeration", docbook_ol_types[type])]
        else:
            attrs=[]

        return self._handleNode('orderedlist',on,attrs)


    def bullet_list(self, on):
        return self._handleNode("itemizedlist",on)

    def definition_list(self, on):
        return self._handleNode("glosslist",on)        


    '''When on is false, we back out just on level. This is
       ok because we know definition_desc gets called, and we
       back out two levels there'''
    def definition_term(self, on, compact=0):
        if on:
            entry=self.doc.createElement('glossentry')
            term=self.doc.createElement('glossterm')
            entry.appendChild(term)
            self.cur.appendChild(entry)

            self.cur=term
        else:
            self.cur=self.cur.parentNode
        return ""
   
    '''We backout two levels when 'on' is false, to leave the glossentry stuff'''
    def definition_desc(self, on):
        if on:
            return self._handleNode("glossdef",on)
        else:
            self.cur=self.cur.parentNode.parentNode
            return ""

    def listitem(self, on, **kw):
        if on:
            node=self.doc.createElement("listitem")
            self.cur.appendChild(node)

            self.cur=node
        else:
            self.cur=self.cur.parentNode
        return ""


### Links ###########################################################

    #FIXME: This is quite crappy
    def pagelink(self, on, pagename='', page=None, **kw):
        apply(FormatterBase.pagelink, (self, on, pagename, page), kw)

        return self.interwikilink(on,'self',pagename) #FIXME

    #FIXME: This is even more crappy
    def interwikilink(self, on, interwiki='', pagename='', **kw):
        if not on:
            self.url(on,kw)
            return ""

        wikitag, wikiurl, wikitail, wikitag_bad = wikiutil.resolve_wiki(self.request, '%s:%s' % (interwiki, pagename))
        wikiurl = wikiutil.mapURL(self.request, wikiurl)
        href = wikiutil.join_wiki(wikiurl, wikitail)
        self.url(on, href)

        #return self._handleNode("link",on,[['linkend',interwiki+"/"+pagename]]) #FIXME
        return ""
            
    def url(self, on, url=None, css=None, **kw):
        return self._handleNode("ulink",on,[['url',url]])

    def anchordef(self, name):
        self._handleNode("anchor",True,[['id',name]])
        self._handleNode("ulink",False)
        return ""

    def anchorlink(self, on, name='', id=None):
        attrs=[]
        if name!='':
            attrs.append( ('endterm',name) )
        if id!=None:
            attrs.append( ('linkend',id) )
        elif name!='':
            attrs.append( ('linkend',name) )

        return self._handleNode("link",on,attrs)


### Images and Smileys ##############################################
    def image(self, **kw):
        media=self.doc.createElement('inlinemediaobject')

        imagewrap=self.doc.createElement('imageobject')
        media.appendChild(imagewrap)

        image=self.doc.createElement('imagedata')
        if kw.has_key('src'):
            image.setAttribute('fileref',kw['src'])
        if kw.has_key('width'):
            image.setAttribute('width',kw['width'])
        if kw.has_key('height'):
            image.setAttribute('depth',kw['height'])
        imagewrap.appendChild(image)
        
        if kw.has_key('alt'):
            txtcontainer=self.doc.createElement('textobject')
            media.appendChild(txtcontainer)        
            txtphrase=self.doc.createElement('phrase')
            txtphrase.appendChild( self.doc.createTextNode(kw['alt']) )
            txtcontainer.appendChild(txtphrase)        
        
        self.cur.appendChild(media)
        return ""        
 
    def smiley(self, text):
        w, h, b, img = config.smileys[text.strip()]
        href = img
        if not href.startswith('/'):
            href = self.request.theme.img_url(img)
        return self.image(src=href, alt=text, width=str(w), height=str(h))

    def icon(self, type):
        return ''#self.request.theme.make_icon(type)

### Tables ##########################################################

    #FIXME: We should copy code from text_html.py for attr handling
    

    def table(self, on, attrs=None):
        sanitized_attrs=[]
        if attrs and attrs.has_key('id'):
            sanitized_attrs[id]=attrs['id']

        self._handleNode("table",on,sanitized_attrs)
        if on:
            self._addEmptyNode("caption") #dtd for table requires caption

        return ""
    
    def table_row(self, on, attrs=None):
        sanitized_attrs=[]
        if attrs and attrs.has_key('id'):
            sanitized_attrs[id]=attrs['id']
        return self._handleNode("tr",on,sanitized_attrs)
    
    def table_cell(self, on, attrs=None):
        sanitized_attrs=[]
        if attrs and attrs.has_key('id'):
            sanitized_attrs[id]=attrs['id']
        return self._handleNode("td",on,sanitized_attrs)


### Code ############################################################
    def code_area(self, on, code_id, code_type='code', show=0, start=-1, step=-1):
        if show:
            show = 'numbered'
        else:
            show = 'unnumbered'
        if start<1:
            start=1
        
        attrs=[ ['id',code_id],
                ['linenumbering',show],
                ['startinglinenumber',str(start)],
                ['language',code_type],
                ['format','linespecific'] 
                ]
        return self._handleFormatting("screen", on, attrs )

    def code_line(self, on):
        return '' #No clue why something should be done here
    



    def code_token(self, on, tok_type):
        toks_map={  'ID':'methodname',
                    'Operator':'',
                    'Char':'',
                    'Comment':'lineannotation',
                    'Number':'',
                    'String':'phrase',
                    'SPChar':'',
                    'ResWord':'token',
                    'ConsWord':'symbol',
                    'Error':'errortext',
                    'ResWord2':'',
                    'Special':'',
                    'Preprc':'',
                    'Text':''}
        if toks_map.has_key(tok_type) and toks_map[tok_type] != '':
            return self._handleFormatting(toks_map[tok_type],on)
        else:
            return ""


### Not supported ###################################################
    def rule(self, size=0):
        return ""

    def small(self, on):
        return ""

    def big(self, on):
        return ""

    def rawHTML(self, markup):
        """ This allows emitting pre-formatted HTML markup, and should be
            used wisely (i.e. very seldom).

            Using this event while generating content results in unwanted
            effects, like loss of markup or insertion of CDATA sections
            when output goes to XML formats.
        """
        return ''

    def escapedText(self, on):
        """ This allows emitting text as-is, anything special will
            be escaped (at least in HTML, some text output format
            would possibly do nothing here)
        """
        return ''
