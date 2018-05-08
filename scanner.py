# -*- coding: utf-8 -*-
import requests,argparse
import threading,sys,math,platform

class progressBar:
    barCount = 20    #the progress bar length
    def __init__(self,lock,count=100,width=60):
        self.count = count
        self.lock = lock
        self.width = width    #the clean blank's width
        self.pos = 0    #current position.max is count
        self.isWindows = True if platform.system()=='Windows' else False

    def move(self,deviation=1):
        with self.lock:
            if(self.pos < self.count):
                self.pos += deviation

    def setCount(self,c):
        self.count = c

    def setWidth(self,w):
        self.width = w

    def __log(self,s,colorStr=''):#colorStr control color
        with self.lock:
            sys.stdout.write(' '* self.width + '\r')
            sys.stdout.flush()
            print colorStr+s    #change color here
            scale = 1.0*self.pos / self.count
            barPos = int(math.floor(progressBar.barCount * scale))
            if(not self.isWindows):
                colorStr = '\033[1;37;40m'
            sys.stdout.write(colorStr+'working... %d/%d [%s%s] %.2f%%\r'%
                             (self.pos,self.count,
                              '#'*barPos,
                              ' '*(progressBar.barCount-barPos),
                              scale*100))
            sys.stdout.flush()
    def update(self):
        colorStr=''
        if(not self.isWindows):
            colorStr = '\033[1;37;40m'
        with self.lock:
            scale = 1.0*self.pos / self.count
            barPos = int(math.floor(progressBar.barCount * scale))
            sys.stdout.write(colorStr+'working... %d/%d [%s%s] %.2f%%\r'%
                                (self.pos,self.count,
                                '#'*barPos,
                              ' '*(progressBar.barCount-barPos),
                              scale*100))
        sys.stdout.flush()
            
    def print_warning(self,s):
        if(self.isWindows):
            self.__log('[-]'+s)
        else:
            colorStr = '\033[1;33m[-]'#highlight yellow
            self.__log(s,colorStr)

    def print_info(self,s):
        if(self.isWindows):
            self.__log('[.]'+s)
        else:
            colorStr = '\033[1;37;40m[.]'#highlight yellow
            self.__log(s,colorStr)

    def print_error(self,s):
        if(self.isWindows):
            self.__log('[!]'+s)
        else:
            colorStr = '\033[1;31m[!]'#highlight yellow
            self.__log(s,colorStr)
    def print_yes(self,s):
        if(self.isWindows):
            self.__log('[+]'+s)
        else:
            colorStr = '\033[1;32m[+]'#highlight yellow
            self.__log(s,colorStr)

def scan(x):
    global url,codeList,method,session,timeout,outfile,attempts,log
    ret = True
    req = requests.Request(method,url+x)
    r = session.prepare_request(req)
    try:
        r = session.send(r,timeout=timeout,allow_redirects=False)
        if(str(r.status_code) in codeList):
            log.print_yes('Find "%s" Response %d'%(url+x,r.status_code))
            if(outfile):
                outfile.write('Find "%s" Response %d\n'%(url+x,r.status_code))
        elif(r.status_code != 404):
            ret = False
            log.print_warning('Maybe "%s" Response %d.'%(url+x,r.status_code))
            if(outfile):
                outfile.write('Maybe "%s" Response %d\n'%(url+x,r.status_code))
        attempts += 1
    except requests.exceptions.Timeout:
        ret = False
        attempts += 1
        log.print_error('The url "%s" timeout!'%(url+x))

    log.move()
    log.update()
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
    global url,fileList,log,threadsNum,codeList,method,session,timeout,outfile,attempts
    parser = argparse.ArgumentParser()
    parser.add_argument("url",help="scanning the url.")
    parser.add_argument("-f","--file",required=True,nargs='+',help="the dictionary files name.")
    parser.add_argument("-m","--method",default="HEAD",choices=['HEAD','GET','OPTIONS','POST'],help="set http method.")
    parser.add_argument("-t","--threads",default=20,type=int,help="set threads count.")
    parser.add_argument("-T","--timeout",type=float,default=5,help="set timeout.")
    parser.add_argument("-c","--code",nargs='+',default=["200","302","403"],help="set the http return code to distinguish")
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
            print '[error]The outfile  "%s" open failed!'%outfileName
            return
        
    for name in fileList:
        try:
            f = open(name,'r')
            fieldList.extend(f.read().strip().split('\n'))
            f.close()
        except Exception as e:
            print '[error]The dic file  "%s" open failed!'%name
            print e
            continue
    log.setCount(len(fieldList))

    #display details
    print 'target: '+url
    print 'method: %s'%method
    print 'success response code: '+' '.join(codeList)
    print 'timeout: %.2fs'%timeout
    s = 'dicFile: '
    for n in fileList:
        s += n+' '
    print s
    print 'outFile: %s'%(outfileName if outfileName else 'None')
    print 'thread count: %d'%threadsNum
    print '\n'
    
    
    tl = []
    for t in range(threadsNum):
        t = threading.Thread(target=work)
        tl.append(t)
    for t in tl:
        t.start()
    for t in tl:
        t.join()
        
    print 'all done!'
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
log = progressBar(lock)

if __name__ == '__main__':
    main()
