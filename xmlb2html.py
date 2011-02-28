#!/usr/bin/env python3.1.4
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
head = [u"<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"\n  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n<head>\n <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n  <title>", "</title>\n<style type=\"text/css\" media=\"screen\">h1, h2, h3, p#subtitle, p.subtitle, p#author, p#publication_date, p#title, p.title, div#dedication { text-align: center; } p, p.title + p, p.subtitle + p, p#author, p#publication_date, p#title, p#subtitle { margin: 0; text-indent: 0; } p + p { text-indent: 1.5em; } p.subtitle + p, { text-indent: 0 } h1 + div.quote, p.title + div.quote, p.subtitle + div.quote { margin-top: 2em, margin-bottom: 2em } div.quote p.source, div.inter_quote p.source { text-align: right; } p#subtitle, p.subtitle { font-variant: small-caps; margin-bottom: 1em } .smallcaps { font-variant: small-caps; } img { display: block; margin-left: auto; margin-right: auto; } div#dedication, p#publication_date, p#author { margin-top: 2em; margin-bottom: 2em } br.page_break { page-break-after: always; } h1 { margin-top: 0px } sup { font-size: 0.75em; line-height: 0.5em } sub { font-size: 0.75em; line-height: .75em } p.aligned + p { text-indent: 0 } p.outdent { margin-left: 1.5em; text-indent: -1.5em !important } div.inter_quote { font-size: .8em; margin-top: 1em; margin-bottom: 1em; text-align: justify; } div.quote { margin-top: 1em; margin-bottom: 1em; text-align: justify; margin-left: 1.25em; margin-right: 1.25em } .book_glyph { margin-top: 30px; text-align: center; font-size: 6em; } </style>\n</head>\n<body>\n    "]


# FUNCTIONS

# Get all children of a node by tag name
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

# Process title, author, dedication, quote(s)
def setBookInfo(topLevelElement, topLevelElementName):
    output = u''
    
    # Title
    try:
        title = getChildrenByTagName(topLevelElement, 'title')
        output += head[0] + d(title) + head[1]
        output += '<h1 id="title">' + handlePChildren(title[0].childNodes) + '</h1>'
    except:
        exit("Error: Missing " + topLevelElementName + " <title> tag")
    
    # Subtitle if it exists
    subtitle = getChildrenByTagName(topLevelElement, 'subtitle')
    if d(subtitle):
        output += '<p id="subtitle">' + handlePChildren(subtitle[0].childNodes) + "</p>" # TODO: Make this work with enclosed italics, etc.
    
    # Author
    try:
        output += '<p id="author"><i>by</i> ' + handlePChildren(getChildrenByTagName(topLevelElement, 'author')[0].childNodes) + '</p>'
    except:
        exit("Error: Missing " + topLevelElementName + " <author> tag")
    
    # Publication Date
    try:
        publication_date = d(getChildrenByTagName(topLevelElement, 'publication_date'))
        output += '<p id="publication_date">published ' + time.strftime("%d %B %Y", time.strptime(publication_date, "%Y-%m-%d")) + '</p>'
    except:
        exit("Error: Missing or invalid " + topLevelElementName + " <publication_date> tag")
    
    # Dedication if it exists
    dedication = getChildrenByTagName(topLevelElement, 'dedication')
    if dedication:
        output += '<div id="dedication">' + handlePChildren(dedication[0].childNodes) + '</div><br class="page_break" />'
    
    # Quotes if they exist
    if topLevelElementName == 'volume':
        if getChildrenByTagName(topLevelElement, 'quote'):
            output += '<br class="page_break" />'
            for quote in getChildrenByTagName(topLevelElement, 'quote'):
                output += handleQuote(quote)
            output += '<br class="page_break" />'
    
    return output

# Process book contents
def handleBook(book):
    output = ''
    
    # Quotes if they exist
    if getChildrenByTagName(book, 'quote'):
        for quote in getChildrenByTagName(book, 'quote'):
            output += handleQuote(quote)
    else:
        output += u'<p align="center" style="font-size: 40px; text-indent: 0px;">✠</p>'
    
    # If book is made up of parts
    parts = getChildrenByTagName(book, 'part')
    if parts:
        # Process pre-part chapters
        chapters = getChildrenByTagName(book, 'chapter')
        if chapters:
            for chapter in chapters:
                output += handleChapter(chapter)
        
        # Process parts
        for part in parts:
            output += handlePart(part)
            
    # If book is just chapters, no parts
    else:
        # Process chapters
        for chapter in getChildrenByTagName(book, 'chapter'):
            output += handleChapter(chapter)
        
    return output

# Process part contents
def handlePart(part):
    output = ''
    
    # Number
    if part.getAttribute('num'):
        output += '<h1 class="part_title">Part ' + part.getAttribute('num') + '</h1>'
    else:
        exit("Error: Missing num attribute in <part> tag")
    
    # Title if it exists
    if getChildrenByTagName(part, 'title'):
        output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(part, 'title')[0].childNodes) + '</p>'
    
    # Subtitle if it exists
    if getChildrenByTagName(part, 'subtitle'):
        output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(part, 'subtitle')[0].childNodes) + '</p>'
    
    # Quotes if they exist
    if getChildrenByTagName(part, 'quote'):
        for quote in getChildrenByTagName(part, 'quote'):
            output += handleQuote(quote)
    else:
        output += u'<p align="center" style="font-size: 40px; text-indent: 0px;">✠</p>'
    
    # Chapters
    for chapter in getChildrenByTagName(part, 'chapter'):
        output += handleChapter(chapter)
    
    return output

