import requests
import sys
import json
import argparse
import warnings
import sys
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Tool for parsing WayBack URLs.')

parser.add_argument('function', help="`pull` or `check`. `pull` will gather the urls from the WayBack API. `check` will ensure the response code is positive (200,301,302,307).")
parser.add_argument('--host', help='The host whose URLs should be retrieved.')
parser.add_argument('--with-subs', help='`yes` or `no`. Retrieve urls from subdomains of the host.', default=False)
parser.add_argument('--loadfile', help='Location of file from which urls should be checked.')

args = parser.parse_args()

def waybackurls(host, with_subs):
    if with_subs:
        url = 'http://web.archive.org/cdx/search/cdx?url=*.%s/*&output=list&fl=original&collapse=urlkey' % host
    else:
        url = 'http://web.archive.org/cdx/search/cdx?url=%s/*&output=list&fl=original&collapse=urlkey' % host
    r = requests.get(url)
    print r.text.strip()
    

def check(data):
    for url in data:
        url = url.strip("\r").strip().strip('"').strip("'")
        req = requests.head(url, verify=False)
        status_code = req.status_code
        if status_code == 404:
            continue
        if "Content-Length" in req.headers.keys():
            cLength = req.headers["Content-Length"]
        else:
            cLength = "Unknown"
        if  "Content-Type" in req.headers.keys():
            cType = req.headers["Content-Type"]
        else:
            cType = "Unknown"
        if str(status_code)[0] == "3":
            rUrl = req.headers["Location"]
            print ", ".join([url, str(status_code), cLength, cType, rUrl])
        else:
            print ", ".join([url, str(status_code), cLength, cType])

if args.function == "pull":
    if not args.host:
        print "[-] Please specify a host using the --host parameter!"
        exit()
    waybackurls(args.host, args.with_subs)
elif args.function == "check":
    if args.loadfile:
        try:
            check(open(args.loadfile).readlines())
        except IOError as e:
            print "[-] File not found!"
            exit()
    elif not sys.stdin.isatty():
        check(sys.stdin.readlines())
    else:
        print "[-] Please either specify a file using --loadfile or pipe some data in!"
        exit()