# -*- coding: utf-8 -*-

import xml.dom.minidom
from xml.dom.minidom import Node
import os.path
import string
import codecs
import sys
import time

# GLOBAL VARIABLES

footnotes = {}
footnote_id = 0


# FUNCTIONS

def getChildrenByTagName(obj, tag):
    matches = []
    for o in obj.childNodes:
        if o.nodeType == 1 and o.tagName == tag:
            matches.append(o)
    return matches

# Return data of node
def d(input):
    if len(input) > 0:
        return input[0].firstChild.data
    
def setBookInfo(tle, tle_name):
    output = u''
    # Book Title
    try:
        title = getChildrenByTagName(tle, 'title')
        output += head[0] + d(title) + head[1]
        output += '<h1 id="title">' + handlePChildren(title[0].childNodes) + '</h1>'
    except:
        exit("Error: Missing " + tle_name + " <title> tag.")
    
    # Book Subtitle If Exists
    subtitle = getChildrenByTagName(tle, 'subtitle')
    if d(subtitle):
        output += '<p id="subtitle">' + handlePChildren(subtitle[0].childNodes) + "</p>" # TODO: Make this work with enclosed italics, etc.
    
    # Book Author
    try:
        output += '<p id="author"><i>by</i> ' + handlePChildren(getChildrenByTagName(tle, 'author')[0].childNodes) + '</p>'
    except:
        exit("Error: Missing " + tle_name + " <author> tag.")
    
    # try:
    #       publication_date = d(getChildrenByTagName(tle, 'publication_date'))
    #       output += '<p id="publication_date">published ' + time.strftime("%d %B %Y", time.strptime(publication_date, "%Y-%m-%d")) + '</p>'
    #   except:
    #       exit("Error: Missing or invalid " + tle_name + " <publication_date> tag.")
    
    # Book Dedication If Exists
    dedication = getChildrenByTagName(tle, 'dedication')
    if dedication:
        output += '<div id="dedication">' + handlePChildren(dedication[0].childNodes) + '</div><br class="page_break" />'
    
    # Book Quotes If Exist
    if tle_name == 'volume':
        if getChildrenByTagName(tle, 'quote'):
            output += '<br class="page_break" />'
            for quote in getChildrenByTagName(tle, 'quote'):
                output += handleQuote(quote)
            output += '<br class="page_break" />'
    
    return output

def handleBook(book):
    output = ''
    
    # Quotes If Exist
    if getChildrenByTagName(book, 'quote'):
        for quote in getChildrenByTagName(book, 'quote'):
            output += handleQuote(quote)
    else:
        output += u'<p align="center" style="font-size: 40px; text-indent: 0px;">✠</p>'
    
    parts = getChildrenByTagName(book, 'part')
    if parts:
        chapters = getChildrenByTagName(book, 'chapter')
        if chapters:
            for chapter in chapters:
                output += handleChapter(chapter)
        for part in parts:
            output += handlePart(part)
    else:
        for chapter in getChildrenByTagName(book, 'chapter'):
            output += handleChapter(chapter)
        
    return output

def handlePart(part):
    output = ''
    
    # Part Num & Title
    if part.getAttribute('num'):
        output += '<h1 class="part_title">Part ' + part.getAttribute('num') + '</h1>'
    else:
        exit("Error: Missing num attribute in <part> tag.")
        
    if getChildrenByTagName(part, 'title'):
        output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(part, 'title')[0].childNodes) + '</p>'
        
    if getChildrenByTagName(part, 'subtitle'):
        output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(part, 'subtitle')[0].childNodes) + '</p>'
    
    # Quotes If Exist
    if getChildrenByTagName(part, 'quote'):
        for quote in getChildrenByTagName(part, 'quote'):
            output += handleQuote(quote)
    else:
        output += u'<p align="center" style="font-size: 40px; text-indent: 0px;">✠</p>'
    
    # Chapters
    for chapter in getChildrenByTagName(part, 'chapter'):
        output += handleChapter(chapter)
    
    return output

def handleChapter(chapter):
    output = ''
    
    # Chapter Num & Title
    heading = ''
    if chapter.getAttribute('num'):
        heading += '<h1 class="chapter_title">Chapter ' + chapter.getAttribute('num') + '</h1>'
        if getChildrenByTagName(chapter, 'title'):
            heading += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(chapter, 'title')[0].childNodes) + '</p>'
        if getChildrenByTagName(chapter, 'subtitle'):
            heading += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(chapter, 'subtitle')[0].childNodes) + '</p>'
    else:
        if getChildrenByTagName(chapter, 'title'):
            heading += '<h1 class="chapter_title">' + handlePChildren(getChildrenByTagName(chapter, 'title')[0].childNodes) + '</h1>'
        if getChildrenByTagName(chapter, 'subtitle'):
            heading += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(chapter, 'subtitle')[0].childNodes) + '</p>'
    
    if heading == '':
        heading = '<br class="page_break" />'
    
    output += heading
    
    output += handleChapterInternals(chapter)
    
    output += returnFootnotes()
    
    return output

