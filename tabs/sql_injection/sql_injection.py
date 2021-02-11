import requests
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import time
import os
threads = 40
base_path=os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(os.path.dirname(base_path),"crawler",'links.txt')
output_file = os.path.join(base_path,'found.txt')
time_based_payload = os.path.join(base_path,'time_payload.txt')
blind_based_payload = os.path.join(base_path,'blind_payload.txt')
time_payloads_list = open(time_based_payload, mode='r',
                          encoding='utf-8').read().split('\n')
blind_payloads_list = open(blind_based_payload, mode='r',
                           encoding='utf-8').read().split('\n')

timeout = 30


def changeNCheck(link):
    # time based check
    link_without_param = link.split('=')
    if len(link_without_param) == 1:
        print("{} ignored for not having injectable params")
        return
    for payload in time_payloads_list:
        if payload == "":
            continue
        target_page = "{}={}".format(link_without_param[0], payload)
        print("Testing {} for time based".format(target_page))
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
        }
        time1 = time.time()
        resp = requests.get(target_page, headers=headers, timeout=timeout).text
        time2 = time.time()
        timet = time2 - time1
        timet = str(timet)
        timet = timet.split(".")
        timet = timet[0]
        if int(timet) >= 2:
            print("Bug(time based) exists for {} with payload {}".format(
                target_page, payload))
            with open(os.path.join(base_path,'time_based_found.txt'), mode='a+', encoding='utf-8') as f:
                f.write(target_page + "\n")
        else:
            print("[!] SQL time based failed.")
    # blind check
    target_page = "{}='".format(link_without_param[0])
    print("Testing {} for blind based".format(target_page))
    resp = requests.get(target_page, headers=headers, timeout=timeout).text
    for payload in blind_payloads_list:
        if payload == "":
            continue
        if payload in resp:
            print("Bug(blind) exists for {} with payload {}".format(
                target_page, payload))
            with open(os.path.join(base_path,'blind_based_found.txt'), mode='a+', encoding='utf-8') as f:
                f.write(target_page + "\n")
            break

def sqli_scanner():
    links = open(input_file, mode='r', encoding='utf-8').read().split('\n')
    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(changeNCheck, links)

if __name__=="__main__":
    sqli_scanner()

