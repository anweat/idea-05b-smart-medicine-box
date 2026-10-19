#!/usr/bin/env python3
import argparse, pathlib, sys

def main():
    ap=argparse.ArgumentParser(description='Replace GitHub links in docs/index.html with domestic URLs')
    ap.add_argument('--repo', required=True, help='domestic repo URL, e.g. https://atomgit.com/user/repo')
    ap.add_argument('--release', required=True, help='domestic release zip URL')
    ap.add_argument('--site', default='', help='domestic Pages site URL (for canonical/og)')
    ap.add_argument('--file', default='docs/index.html')
    a=ap.parse_args()
    p=pathlib.Path(a.file)
    s=p.read_text(encoding='utf-8')
    gh_repo='https://github.com/anweat/idea-05b-smart-medicine-box'
    gh_rel=gh_repo+'/releases/download/v1.0.0/IDEA-05B_delivery_20261018.zip'
    gh_site='https://anweat.github.io/idea-05b-smart-medicine-box'
    s=s.replace(gh_rel,a.release)
    s=s.replace(gh_repo,a.repo)
    if a.site:
        s=s.replace(gh_site,a.site.rstrip('/'))
    s=s.replace('>GitHub ↗<','>代码仓库 ↗<')
    p.write_text(s,encoding='utf-8')
    print('patched',p,'->',a.repo)
if __name__=='__main__':
    main()
