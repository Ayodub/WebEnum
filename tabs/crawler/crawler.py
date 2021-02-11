import requests
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import os
import sys

base_path=os.path.dirname(os.path.abspath(__file__))
processed_urls = []
output_file = os.path.join(base_path,"links.txt")  # the file that will contain output data
max_depth = 5  # maximum depth of links to access
threads = 40  # number of concurrent input urls to process


def recordLink(link):
    try:
        old_ones = open(output_file, mode='r',
                        encoding='utf-8').read().split('\n')
    except Exception as e:
        print(e)
    if link not in old_ones:
        with open(output_file, mode='a+', encoding='utf-8') as f:
            f.write(link + "\n")


def getSubPages(html_data, domain):
    soup = bs(html_data, 'html.parser')
    all_urls = [tag['href'] for tag in soup.findAll('a', href=True)]
    same_domains = []
    for an_url in all_urls:
        if an_url.startswith('#'):
            continue
        if an_url.endswith('.txt') or an_url.endswith('.xml') or an_url.endswith('#'):
            continue
        if an_url.startswith('//'):
            an_url = "http:" + an_url
        if an_url.startswith("/"):
            an_url = "http://{}{}".format(domain, an_url)
        if an_url.startswith("http://{}".format(domain)) or an_url.startswith("https://{}".format(domain)):
            if an_url.endswith("{}".format(domain)) or an_url.endswith("{}/".format(domain)):
                continue
            if an_url not in processed_urls and an_url not in same_domains:
                same_domains.append(an_url)
        elif an_url.startswith("http://www.{}".format(domain)) or an_url.startswith("https://www.{}".format(domain)):
            if an_url.endswith("{}".format(domain)) or an_url.endswith("{}/".format(domain)):
                continue
            if an_url not in processed_urls and an_url not in same_domains:
                same_domains.append(an_url)
    same_domains = list(set(same_domains))
    for d in same_domains:
        print(d)
    return same_domains


def accessPage(data):
    link, domain, depth = data
    print("Accessing {}".format(link))
    recordLink(link)
    if depth == 0:
        return

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = requests.get(link, headers=headers).text
    except:
        print("Cannot open {}".format(link))
        return
    subpages = getSubPages(resp, domain)
    for subpage in subpages:
        accessPage((subpage, domain, depth-1))
        exit(0)


if __name__=="__main__":
    with open(output_file,'w+') as f:f.close()
    links = open(os.path.join(base_path,"list.txt"), mode='r', encoding='utf-8').read().split("\n")
    # links = open(sys.argv[1], mode='r', encoding='utf-8').read().split("\n")
    link_data = []
    for link in links:
        if link == "":
            continue
        if not link.startswith('http'):
            link = "http://{}".format(link)
        domain = link.split('://')[1].split('/')[0]
        link_data.append((link, domain, max_depth))
    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(accessPage, link_data)




