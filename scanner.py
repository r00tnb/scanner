# -*- coding: utf-8 -*-
import requests,argparse
import threading

def print_info(s):
    global lock
    with lock:
        print('[.]'+s)
def print_warning(s):
    global lock
    with lock:
        print('[-]'+s)
def print_error(s):
    global lock
    with lock:
        print('[!]'+s)
def print_yes(s):
    global lock
    with lock:
        print('[+]'+s)
def print_normal(s):
    global lock
    with lock:
        print(s)

def scan(x):
    global url,codeList,method,session,timeout,outfile,attempts
    ret = True
    req = requests.Request(method,url+x)
    r = session.prepare_request(req)
    try:
        r = session.send(r,timeout=timeout)
        if(str(r.status_code) in codeList):
            print_yes('Find "%s" Response %d'%(url+x,r.status_code))
            if(outfile):
                outfile.write('Find "%s" Response %d\n'%(url+x,r.status_code))
        elif(r.status_code != 404):
            ret = False
            print_warning('Maybe "%s" Response %d.'%(url+x,r.status_code))
        attempts += 1
    except requests.exceptions.Timeout:
        ret = False
        attempts += 1
        print_error('The url "%s" timeout!'%(url+x))
    
    return ret

def work():
    global lock,fieldList,indexOffield
    ret = []
    index = 0
    length = len(fieldList)
    while(True):
        with lock:
            index = indexOffield
            indexOffield += 1
        if(index < length):
            if(scan(fieldList[index])):
                ret.append(fieldList[index])
        else:
            break
    return ret

def main():
    '''参数解析和主要逻辑'''
    global url,fileList,threadsNum,codeList,method,session,timeout,outfile,attempts
    parser = argparse.ArgumentParser()
    parser.add_argument("url",help="scanning the url.")
    parser.add_argument("-f","--file",required=True,nargs='+',help="the dictionary files name.")
    parser.add_argument("-m","--method",default="HEAD",choices=['HEAD','GET','OPTIONS','POST'],help="set http method.")
    parser.add_argument("-t","--threads",default=20,type=int,help="set threads count.")
    parser.add_argument("-T","--timeout",type=float,default=5,help="set timeout.")
    parser.add_argument("-c","--code",nargs='+',default=["200","403"],help="set the http return code to distinguish")
    parser.add_argument("-o","--outfile",nargs='?',const="scansuccessurl.txt",help="set outfile.")
    
    args = parser.parse_args()
    url = args.url.strip('/')+'/'
    fileList = args.file
    method = args.method
    threadsNum = args.threads
    codeList = args.code 
    outfileName = args.outfile
    timeout = args.timeout
    headers = {}    # here change headers
    session = requests.Session()
    session.headers.update(headers)
    if(outfileName):
        try:
            outfile = open(outfileName,'w')
        except:
            print_error('The outfile  "%s" open failed!'%outfileName)
            return
        
    for name in fileList:
        try:
            f = open(name,'r')
            fieldList.extend(f.read().strip().split('\n'))
            f.close()
        except:
            print_error('The dic file  "%s" open failed!'%outfileName)
            continue
    
    tl = []
    for t in range(threadsNum):
        t = threading.Thread(target=work)
        tl.append(t)
    for t in tl:
        t.start()
    for t in tl:
        t.join()
        
    print_yes('all done!')
    try:
        outfile.close()
        session.close()
    except:
        pass
url = ''
fileList = []
method = ''
threadsNum = 20
codeList = []
session = ''
timeout = 5
outfile = ''
attempts = 0
lock = threading.RLock()
fieldList = []
indexOffield = 0

if __name__ == '__main__':
    main()
