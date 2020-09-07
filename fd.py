# -*- coding:utf-8 -*-
import sys, os, re
from workflow import Workflow3
import time
from itertools import permutations


def getsize(path):
    if isinstance(path, int):
        size = path
    else:
        try:
            if not os.path.isdir(path):
                size = os.path.getsize(path)
            else:
                raise 1
        except:
            return 0, '', 0, 'DIR'
    size_B = size
    size /= 1024.
    if size < 1024:
        suffix = 'KB'
    else:
        size /= 1024.
        if size < 1024:
            suffix = 'MB'
        else:
            size /= 1024.
            if size < 1024:
                suffix = 'GB'
            else:
                size /= 1024.
                suffix = 'TB'
    name = '%.2f%s' % (size, suffix)
    return size, suffix, size_B, name


def main(wf):
    start = time.time()
    file_num = 0
    dir_num = 0
    all_size = 0
    max_size = 0
    max_file = ''
    max_sPath = ''
    max_allPath = ''

    paras_pos = 2
    arg = ''
    noFile = noDir = False
    if sys.argv[2][0] == '-':  # 输入fd命令的参数
        flags = {'H', 's', 'p', '-', '='}
        arg = sys.argv[2][1:]
        t = len(set(arg) - flags) == 0 and not ('-' in arg and '=' in arg)
        if t and len(sys.argv) > 3:
            paras_pos = 3
            if '-' in arg:
                arg = arg.replace('-', '')
                noDir = True
            if '=' in arg:
                arg = arg.replace('=', '')
                noFile = True
        else:
            title = '参数 例如:-Hsp,-ps,-s,--,-,...'
            subtitle = 'H:包括隐藏文件, s:大小写敏感, p:全路径搜索, -:不含文件夹, =:不含文件'
            wf.add_item(
                title=(title if t else (title + '  输入参数错误!')),
                subtitle=subtitle,
                largetext=subtitle,
            ).add_modifier(key='cmd', subtitle='⌘+L')
            wf.send_feedback()
            return
    # 全排列用于正则并搜索所有关键词
    paras = []
    for i in permutations(sys.argv[paras_pos:]):
        paras.append('(' + '.*'.join(i) + ')')
    paras = '|'.join(paras)

    max_results = 500
    show_results = 200  # 显示多少条结果
    fPath_L = [os.path.expanduser(i) for i in sys.argv[1].split(':')]
    for fPath in fPath_L:  # 带检索目录
        command = "./fd -ai%s --regex --max-results %d '%s' --search-path '%s'" % (arg, max_results, paras, fPath)
        for i, line in enumerate(os.popen(command).readlines()):
            allPath = line.strip('\r\n')
            sPath = allPath.replace(fPath, '').strip(os.sep)
            if len(fPath_L) > 1:  # 多个目录则显示上一层的目录
                sPath = os.path.join(os.path.split(fPath)[1], sPath)
            path, file = os.path.split(allPath)
            name, suffix = os.path.splitext(file)
            x = getsize(allPath)
            size = x[3]

            if size == 'DIR':
                if noDir:
                    continue
                dir_num += 1
            else:
                if noFile:
                    continue
                file_num += 1
            all_size += x[2]
            if x[2] > max_size:
                max_size = x[2]
                max_file = file
                max_sPath = sPath
                max_allPath = allPath
            if i < show_results:  # 限制显示数量
                wf.add_item(
                    title=file + ' (' + size + ')',
                    subtitle=name,
                    arg=allPath,
                    valid=True,
                    icon=allPath,
                    quicklookurl=allPath,
                    largetext=allPath,
                ).add_modifier(key='cmd', subtitle=os.path.split(sPath)[0])
    wf.add_item(
        title='f: %d, d: %d, s: %s, time: %.2fs  (详情:⌘+L)' %
              (file_num, dir_num, getsize(all_size)[3], time.time() - start),
        subtitle='max: ' + max_file + ' (' + getsize(max_size)[3] + ')',
        arg=max_allPath,
        icon=max_allPath,
        quicklookurl=max_allPath,
        valid=True,
        largetext='max: ' + max_allPath
                  + '\n' + 'f:文件数量, d:文件夹数量, s:文件总大小, time:检索耗时(秒)'
                  + '\n' + '由于限制了显示数量(%d)和检索上限(%d), 统计数量可能不全, 但是加快了速度' % (show_results, max_results),
    ).add_modifier(key='cmd', subtitle=os.path.split(max_sPath)[0])
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
