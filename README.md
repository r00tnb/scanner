# scanner
用Python2写的网站目录文件扫描程序

usage: scanner.py [-h] -f FILE [FILE ...] [-m {HEAD,GET,OPTIONS,POST}]
                  [-t THREADS] [-T TIMEOUT] [-c CODE [CODE ...]]
                  [-o [OUTFILE]]
                  url

positional arguments:
  url                   scanning the url.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE [FILE ...], --file FILE [FILE ...]
                        the dictionary files name.
  -m {HEAD,GET,OPTIONS,POST}, --method {HEAD,GET,OPTIONS,POST}
                        set http method.
  -t THREADS, --threads THREADS
                        set threads count.
  -T TIMEOUT, --timeout TIMEOUT
                        set timeout.
  -c CODE [CODE ...], --code CODE [CODE ...]
                        set the http return code to distinguish
  -o [OUTFILE], --outfile [OUTFILE]
                        set outfile.

 更新：
 20180828
    1.将scanner从码云移植到github。
