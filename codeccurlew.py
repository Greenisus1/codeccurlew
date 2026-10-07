#!/usr/bin/env python3
"""Codeccurlew: read-only BOM, strict decoding and newline inspection."""
import argparse,json,os,stat,sys
from pathlib import Path
BOMS=[(b'\xff\xfe\x00\x00','UTF-32 LE','utf-32'),(b'\x00\x00\xfe\xff','UTF-32 BE','utf-32'),(b'\xef\xbb\xbf','UTF-8','utf-8-sig'),(b'\xff\xfe','UTF-16 LE','utf-16'),(b'\xfe\xff','UTF-16 BE','utf-16')]
ENCODINGS=('utf-8','utf-8-sig','utf-16','utf-16-le','utf-16-be','utf-32','utf-32-le','utf-32-be','ascii','latin-1')
def read(path):
    fd=os.open(Path(path).expanduser(),os.O_RDONLY|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):raise ValueError('Choose a regular file.')
        data=f.read(8*1024*1024+1)
    if len(data)>8*1024*1024:raise ValueError('Maximum 8 MiB.')
    return data

def inspect(data,encoding=None):
    bom=next(((label,codec) for prefix,label,codec in BOMS if data.startswith(prefix)),None)
    selected=encoding or (bom[1] if bom else 'utf-8')
    if selected not in ENCODINGS:raise ValueError('Unsupported explicit encoding.')
    report={'format':'codeccurlew-1','bytes':len(data),'bom':bom[0] if bom else None,'selected_encoding':selected,'selection':'explicit' if encoding else 'BOM' if bom else 'default UTF-8, not detected','nul_bytes':data.count(b'\x00')}
    try:
        if selected in ('utf-16','utf-32') and not (bom and bom[1]==selected):raise UnicodeError('Explicit '+selected+' requires matching BOM; choose LE/BE for BOM-less data.')
        text=data.decode(selected,errors='strict')
    except UnicodeError as exc:report.update({'decoded':False,'decode_error':str(exc),'characters':None});return report
    crlf=text.count('\r\n');bare_lf=text.count('\n')-crlf;bare_cr=text.count('\r')-crlf
    report.update({'decoded':True,'characters':len(text),'crlf':crlf,'bare_lf':bare_lf,'bare_cr':bare_cr,'mixed_cr_lf_styles':sum(n>0 for n in (crlf,bare_lf,bare_cr))>1,'ends_cr_or_lf':text.endswith(('\r','\n')),'nul_characters':text.count('\x00'),'non_ascii_characters':sum(ord(c)>127 for c in text),'unicode_line_separators':sum(text.count(c) for c in ('\x85','\u2028','\u2029'))})
    return report

def show(r):
    print('\nCODECCURLEW | read-only encoding checks')
    for k,v in r.items():
        if k!='format':print(k+':',str(v).replace('\x1b','\\x1b'))
    print('Successful decoding is not proof of intended encoding. No content preview or conversion writes.')

def save(r,path):
    with open(Path(path).expanduser(),'x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',nargs='?');p.add_argument('--encoding',choices=ENCODINGS);p.add_argument('--output');a=p.parse_args(argv)
    try:
        if a.file:r=inspect(read(a.file),a.encoding);show(r);save(r,a.output) if a.output else None;return 0 if r['decoded'] else 1
        while True:
            print('\nCODECCURLEW\n1 Inspect file  0 Exit');c=input('> ').strip()
            if c=='0':return 0
            if c!='1':continue
            try:
                path=input('Filename: ');encoding=input('Encoding [blank uses BOM/default UTF-8]: ').strip() or None;r=inspect(read(path),encoding);show(r);out=input('New JSON report (blank skips): ').strip()
                if out:save(r,out)
            except (OSError,ValueError) as exc:print('Error:',exc)
    except (EOFError,KeyboardInterrupt):print('\nBye.')
    except (OSError,ValueError) as exc:print('Error:',exc,file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
