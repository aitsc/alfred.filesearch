# -*- coding:utf-8 -*-
import sys, os, re
from workflow import Workflow3
import time
from fd import getsize


def seg(utext='', n=3):
    '''
    :param utext: utf-8 编码的字符串
    :param n: 穷举分割最大长度, 0表示不分割
    :return: 空格+不分割+按长度1分割+...
    '''
    utext_noSpace = utext.replace(' ', '')  # 去除空格后分割
    join = [' ' + utext]
    for i in range(1, n + 1):
        for j in range(i):
            join.append(re.sub('(.{%d})' % i, r' \1', utext_noSpace[j:]))
    return ' '.join(join)


def hanz2piny(utext_L):
    """
    快速拼音获取
    :param utext_L: ['utf-8编码的字符串',..]
    :return:
    """
    ARG_MAX = int(int(os.popen('getconf ARG_MAX').read()) / 3 - 900)  # 命令行最大参数长度
    utext = '\n'.join(utext_L)
    pinyin = []
    for i in range(0, len(utext), ARG_MAX):
        pinyin.append(os.popen(
            "echo '" + utext[i: i + ARG_MAX].encode('utf-8') +
            "'|./hanz2piny --tone --replace-unknown --replace-unknown-with '' --polyphone all"
        ).read().decode(encoding='utf8')[:-1])
    pinyin = re.sub('[^a-zA-Z\n]+', ' ', ''.join(pinyin)).split('\n')
    return pinyin


def main(wf):
    start = time.time()
    max_age, uuid = sys.argv[1].split(':')  # 比如 60, 7tTzXHqr
    targetPath_L = sys.argv[2].split(':')
    targetPath_L = [i for i in targetPath_L if i]
    suffix_S = sys.argv[3].split(':')
    suffix_S = [i for i in suffix_S if i]
    excludeFolder = sys.argv[4].split(':')
    excludeFolder = [i for i in excludeFolder if i]

    wf_paras = None
    tempFile = 'alfred-search-file.' + uuid + '.pkl2'
    if max_age:
        max_age = float(max_age)
        if max_age > 0:
            wf_paras = wf.cached_data(tempFile, max_age=max_age)
    file_num = 0
    all_size = 0
    max_size = 0
    max_size_name = ''

    if not wf_paras:
        wf_paras = []
        targetPath_L = [os.path.expanduser(i) for i in targetPath_L]
        if not suffix_S:
            paras = '.'
        else:
            suffix_S = set(['[.]' + i.lower() + '$' for i in suffix_S])
            paras = '|'.join(suffix_S)
        if excludeFolder:
            excludeFolder = set(excludeFolder)
        else:
            excludeFolder = set()

        zh_match_L = []
        for targetPath in targetPath_L:
            command = "./fd -ai --regex '%s' '%s'" % (paras, targetPath)
            for i, line in enumerate(os.popen(command).readlines()):
                allPath = line.strip('\r\n')
                fPath, f = os.path.split(allPath)
                if set(fPath.split(os.sep)) & excludeFolder:  # 排除文件
                    continue
                name, suffix = os.path.splitext(f)
                if not name or not suffix:  # 无名字或后缀的文件不要
                    continue
                path = os.path.join(fPath, f)
                x = getsize(path)
                size = x[3]
                uf = f.decode('utf-8')
                match = uf
                match += re.sub('([0-9]+|[a-zA-Z]+)', r' \1 ',
                                re.sub(r'[^0-9a-zA-Z,.:?;!@#$%&*_+=`~|}{<>·/-]+', ' ', uf)) + ' '
                # match += ' '.join(list(re.sub(u'([^0-9a-zA-Z]+)', '', uf))) + ' '  # 字母数字分割
                if re.search(u'[一-龥]', uf):
                    zh_ = re.sub(u'([^一-龥]+)', ' ', uf)
                    zh = seg(zh_, n=4)
                    match += zh + ' '
                    zh_match_L.append(zh_)
                else:
                    zh_match_L.append(u'')
                wf_paras.append({
                    'title': f + ' (' + size + ')',
                    'subtitle': name,
                    'arg': path,
                    'valid': True,
                    'match': match,
                    'icon': path,
                    'quicklookurl': path,
                    'largetext': path,
                    'add_modifier': {
                        'key': 'cmd',
                        'subtitle': fPath,
                    },
                })
                file_num += 1
                all_size += x[2]
                if x[2] > max_size:
                    max_size = x[2]
                    max_size_name = f
        zh_match_L = hanz2piny(zh_match_L)
        for i, v in enumerate(wf_paras):
            v['match'] += zh_match_L[i]
        wf.cache_data(tempFile, data=wf_paras)
    else:
        file_num = len(wf_paras)
        max_size_name = ':缓存文件中调取 ' + tempFile
    # 生成返回值
    for i, v in enumerate(wf_paras):
        wf.add_item(
            title=v['title'],
            subtitle=v['subtitle'],
            arg=v['arg'],
            valid=v['valid'],
            match=v['match'],
            icon=v['icon'],
            quicklookurl=v['quicklookurl'],
            largetext=v['largetext'],
        ).add_modifier(
            key=v['add_modifier']['key'],
            subtitle=v['add_modifier']['subtitle']
        )
    wf.add_item(
        title='num: %d, all: %s, max: %s, time: %.2fs' %
              (file_num, getsize(all_size)[3], getsize(max_size)[3], time.time() - start),
        subtitle='max: ' + max_size_name,
        copytext=max_size_name,
        valid=True,
    )
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
