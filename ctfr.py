#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
	CTFR - 04.03.18.02.10.00 - Sheila A. Berta (UnaPibaGeek)
------------------------------------------------------------------------------
"""

## # LIBRARIES # ##
import re
import requests

from lxml import etree

## # CONTEXT VARIABLES # ##
version = 1.2


## # MAIN FUNCTIONS # ##

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help="Target domain. eg: google.com")
    parser.add_argument('-o', '--output', type=str, required=True, help="Output file.")
    parser.add_argument('-x', '--xpath', action='store_true', help="Get result for xpath.")
    return parser.parse_args()


def banner():
    global version
    b = '''
          ____ _____ _____ ____  
         / ___|_   _|  ___|  _ \ 
        | |     | | | |_  | |_) |
        | |___  | | |  _| |  _ < 
         \____| |_| |_|   |_| \_\\
	
     Version {v} - Hey don't miss AXFR!
    Made by Sheila A. Berta (UnaPibaGeek)
	'''.format(v=version)
    print(b)


def clear_url(target):
    return re.sub('.*www\.', '', target, 1).split('/')[0].strip()


def save_subdomains(subdomains, output_file):
    with open(output_file, "a") as f:
        f.write('\n'.join(subdomains))
        f.close()


def get_result_for_json(target):
    req = requests.get("https://crt.sh/?q=%.{d}&output=json".format(d=target))

    if req.status_code != 200:
        print("[X] Information not available!")
        exit(1)

    results = []
    domain_pattern = r'^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$'
    for (key, value) in enumerate(req.json()):
        for sub in value['name_value'].split('\n'):
            sub = re.sub(r'(\*.)', '', sub)
            if re.match(domain_pattern, sub) == None:
                continue
            if sub in results:
                continue
            results.append(sub)

    return results


def get_result_for_html(target):
    req = requests.get("https://crt.sh/?q=%.{d}".format(d=target))

    if req.status_code != 200:
        print("[X] Information not available!")
        exit(1)

    results = []
    td_result = etree.HTML(req.content).xpath('//td/text()')
    domain_pattern = r'^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$'

    for sub in td_result:
        if target not in sub:
            continue
        sub = re.sub(r'(\*.)', '', sub)
        if re.match(domain_pattern, sub) == None:
            continue
        if sub in results:
            continue
        results.append(sub)

    return results

def main():
    banner()
    args = parse_args()

    target = clear_url(args.domain)
    output = args.output

    if args.xpath:
        results = get_result_for_html(target)
    else:
        results = get_result_for_json(target)

    print("\n[!] ---- TARGET: {d} ---- [!] \n".format(d=target))

    subdomains = sorted(set(results))

    if output is not None:
        save_subdomains(subdomains, output)

    for subdomain in subdomains:
        print("[+]  {s}".format(s=subdomain))

    print("\n\n[!]  Done. Have a nice day! ;).")


if __name__ == '__main__':
    main()
