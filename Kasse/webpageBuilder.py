'''
Created on Sep 8, 2018

@author: sedlmeier
'''

def html(head, body):
    return '''<!DOCTYPE html>%s%s</html>'''%(head,body)
    
def head(titletxt,style,script):
    return '''<head><meta charset="UTF-8"><meta name="referrer" content="no-referrer" /><title>%s</title>%s%s</head>'''%(titletxt,style,script)

def script(scripttxt):
    return '''<script>%s</script>'''%(scripttxt)

def style(styletxt):
    return '''<style>%s</style>'''%(styletxt)
        
def body(header, content):
    return '''<body><section id=sectionbodyheader>%s</section><section id=sectionbodycontent>%s</section></body>'''%(header,content)

def header(headertext):
    return '''<h4>%s</h4>'''%(headertext)

def table(tablehead,tablecontent):
    return '''<table>%s%s</table>'''%(tablehead,tablecontent)

def tablehead():
    return '''<th>%s</th>'''

def tablerow():
    return '''<tr>%s</tr>'''





    
    