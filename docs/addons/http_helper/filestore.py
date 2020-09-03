# coding:utf-8
import os
from datetime import datetime
from uuid import uuid4
_default_save_parrent = '/data/mitm/storage/'


def filestore(stream, uniq_suf, date=None, suffix=''):
    """
    输入一个独特的字符川，接着会按照这个字符串的位置进行存储，后期使用分布式存储。
    :param uniq_suf:
    :return:
    """
    # 这行肯定不严密注意严格按照我们的规范来，不要输入错误的date
    _date = date if type(date) == str else str(date) if date else str(datetime.now().date())
    _save_path = os.path.join(_default_save_parrent, _date, uniq_suf)
    if not os.path.isdir(_save_path):
        os.makedirs(_save_path)
    filename = os.path.join(_save_path, str(uuid4()) + suffix)
    with open(filename, 'wb') as f:
        f.write(stream)
        f.close()
    # 日志阶段; 写入文件相关的日志
    return filename


def clear_all_file():
    os.system('rm -rf {}'.format(_default_save_parrent))
    print('clear all ok')


if __name__ == '__main__':
    stream = open('/root/test.py', 'rb').read()
    filestore(stream, 'demo_test', date=None, suffix='.py')

    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clear':
            clear_all_file()