# Process chapter
def handleChapter(chapter):
    output = ''
    
    # Number, title and subtitle
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
    
    # Add forced page break if chapter has no heading
    if heading == '':
        heading = '<br class="page_break" />'
    
    # Process chapter content
    output += heading
    output += handleChapterInternals(chapter)
    output += returnFootnotes()
    
    return output

# Process chapter content
def handleChapterInternals(chapter, level = 1):
    output = ''
    
    for e in chapter.childNodes:
        if e.nodeType == 3:
            output += e.data
        elif e.nodeType == 1:
            if e.nodeName == 'subtitle':
                if level > 1:
                    exit("Error: Invalid location for a subtitle")
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
                exit("Error: <" + e.nodeName + "> used in invalid location")
                
    if chapter.nodeName == 'subchapter': output += '<br/> <br />'
    
    return output

# Process table
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

# Process quote
def handleQuote(quote):
    output = ''
    
    attributes = ''
    if quote.getAttribute('type'):
        if quote.getAttribute('type') == 'inter':
            output += '<table width="100%"><tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td><div class="inter_quote">'
        else:
            exit("Error: Unknown <quote> type")
    else:
        output += '<div class="quote">'
    output += handlePs(quote)
    
    # Quote source if it exists
    source = getChildrenByTagName(quote, 'source')
    if source:
        output += u'<p class="source">—' + handlePChildren(source[0].childNodes) + '</p>'
    
    if quote.getAttribute('type'):
        if quote.getAttribute('type') == 'inter':
            output += '</div></td><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table>'
    else:
        output += '</div>'
    
    return output

# Process paragraphs
def handlePs(ps, attributes = '', prefix = ''):
    output = ""
    if attributes != '': attributes = ' ' + attributes
    for p in getChildrenByTagName(ps, 'p'):
        if p.getAttribute('align'):
            if p.getAttribute('align') == 'right' or p.getAttribute('align') == 'center':
                attributes += ' class="aligned" align="' + p.getAttribute('align') + '"'
            else:
                exit('Error: Unknown <p> align position')
        if p.getAttribute('outdent'):
            if p.getAttribute('outdent') == 'true':
                attributes += ' class="outdent"'
        output += '<p' + attributes + '>'
        
        if prefix != '': output += prefix
        
        output += handlePChildren(p.childNodes)
            
        output += '</p>'
        attributes = ''
    return output

# Process the children of paragraphs
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
                    error("Error: <img> missing name attribute")
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

# Process and return footnotes
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

# Main
def main():
    # Load XMLB file
    try:
        in_path = sys.argv[1]
    except:
        exit("Error: You must provide an XMLB file as an argument")

    # Parse XML
    try:
        doc = xml.dom.minidom.parse(in_path)
    except:
        exit("Error: Unable to parse XML")

    # Initialize output
    output = u""

    # Get XMLB element
    try:
        xmlb = doc.getElementsByTagName("xmlb")[0]
    except:
        exit("Error: File missing mandatory top level <xmlb> tag")

    # Ensure XMLB version >= 0.2
    try:
        if float(xmlb.getAttribute("version")) < 0.2:
            exit("Error: XMLB version must be 0.2 or greater")
    except:
        exit("Error: XMLB version not provided")

    # If XMLB file is volume with multiple books
    topLevelElement = getChildrenByTagName(xmlb, 'volume')
    if topLevelElement:
        topLevelElement = topLevelElement[0]

        # Process title, author, dedication, volume-level quote(s)
        output += setBookInfo(topLevelElement, 'volume')

        # Process volume-level chapters, if they exist
        chapters = getChildrenByTagName(topLevelElement, 'chapter')
        if chapters:
            for chapter in chapters:
                output += handleChapter(chapter)

        # Process books
        for book in getChildrenByTagName(topLevelElement, 'book'):
            # Book num and title
            if book.getAttribute('num'):
                output += '<h1 class="book_title">Book ' + book.getAttribute('num') + '</h1>'
                try:
                    output += '<p class="subtitle">' + handlePChildren(getChildrenByTagName(book, 'title')[0].childNodes) + '</p>'
                except:
                    exit("Error: Missing book <title> tag")

            # Book title on its own
            else:
                try:
                    output += '<h1>' + handlePChildren(getChildrenByTagName(book, 'title')[0].childNodes) + '</h1>'
                except:
                    exit("Error: Missing book <title> tag")

            # Book subtitle if it exists
            subtitle = getChildrenByTagName(book, 'subtitle')
            if subtitle:
                output += '<p class="subtitle">' + d(subtitle) + '</p>'

            # Process book contents
            output += handleBook(book)

    # If XMLB file is single book
    else:
        topLevelElement = getChildrenByTagName(xmlb, 'book')
        if topLevelElement:
            topLevelElement = topLevelElement[0]

            # Process title, author, dedication, book-level quote(s)
            output += setBookInfo(topLevelElement, 'book')

            # Process book contents
            output += handleBook(topLevelElement)
        else:
            exit("Error: Missing top level <volume> or <book> tag")

    # HTML footer
    output += "\n</body>\n</html>"

    # Write output to HTML file in same directory as XMLB file
    out_path = os.path.dirname(in_path) + "/" + string.split(os.path.basename(in_path), ".")[0] + ".html"
    f = codecs.open(out_path, "w", "utf-8")
    f.write(output)
    f.close()

    print "Done!"

if __name__ == '__main__':
    main()