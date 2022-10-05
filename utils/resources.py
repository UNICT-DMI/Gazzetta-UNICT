import re
import os
from typing import Dict, List
import requests
from PyPDF2 import PdfReader
import yaml

reg = [
    
]

#data is a composite dictionary
#["sitename"] -> [list of announcements]
#each announcment is a dictionary with keys: object, date, odg, odgagg, pdf report link, verbale 
def read_all_sent_announcements(filename: str):
    if not os.path.exists(filename):
        with open(filename, 'w'): pass
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def write_all_sent_announcements(filename: str, sent_announcements):
    with open(filename, "w") as f_announcements:
        yaml.dump(sent_announcements, f_announcements)
        #print(sent_announcements)

def save_attachments(pdf_links: List[str]) -> List[str]:
    local_files = []
    for pdf_link in pdf_links:
        response = requests.get(pdf_link, timeout=None)
        with open('tmp/' + pdf_link.split("/")[-1], 'wb') as f:
            f.write(response.content)
        local_files.append('tmp/' + pdf_link.split("/")[-1])
    return local_files

def match_regex_tag(text: str) -> List[str]:
    tags_found = []
    for tag in reg:
        if re.search(tag['exp'], text, re.IGNORECASE):
            tags_found.append('*' + tag['tag'] + '*')
    return tags_found

def get_pdf_text(pdf_files: List[str]) -> str:
    text = ""
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)        
            number_of_pages = len(reader.pages)
            for i in range (number_of_pages):
                page = reader.pages[i]
                text += page.extract_text() + " "
        except Exception as e:
            print(e)
    return text

def already_sent(announcement, sent_announcements: List[str]) -> Dict:
    if announcement['object'] not in [ x['object'] for x in sent_announcements ]:
        return { 
            'announcement': True,
            'odgagg':        announcement['odgagg'],
            'pdf_report':    announcement['pdf_report'],
            'verbale':       announcement['verbale']
        }
    else :
        matched_announcement = next(item for item in sent_announcements if item['object'] == announcement['object'])
        return {
            'announcement': False ,
            'odgagg':      ( announcement['odgagg']     ^ matched_announcement['odgagg'] ),
            'pdf_report':  ( announcement['pdf_report'] ^ matched_announcement['pdf_report'] ),
            'verbale':     ( announcement['verbale']    ^ matched_announcement['verbale'] )
        }
