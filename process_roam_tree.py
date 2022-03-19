import re
import markdown
import zipfile
import shutil
import sys
from os import listdir
from datetime import date

def unzip_roam(filename):
    with zipfile.ZipFile(f"{filename}.zip", 'r') as zip_ref:
        zip_ref.extractall("./Roam-Export")

def read_exported_file(ref_name):
    f = open(f'./Roam-Export/{ref_name}.md', 'r')
    text = f.read() 
    f.close()
    return text

def store_updated_file(ref_name, html):
    f = open(f"./docs/{ref_name}.html", "w")
    f.write(html)
    f.close()

def get_refs_on_text(text):
    refs = re.findall('\[\[(.*?)\]\]', text)
    return refs

def rewrite_text_with_links(text,  refs):
    for ref_name in refs:
        # text = text.replace(f"[[{ref_name}]]", f"[{ref_name}](<{ref_name}.md>)")
        link = ref_name.replace('?', '%3F')
        text = text.replace(f"[[{ref_name}]]", f"[{ref_name}](<{link}.html>)")
    return text

def replace_regular_links(text):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,text)  
    urls = [x[0] for x in url]
    for url in urls:
        text = text.replace(url, f'[{url}]({url})')
    return text

def replace_hashtags(text):
    hashtags  = re.findall('#\[\[(.*?)\]\]', text)
    for hashtag in hashtags:
        text = text.replace(f"#[[{hashtag}]]", f"\#{hashtag}")
    return text
    
def fix_padding(text):
    text = text.replace("\n-", "\n\n-")
    text = text.replace("\n    - ", "\n\n")
    text = text.replace("    -", ">")
    text = text.replace("\n    ", "\n\n")
    return text

def process_ref(ref_name):
    text = read_exported_file(ref_name)
    text = fix_padding(text)
    text = replace_regular_links(text)
    text = replace_hashtags(text)
    refs = get_refs_on_text(text)
    text = rewrite_text_with_links(text, refs)
    final_html = text_to_html(text, ref_name)
    store_updated_file(ref_name, final_html)
    return set(refs)

def create_index():
    files = {name.replace(".html", "") for name in listdir("./docs")}
    ignore_files = set(["TODO", "index", ".DS_Store"])
    files = files - ignore_files
    today = date.today()
    dia = today.strftime("%d/%m/%Y")
    html = f"<h1> Sobre: </h1><p>Esse site contém todas anotações da pesquisa genealógica feita por mim (Lyssa Scherer) e é constantemente modificada. Abaixo você pode encontrar o nome de todas as pessoas que estão presentes na minha árvore, alem de algumas páginas contendo documentos e observações. Caso tenha algo para contrbiuir, entre em contato pelo email <b>lyssa.scherer@gmail.com</b>!</p><p><b>Última modificação: {dia}</b></p>"
    html += "<h1>Lista de páginas disponíveis:</h1>"
    for name in files:
        link = name.replace(" ","%20").replace("?","%3F")
        html += f'<p><a href="{link}.html">{name}</a></p>'
    full_html = create_full_html(html, "Inicio")
    store_updated_file("index", full_html)

def create_full_html(html_body, title):
    style = """<style>
        p {
        padding: 0 5em;
        }
        .navbar {
                list-style: none;
                font-weight: bold;
        }


        </style>"""
    final_html = f'''<!DOCTYPE html>
    <html>

    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="tufte.css"/>
    {style}
    </head>


    <body>
    <ul class="navbar">
        <li><a href="index.html">Início</a></li>
    </ul>
    <h1>{title}</h1>
    {html_body}
    </body>

    </html>'''
    return final_html

def text_to_html(text, title):
    html = markdown.markdown(text, output_format='html4')
    if not len(html):
        html = '<a href="javascript:history.back()">Essa pagina ainda não foi criada. Volte para a página anterior!</a>'
    final_html = create_full_html(html, title)
    return final_html

def process_tree(starter_name, roam_filename):
    unzip_roam(roam_filename)
    inline_refs = set()
    imported_refs = set()

    ref_name = starter_name
    used_refs = process_ref(ref_name)
    imported_refs.add(ref_name)
    inline_refs.update(used_refs)

    while len(inline_refs):
        ref_name = inline_refs.pop()
        used_refs = process_ref(ref_name)
        imported_refs.add(ref_name)
        inline_refs.update(used_refs)
        inline_refs = inline_refs-imported_refs
    shutil.rmtree("./Roam-Export")
    create_index()

def example():
    roam_filename = "Roam-Export-1647102847501"
    starter_name = "Lyssa Priscyla Scherer"
    process_tree(starter_name, roam_filename)

if __name__ == "__main__":
    roam_filename = sys.argv[1]#"Roam-Export-1647102847501"
    starter_name = "Lyssa Priscyla Scherer"
    process_tree(starter_name, roam_filename)