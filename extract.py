import os

content = open('index.html', encoding='utf-8').read()
start_script = content.find('<script>')
end_script = content.rfind('</script>')
if start_script != -1 and end_script != -1:
    html = content[:start_script]
    js = content[start_script + 8:end_script]
    rest = content[end_script + 9:]
    
    new_html = html + '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>\n<script src="app.js"></script>\n' + rest
    open('index.html', 'w', encoding='utf-8').write(new_html)
    open('app.js', 'w', encoding='utf-8').write(js)
    print("Extracted app.js and updated index.html")
else:
    print("Could not find script block")