def handleChapterInternals(chapter, level = 1):
    output = ''
    
    for e in chapter.childNodes:
        if e.nodeType == 3:
            output += e.data
        elif e.nodeType == 1:
            if e.nodeName == 'subtitle':
                if level > 1:
                    exit("Error: Invalid location for a subtitle.")
            elif e.nodeName == 'title':
                if level > 1:
                    output += '<h3>' + handlePChildren(e.childNodes) + '</h3>'
            elif e.nodeName == 'p':
                attributes = ''
                if e.getAttribute('align'):
                    attributes = ' class="aligned" align="' + e.getAttribute('align') + '"'
                
                if e.getAttribute('outdent'):
                    if e.getAttribute('outdent') == 'true':
                        attributes += ' class="outdent"'
                
                output += '<p' + attributes + '>'
                
                output += handlePChildren(e.childNodes)
                
                output += '</p>'
            elif e.nodeName == 'quote':
                output += handleQuote(e)
            elif e.nodeName == 'code':
                output += '<pre>' + e.firstChild.data +'</pre>'
            elif e.nodeName == 'table':
                output += handleTable(e)
            elif e.nodeName == 'hr':
                output += '<hr />'
            elif e.nodeName == 'subchapter':
                output += handleChapterInternals(e, level + 1)
            else:
                exit("Error: <" + e.nodeName + "> used in invalid location.")
                
    if chapter.nodeName == 'subchapter': output += '<br/> <br />'
    
    return output
    
def handleTable(table):
    output = '<table>'
    for row in getChildrenByTagName(table, 'row'):
        output += '<tr>'
        for column in getChildrenByTagName(row, 'column'):
            attributes = ''
            if column.getAttribute('align'):
                attributes += ' align="' + column.getAttribute('align') + '"'
            output += '<td valign="top"' + attributes + '>' + handlePs(column) + '</td>'
        output += '</tr>'
    output += '</table>'
    
    return output

def handleQuote(quote):
    output = ''
    
    attributes = ''
    if quote.getAttribute('type'):
        if quote.getAttribute('type') == 'inter':
            output += '<table width="100%"><tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td><div class="inter_quote">'
        else:
            exit("Error: Unknown <quote> type.")
    else:
        output += '<div class="quote">'
    output += handlePs(quote)
    
    # Quote Source If Exists 
    source = getChildrenByTagName(quote, 'source')
    if source:
        output += u'<p class="source">—' + handlePChildren(source[0].childNodes) + '</p>'
    
    if quote.getAttribute('type'):
        if quote.getAttribute('type') == 'inter':
            output += '</div></td><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table>'
    else:
        output += '</div>'
    
    return output

def handlePs(ps, attributes = '', prefix = ''):
    output = ""
    if attributes != '': attributes = ' ' + attributes
    for p in getChildrenByTagName(ps, 'p'):
        if p.getAttribute('align'):
            if p.getAttribute('align') == 'right' or p.getAttribute('align') == 'center':
                attributes += ' class="aligned" align="' + p.getAttribute('align') + '"'
            else:
                exit('Error: Unknown <p> align position.')
        if p.getAttribute('outdent'):
            if p.getAttribute('outdent') == 'true':
                attributes += ' class="outdent"'
        output += '<p' + attributes + '>'
        
        if prefix != '': output += prefix
        
        output += handlePChildren(p.childNodes)
            
        output += '</p>'
        attributes = ''
    return output

def handlePChildren(c):
    global footnotes
    global footnote_id
    output = ''
    for child in c:
        if child.nodeType == 3:
            output += child.nodeValue
        elif child.nodeType == 1:
            if child.nodeName == 'b' or child.nodeName == 'em' or child.nodeName == 'i' or child.nodeName == 'strong' or child.nodeName == 'sup' or child.nodeName == 'sub' or child.nodeName == 'u':
                output += '<' + child.nodeName + '>'
                try:
                    if child.childNodes:
                        output += handlePChildren(child.childNodes)
                    else:
                        output += child.firstChild.data
                except:
                    output += handlePChildren(child.childNodes)
                output += '</' + child.nodeName + '>'
            elif child.nodeName == 'br':
                output += '<br />'
            elif child.nodeName == 'sc':
                output += '<span class="smallcaps">'
                try:
                    if child.childNodes:
                        output += handlePChildren(child.childNodes)
                    else:
                        output += child.firstChild.data
                except:
                    output += handlePChildren(child.childNodes)
                output += '</span>'
            elif child.nodeName == 'footnote':
                footnote_id += 1
                
                try:
                    if child.childNodes:
                        footnotes[footnote_id] = handlePChildren(child.childNodes)
                    else:
                        footnotes[footnote_id] = child.firstChild.data
                except:
                    footnotes[footnote_id] = handlePChildren(child.childNodes)
                
                output += '<sup><a id="footnote_' + str(footnote_id) + '_backlink" href="#footnote_' + str(footnote_id) + '">[' + str(len(footnotes)) + ']</a></sup>'
            elif child.nodeName == 'img':
                try:
                    imgname = child.getAttribute('name')
                except:
                    error("Error: <img> missing name attribute.")
                output += '<img src="images/' + imgname + '" />'
            elif child.nodeName == 'code':
                output += '<tt>'
                
                try:
                    if child.childNodes:
                        output += handlePChildren(child.childNodes)
                    else:
                        output += child.firstChild.data
                except:
                    output += handlePChildren(child.childNodes)
                
                output += '</tt>'
            else:
                exit("Error: <" + child.nodeName + "> is not an allowed tag in <p>: " + child.toxml())
                
    return output

