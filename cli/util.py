import time
import os
from select import select
import pyqrcode
import subprocess
import re

SUPPORTED_FORMATS = ['mkv','mp4']

def wait_until_error(f, timeout=0.5):
    """ Wait for timeout seconds until the function stops throwing any errors. """

    def inner(*args, **kwargs):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout or timeout < 0):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if(e or not e):
                    continue
    return inner


def send_until_writable(timeout=0.5):
    """ This will send a message to the socket only when it is writable and wait for timeout seconds
    for the socket to become writable, if the socket was busy. """

    def inner(f, socket, message):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout):
            if(check_writable(socket)):
                return f(message)
    return inner


def check_writable(socket):
    """ Checks whether the socket is writable """

    _, writable, _ = select([], [socket], [], 60)
    return writable == [socket]


def print_url(url):
    """ Makes a txt file with the URL that is received from the server for the GUI app. """

    print(f"Please visit {url}")
    f = open("invite_link.txt", 'w')
    f.write(url)
    f.close()


def print_qr(url):
    """ Prints a QR code using the URL that we received from the server. """

    image = pyqrcode.create(url)
    image.svg('invite_link.svg', scale=1)
    print(image.terminal(quiet_zone=1))


def get_videos(path):
    if(os.path.isfile(path)):
        if (path[-3:] in SUPPORTED_FORMATS):
            return [path]
        return []
    if(os.path.isdir(path)):
        ans = []
        for file in os.listdir(path):
            ans.extend(get_videos(path+'/'+file))
        return ans

def path2title(path):
    return path.split('/')[-1:][0].split('.')[0]

def get_interface():
    arp_details = subprocess.Popen('arp -a'.split(),stdout=subprocess.PIPE).communicate()
    arp_details = arp_details[0].decode().split('\n')[:-1]

    intf = None
    for detail in arp_details:
        match = re.search('on (.*)$',detail)
        if(match is not None):
            new_intf = match.groups()[0]
            if(intf is not None and intf != new_intf):
                return input("[+] Enter the interface to use: ")
            intf = new_intf
    if (intf is None):
        return input("[+] Enter the interface to use: ")
    
    return intf