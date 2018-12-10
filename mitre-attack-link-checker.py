
#!/usr/bin/env python3.6

__AUTHOR__ = 'Michael Hidalgo'
__VERSION__ = "1.0.0 December 2018"

"""
Install dependencies with:
pip install requests
"""

import json
import requests


def read_attack_enterprise_matrix():
    try:
        r = requests.get('https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json')
        return json.loads(r.content)
    except IOError:
        print('Failed to open URL') 
        
def write_broken_links_to_file(data):
    with open('broken_links.json', 'w') as broken_links:
        broken_links.write(json.dumps(data))

def get_unique_links():
    data_source  = read_attack_enterprise_matrix()['objects']
    unique_links = {}
    for item in data_source:
        if 'external_references' in item:
            for link in item.get('external_references'):
                url         = link.get('url')  # fetch url
                description = link.get('description')
                source_name = link.get('source_name') 

                if url != None:
                    if url in unique_links :
                        unique_links[url]['referenced_by'].append(item.get('id'))
                    else :
                        link_info                     = {}
                        link_info['referenced_by']    = []
                        link_info['referenced_by'].append(item.get('id'))
                        unique_links[url]             = link_info
                        if (description != None and source_name != None):
                            unique_links[url]['description'] = description
                            unique_links[url]['source_name'] = source_name
                        
    return unique_links

def find_broken_links():
   all_links = get_unique_links()
   for item in list(all_links):
       if not is_link_broken(item):
        del all_links[item]                 # leaves just those links that are broken
   write_broken_links_to_file(all_links)    # saving results

def get_status_code(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req         = requests.head(url, headers = headers, allow_redirects = True )
        status_code = req.status_code
        
        if (status_code == 405 or status_code == 409):  # some sites do not allow get
            req         = requests.get(url, headers = headers, allow_redirects = True )
            status_code = req.status_code
        return status_code 
    except:
        return None

def is_link_broken(url):
    return get_status_code(url) != 200

def main():
    print(">>> Finding broken links <<<")
    find_broken_links()
    print(">> Done <<")

if __name__ == '__main__':  
    main()
