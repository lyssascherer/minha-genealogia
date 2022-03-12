import re
import markdown
import zipfile
import shutil
import sys

def unzip_roam(filename):
    with zipfile.ZipFile(f"{filename}.zip", 'r') as zip_ref:
        zip_ref.extractall("./Roam-Export")

def read_exported_file(ref_name):
    f = open(f'./Roam-Export/{ref_name}.md', 'r')
    text = f.read() 
    f.close()
    return text

def store_updated_file(ref_name, html):
    f = open(f"./data/{ref_name}.html", "w")
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

def text_to_html(text, title):
    html = markdown.markdown(text, output_format='html4')
    if not len(html):
        html = '<a href="javascript:history.back()">Essa pagina ainda não foi criada. Volte para a página anterior!</a>'
    
    style = """<style>
        p {
        padding: 0 5em;
        }

        </style>"""
    final_html = f'''<!DOCTYPE html>
    <html>

    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {style}
    </head>

    <body>
    <h1>{title}</h1>
    {html}
    </body>

    </html>'''
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

def example():
    roam_filename = "Roam-Export-1647102847501"
    starter_name = "Lyssa Priscyla Scherer"
    process_tree(starter_name, roam_filename)

if __name__ == "__main__":
    roam_filename = sys.argv[1]#"Roam-Export-1647102847501"
    starter_name = "Lyssa Priscyla Scherer"
    process_tree(starter_name, roam_filename)