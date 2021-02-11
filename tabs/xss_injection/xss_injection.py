import requests
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import os
threads = 40
base_path=os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(os.path.dirname(base_path),"crawler",'links.txt')
output_file = os.path.join(base_path,'found.txt')
payload_file = os.path.join(base_path,'payload.txt')
payloads = open(payload_file, mode='r', encoding='utf-8').read().split('\n')
timeout = 30


def changeNCheck(link):
    if link == "":
        return
    normal_link = True
    if '=' in link:
        normal_link = False
    link_old = link
    for payload in payloads:
        # GET REQUEST
        if not normal_link:
            link_temp = link.split('=')[0]
            link = link_temp + '=' + payload
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
            }
            resp = requests.get(link, headers=headers, timeout=timeout).text
            if payload in resp:
                with open(output_file, mode='a+', encoding='utf-8') as f:
                    f.write(link + "\n")
                print("Valid: {}".format(link))
            else:
                print("Invalid: {}".format(link))
        except:
            print("Can't open {}".format(link))
        # POST REQUEST
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
            }
            resp = requests.get(link_old, headers=headers,
                                timeout=timeout).content
            soup = bs(resp, 'html.parser')
            forms = soup.findAll('form')
            if len(forms) == 0:
                print("No forms found in {}".format(link_old))
            if soup.find('input') is not None or soup.find('textarea') is not None:
                print("Form exists in {}!".format(link_old))
                with open(os.path.join(base_path,"forms.txt"), mode='a+', encoding='utf-8') as f:
                    f.write(link_old + "\n")
            for form in forms:
                action_link = form.get('action')
                method = form.get('method')
                print("Request Method: {}".format(method))
                domain = link.split('://')[0] + "://" + \
                    link.split('://')[1].split('/')[0]
                if action_link.startswith('//'):
                    action_link = "https:" + action_link
                if not domain.endswith('/'):
                    domain = domain + "/"
                if action_link.startswith('/'):
                    action_link = "".join(action_link[1::])
                if not action_link.startswith('http'):
                    action_link = domain + action_link
                print("EndPoint: {}".format(action_link))
                params_list = form.findAll('input')
                textarea_list = form.findAll('textarea')
                params_name = []
                params_name.extend(
                    [x.get('name') for x in params_list if x.get('name') is not None])
                params_name.extend(
                    [x.get('name') for x in textarea_list if x.get('name') is not None])
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
                }
                data = {}
                for param in params_name:
                    data[param] = payload
                print("Submitting: {}".format(data))
                if method.lower() == 'get':
                    try:
                        resp = requests.get(
                            action_link, headers=headers, params=data).text
                        if payload in resp:
                            with open(output_file, mode='a+', encoding='utf-8') as f:
                                f.write(link + "\n")
                            print("Valid: {}".format(link))
                        else:
                            print("Invalid: {}".format(link))
                    except:
                        print("Cannot make GET request to {} with params {}".format(
                            action_link, data))
                else:
                    try:
                        resp = requests.post(
                            action_link, headers=headers, data=data).text
                        if payload in resp:
                            with open(output_file, mode='a+', encoding='utf-8') as f:
                                f.write(link + "\n")
                            print("Valid: {}".format(link))
                        else:
                            print("Invalid: {}".format(link))
                    except:
                        print("Cannot make POST request to {} with payload {}".format(
                            action_link, data))
        except:
            print("Can't open {}".format(link_old))


def stored_xss_checker():
    links = open(input_file, mode='r', encoding='utf-8').read().split('\n')
    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(changeNCheck, links)

if __name__=="__main__":
    stored_xss_checker()

