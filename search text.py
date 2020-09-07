# -*- coding:utf-8 -*-
import sys, os, re
from workflow import Workflow3
import time
from pprint import pprint
from fd import getsize

file_types = '''--actionscript: .as .mxml
--ada: .ada .adb .ads
--asciidoc: .adoc .ad .asc .asciidoc
--apl: .apl
--asm: .asm .s
--batch: .bat .cmd
--bitbake: .bb .bbappend .bbclass .inc
--bro: .bro .bif
--cc: .c .h .xs
--cfmx: .cfc .cfm .cfml
--chpl: .chpl
--clojure: .clj .cljs .cljc .cljx
--coffee: .coffee .cjsx
--coq: .coq .g .v
--cpp: .cpp .cc .C .cxx .m .hpp .hh .h .H .hxx .tpp
--crystal: .cr .ecr
--csharp: .cs
--css: .css
--cython: .pyx .pxd .pxi
--delphi: .pas .int .dfm .nfm .dof .dpk .dpr .dproj .groupproj .bdsgroup .bdsproj
--dlang: .d .di
--dot: .dot .gv
--dts: .dts .dtsi
--ebuild: .ebuild .eclass
--elisp: .el
--elixir: .ex .eex .exs
--elm: .elm
--erlang: .erl .hrl
--factor: .factor
--fortran: .f .f77 .f90 .f95 .f03 .for .ftn .fpp
--fsharp: .fs .fsi .fsx
--gettext: .po .pot .mo
--glsl: .vert .tesc .tese .geom .frag .comp
--go: .go
--groovy: .groovy .gtmpl .gpp .grunit .gradle
--haml: .haml
--handlebars: .hbs
--haskell: .hs .hsig .lhs
--haxe: .hx
--hh: .h
--html: .htm .html .shtml .xhtml
--idris: .idr .ipkg .lidr
--ini: .ini
--ipython: .ipynb
--isabelle: .thy
--j: .ijs
--jade: .jade
--java: .java .properties
--jinja2: .j2
--js: .es6 .js .jsx .vue
--json: .json
--jsp: .jsp .jspx .jhtm .jhtml .jspf .tag .tagf
--julia: .jl
--kotlin: .kt
--less: .less
--liquid: .liquid
--lisp: .lisp .lsp
--log: .log
--lua: .lua
--m4: .m4
--make: .Makefiles .mk .mak
--mako: .mako
--markdown: .markdown .mdown .mdwn .mkdn .mkd .md
--mason: .mas .mhtml .mpl .mtxt
--matlab: .m
--mathematica: .m .wl
--md: .markdown .mdown .mdwn .mkdn .mkd .md
--mercury: .m .moo
--naccess: .asa .rsa
--nim: .nim
--nix: .nix
--objc: .m .h
--objcpp: .mm .h
--ocaml: .ml .mli .mll .mly
--octave: .m
--org: .org
--parrot: .pir .pasm .pmc .ops .pod .pg .tg
--pdb: .pdb
--perl: .pl .pm .pm6 .pod .t
--php: .php .phpt .php3 .php4 .php5 .phtml
--pike: .pike .pmod
--plist: .plist
--plone: .pt .cpt .metadata .cpy .py .xml .zcml
--proto: .proto
--pug: .pug
--puppet: .pp
--python: .py
--qml: .qml
--racket: .rkt .ss .scm
--rake: .Rakefile
--restructuredtext: .rst
--rs: .rs
--r: .r .R .Rmd .Rnw .Rtex .Rrst
--rdoc: .rdoc
--ruby: .rb .rhtml .rjs .rxml .erb .rake .spec
--rust: .rs
--salt: .sls
--sass: .sass .scss
--scala: .scala
--scheme: .scm .ss
--shell: .sh .bash .csh .tcsh .ksh .zsh .fish
--smalltalk: .st
--sml: .sml .fun .mlb .sig
--sql: .sql .ctl
--stata: .do .ado
--stylus: .styl
--swift: .swift
--tcl: .tcl .itcl .itk
--terraform: .tf .tfvars
--tex: .tex .cls .sty
--thrift: .thrift
--tla: .tla
--tt: .tt .tt2 .ttml
--toml: .toml
--ts: .ts .tsx
--twig: .twig
--vala: .vala .vapi
--vb: .bas .cls .frm .ctl .vb .resx
--velocity: .vm .vtl .vsl
--verilog: .v .vh .sv
--vhdl: .vhd .vhdl
--vim: .vim
--wix: .wxi .wxs
--wsdl: .wsdl
--wadl: .wadl
--xml: .xml .dtd .xsl .xslt .ent .tld .plist
--yaml: .yaml .yml'''