def returnFootnotes():
    global footnotes
    output = ''
    if footnotes:
        output += '<hr />'
        i = 1
        for k, v in footnotes.iteritems():
            output += '<p class="outdent"><a id="footnote_' + str(k) + '" href="#footnote_' + str(k) + '_backlink">' + str(i) + '</a> ' + v + '<br /><br /></p>'
            i = i + 1
        output += ''
    
        footnotes = {}
    
    return output
    
# Load Book

try:
    in_path = sys.argv[1]
except:
    exit("Error: You must provide an XMLB file as an argument.")

try:
    doc = xml.dom.minidom.parse(in_path)
except:
    exit("Error: Unable to parse XML.")

# HTML Header

head = [u"<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"\n  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n<head>\n <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n  <title>", "</title>\n<style type=\"text/css\" media=\"screen\">h1, h2, h3, p#subtitle, p.subtitle, p#author, p#publication_date, p#title, p.title, div#dedication { text-align: center; } p, p.title + p, p.subtitle + p, p#author, p#publication_date, p#title, p#subtitle { margin: 0; text-indent: 0; } p + p { text-indent: 1.5em; } p.subtitle + p, { text-indent: 0 } h1 + div.quote, p.title + div.quote, p.subtitle + div.quote { margin-top: 2em, margin-bottom: 2em } div.quote p.source, div.inter_quote p.source { text-align: right; } p#subtitle, p.subtitle { font-variant: small-caps; margin-bottom: 1em } .smallcaps { font-variant: small-caps; } img { display: block; margin-left: auto; margin-right: auto; } div#dedication, p#publication_date, p#author { margin-top: 2em; margin-bottom: 2em } br.page_break { page-break-after: always; } h1 { margin-top: 0px } sup { font-size: 0.75em; line-height: 0.5em } sub { font-size: 0.75em; line-height: .75em } p.aligned + p { text-indent: 0 } p.outdent { margin-left: 1.5em; text-indent: -1.5em !important } div.inter_quote { font-size: .8em; margin-top: 1em; margin-bottom: 1em; text-align: justify; } div.quote { margin-top: 1em; margin-bottom: 1em; text-align: justify; margin-left: 1.25em; margin-right: 1.25em } .book_glyph { margin-top: 30px; text-align: center; font-size: 6em; } </style>\n</head>\n<body>\n    "]

output = u""

# Get XMLB Element
try:
    xmlb = doc.getElementsByTagName("xmlb")[0]
except:
    exit("Error: File missing mandatory top level <xmlb> tag.")

# Ensure XMLB Version >= 0.2
try:
    if float(xmlb.getAttribute("version")) < 0.2:
        exit("Error: XMLB version must be 0.2 or greater")
except:
    exit("Error: XMLB version not provided.")

# Get Top Level Element
tle = getChildrenByTagName(xmlb, 'volume')
if tle:
    tle = tle[0]
    output += setBookInfo(tle, 'volume')
    
    chapters = getChildrenByTagName(tle, 'chapter')
    if chapters:
        for chapter in chapters:
            output += handleChapter(chapter)
    
    for book in getChildrenByTagName(tle, 'book'):
        # Book Num & Title
        if book.getAttribute('num'):
            output += '<h1 class="book_title">Book ' + book.getAttribute('num') + '</h1>'
            try:
                output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(book, 'title')[0].childNodes) + '</p>'
            except:
                exit("Error: Missing book <title> tag.")
        else:
            try:
                output += '<h1>' + handlePChildren(getChildrenByTagName(book, 'title')[0].childNodes) + '</h1>'
            except:
                exit("Error: Missing book <title> tag.")
        
        #Book Subtitle If Exists
        subtitle = getChildrenByTagName(book, 'subtitle')
        if subtitle:
            output += '<p class="subtitle">' + d(subtitle) + '</p>'
        
        output += handleBook(book)
else:
    tle = getChildrenByTagName(xmlb, 'book')
    if tle:
        tle = tle[0]
        output += setBookInfo(tle, 'book')
        output += handleBook(tle)
    else:
        exit("Error: File missing top level <volume> or <book> tag.")

# HTML Footer
output += "\n</body>\n</html>"

# print output

out_path = os.path.dirname(in_path) + "/" + string.split(os.path.basename(in_path), ".")[0] + ".html"
f = codecs.open(out_path, "w", "utf-8")
f.write(output)
f.close()

print "Done!"