def ag(paras, max_count=100, arg='ts', path_L=('.',), depth=100, lr_charNum=15, show_count=20, show_results=200,
       f_types='', f_ignore=""):
    """
    :param paras: ['待检索关键词',..]
    :param max_count: 每个结果最多寻找多少条匹配位置
    :param arg: ag 参数
    :param path_L: 所有待检索路径
    :param depth: 最大检索目录深度
    :param lr_charNum: 显示匹配词左右多少字符
    :param show_count: 每个结果显示多少条匹配位置
    :param show_results: 显示多少条结果
    :param f_types: 文件类型参数, 比如 '--python --java'
    :param f_ignore: 忽略匹配文件(全路径), 比如 "'**.txt','**.json'"
    :return:
    """
    paras_ = ['(?=.*%s)' % i for i in paras]
    ret = []  # [['文件路径',[(行号,文本),..],'父路径'],..]
    stat = []  # 每个路径一个统计
    for path in path_L:
        path = os.path.expanduser(path)
        command = "./ag %s -i%sm%d --column --silent --nocolor --stats --ackmate --ignore={%s,} --depth %d '%s' '%s'" % \
                  (f_types, arg, max_count, f_ignore, depth, '^' + ''.join(paras_) + '.*', path)
        output = os.popen(command).readlines()
        assert 'can be found at' not in output[-1], 'ag 参数错误!'
        for line in output:
            line = line.strip()
            if not line:
                continue
            if line[0] == ':':
                ret.append([line[1:], [], path])
            elif re.search('^[0-9]+;', line):
                ret[-1][1].append((0, line))
        stat.append(output[-5:])  # 最后5行是统计结果
    ret = sorted(ret, key=lambda t: -len(t[1]))  # 数量排序
    # 加速, 不显示的文本就不要了
    for _, n_text_L, _ in ret[:show_results]:
        for i, (_, line) in enumerate(n_text_L[:show_count]):
            n, other = line.split(';', 1)
            text = other.split(':', 1)[1].decode('utf-8', errors='ignore')  # 提前解码, 防止中文截取字符3倍过少
            p = paras[0].decode('utf-8')
            if 's' not in arg:  # 大小写不敏感
                s, e = re.search(p, text, re.IGNORECASE).span()
            else:
                s, e = re.search(p, text).span()
            lr_charNum_ = lr_charNum  # 到边界的话长度另一边补充上去, 太长太多可能导致alfred显示不出来
            lr_charNum_ += - min(0, s - lr_charNum) - min(0, len(text) - e - lr_charNum)
            # lr_charNum_ = min(lr_charNum_, 2 * lr_charNum)
            text = '...' + text[max(0, s - lr_charNum_): e + lr_charNum_] + '...'
            text = re.sub(r'\s+', ' ', text)  # 长空白去掉
            n_text_L[i] = (n, text)
    # 统计整合
    ss = [i.strip().split(' ', 1) for i in stat[0]]  # [[统计数字, 描述],..]
    ss = [[float(i) if '.' in i else int(i), j] for i, j in ss]
    for i in stat[1:]:
        for j, v in enumerate(i):
            v = v.split(' ', 1)[0]
            ss[j][0] += float(v) if '.' in v else int(v)
    return ret, ss


# ret, stat = ag(paras=['asdv'], path_L=['~/Nutstore Files'])
# for i in ret:
#     print(i)
# pprint(stat)


def main(wf):
    start = time.time()
    file_num = 0
    all_size = 0
    max_size = 0
    max_file = ''
    max_sPath = ''
    max_allPath = ''

    # sys.argv = ['python', 'search text.py', '~/Nutstore Files', 'abc']
    paras_pos = 2
    arg = ''
    f_types = ''  # 比如 '--python --cc'
    f_ignore = ''  # 比如 '**.txt','**.json'
    if sys.argv[2][0] == '-':  # 输入ag命令的参数
        flags = {'s', 't', '-', '.'}
        arg = sys.argv[2][1:]
        t = len(set(arg) - flags) == 0
        # 约束输入参数的正确性
        search = True
        if re.search(r'[\-.]', arg) and len(sys.argv) > 3:
            if len(sys.argv) <= 4:
                search = False
            if '-' in arg and re.search('[^a-z,]|,$|^,', sys.argv[3]):
                t = False
        if t and len(sys.argv) > 3 and search:
            if re.search(r'[\-.]', arg):  # 指定文件类型, 或排除
                if '-' in arg:
                    f_types = '--' + sys.argv[3].replace(',', ' --')
                else:
                    f_ignore = "'**" + sys.argv[3].replace(':', "','**") + "'"
                arg = re.sub(r'[\-.]', '', arg)
                paras_pos = 4
            else:
                paras_pos = 3
        else:
            title = '参数 例如:-st,-s,-,...'
            subtitle = 's:大小写敏感, t:所有文本, -:指定文件类型(⌘查看介绍), .:排除文件后缀'
            wf.add_item(
                title=(title if t else (title + '  输入参数错误!')),
                subtitle=subtitle,
                largetext=file_types,
            ).add_modifier(key='cmd', subtitle='指定文件类型(⌘+L查看支持文件类型), 比如 --st py,cc,java 关键词')
            wf.add_item(
                title="使用指定文件类型参数'-' 则不会再考虑'.'",
                subtitle='排除文件(冒号分割): 比如 -. py*:c:.txt 关键词',
                largetext=file_types,
            )
            wf.send_feedback()
            return

    show_results = 100  # 显示多少条结果
    show_count = 20  # 每个结果显示多少条匹配位置
    max_count = 1000  # 每个结果最多寻找多少条匹配位置
    depth = 50  # 最大检索目录深度
    lr_charNum = 15  # 显示匹配词左右多少字符

    paras = sys.argv[paras_pos:]
    fPath_L = [os.path.expanduser(i) for i in sys.argv[1].split(':')]
    ret, stat = ag(paras, max_count=max_count, arg=arg, path_L=fPath_L, depth=depth, lr_charNum=lr_charNum,
                   show_count=show_count, show_results=show_results, f_types=f_types, f_ignore=f_ignore)

    for i, (allPath, n_text_L, fPath) in enumerate(ret):
        sPath = allPath.replace(fPath, '').strip(os.sep)
        if len(fPath_L) > 1:  # 多个目录则显示上一层的目录
            sPath = os.path.join(os.path.split(fPath)[1], sPath)
        path, file = os.path.split(allPath)
        x = getsize(allPath)
        size = x[3]  # str

        file_num += 1
        all_size += x[2]
        if x[2] > max_size:
            max_size = x[2]
            max_file = file
            max_sPath = sPath
            max_allPath = allPath

        if i < show_results:  # 限制显示数量
            show_pos = '\n'.join([': '.join(i) for i in n_text_L[:show_count]]).encode('utf-8')
            if len(n_text_L) > show_count:
                show_pos += '\n...'
            wf.add_item(
                title=file + ' (%d行)' % len(n_text_L),
                subtitle=': '.join(n_text_L[0]),
                arg=allPath,
                valid=True,
                icon=allPath,
                quicklookurl=allPath,
                largetext=allPath + '   (' + size + ')\n匹配位置(行, 最多显示%d个):\n' % show_count + show_pos,
            ).add_modifier(key='cmd', subtitle=os.path.split(sPath)[0])
    wf.add_item(
        title='f: %d, s: %s, time: %.2fs  (详情:⌘+L)' %
              (file_num, getsize(all_size)[3], time.time() - start),
        subtitle='max: ' + max_file,
        arg=max_allPath,
        icon=max_allPath,
        quicklookurl=max_allPath,
        valid=True,
        largetext='max: ' + max_allPath + '  (' + getsize(max_size)[3] + ')'
                  + '\n' + 'f:文件数量, s:文件总大小, time:检索耗时(秒)'
                  + '\n' + '由于限制了显示数量(%d)和匹配位置数量(%d)等, 统计数量可能不全' % (show_results, max_count)
                  + '\n' + '-' * 10 + 'ag:'
                  + '\n' + '\n'.join(['%s %s' % (str(i[0]), i[1]) for i in stat])
    ).add_modifier(key='cmd', subtitle=os.path.split(max_sPath)[0])
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
