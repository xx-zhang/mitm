# encoding=utf-8
"""
author: -
create: 2018-08-23 10:36
overview:
"""
import json
import binascii
import shutil
import struct
import shlex
import os
import subprocess
import sys
ALGORITHM_NAME = 0x1
ALGORITHM_VERSION = 0x1

RULE_TYPE = 0x1
SYS_TYPE = 0x2
RULE_TPL_TYPE = 0x3  # 规则模板

__VERSION__ = 2, 0

__TAR_CMD = "/usr/bin/tar"
__SUFFIX = '.up'
__DCMD = '/usr/bin/openssl'


def gen_tmp_filename():
    __tmp = os.urandom(16)
    __tmp = binascii.b2a_hex(__tmp).decode('utf-8')
    return __tmp


class FileHeader(object):
    __slots__ = 'file_type', 'at', 'av'

    def __init__(self):
        self.file_type = None
        self.at = None  # 算法名称
        self.av = None  # 算法版本

    def unpack(self, _buff):
        self.file_type = struct.unpack('>I', _buff[:4])[0]
        self.at = struct.unpack('>I', _buff[4:8])[0]
        self.av = struct.unpack('>I', _buff[8:12])[0]

    def pack(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return "<file_type=%s,at=%s,av=%s>" % (self.file_type, self.at, self.av)


class RuleHeader(FileHeader):
    __slots__ = 'major', 'minor'

    def __init__(self):
        self.major = 0
        self.minor = 0
        super().__init__()

    def unpack(self, _buff):
        super().unpack(_buff)
        self.major = struct.unpack('>I', _buff[12:16])[0]
        self.minor = struct.unpack('>I', _buff[16:20])[0]

    def pack(self, _file_type, _at, _av, _major, _minor):
        return struct.pack('>IIIII', _file_type, _at, _av, _major, _minor)

    def __str__(self):
        return "<file_type=%s,at=%s,av=%s,version=%s.%s>" % (self.file_type, self.at, self.av, self.major, self.minor)


class SysHeader(RuleHeader):
    __slots__ = ()


class RuleTPLHeader(FileHeader):
    __slots__ = ()

    def pack(self, _file_type, _at, _av):
        return struct.pack('>III', _file_type, _at, _av)


def __execute_cmd(cmd, shell=False):
    if shell is True:
        args = cmd
    else:
        args = shlex.split(cmd)

    dev_null = os.devnull
    with open(dev_null, 'wb') as fd:
        process = subprocess.Popen(args, bufsize=0, stdin=None,
                                   stdout=fd, stderr=fd, close_fds=True,
                                   shell=shell, cwd=None)

    process.wait()
    code = process.returncode
    return code


def decrypt_sys(_pass, _enc_file, _dst_path, _current_version=None, _callback=None):
    """
    """
    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # tmp dir
    __done_dir = os.path.join(_dst_path, gen_tmp_filename())
    if os.path.exists(__done_dir) is False:
        os.makedirs(__done_dir)
    try:
        with open(_enc_file, 'rb') as __fd:
            __buff = __fd.read(20)
            __file_header = SysHeader()
            __file_header.unpack(__buff)
            __tmp_data = __fd.read()

        if __file_header.file_type != SYS_TYPE:
            return 1, None

        if __file_header.at != ALGORITHM_NAME or __file_header.av != ALGORITHM_VERSION:
            return 2, None

        if _current_version:
            if _current_version >= (__file_header.major, __file_header.minor):
                return 4, None

        # 解密文件
        __enc_file = os.path.join(__done_dir, gen_tmp_filename())
        with open(__enc_file, 'wb') as __fd:
            __fd.write(__tmp_data)

        _gz_file = os.path.join(
            __done_dir, gen_tmp_filename())  # 解密后的文件， 即压缩文件路径
        # 先解密
        __cmd = "%s enc -d -aes-256-cbc -in %s -out %s -pass file:%s" % (
            __DCMD, __enc_file, _gz_file, _pass)
        __code = __execute_cmd(__cmd)
        if __code != 0:
            # 解密失败
            return 5, None

        # 解压后的文件夹
        __dst_gz_path = os.path.join(__done_dir, gen_tmp_filename())
        if os.path.exists(__dst_gz_path) is False:
            os.makedirs(__dst_gz_path)

        __cmd = "%s -zxvf %s -C %s" % (__TAR_CMD, _gz_file, __dst_gz_path)
        __code = __execute_cmd(__cmd)
        if __code != 0:
            # 解压失败
            return 6, None

        _callback(__dst_gz_path, _current_sys_version=_current_version)
    finally:
        shutil.rmtree(__done_dir, True)

    return 0, (__file_header.major, __file_header.minor)


def encrypt_sys(_file_type, _at, _av, _pass, _abs_dir, _dst_path, _update_version):
    """
    系统更新 一般 都是 以文件夹形式 打包
    :return:
    :param tuple _update_version: 此更新包中 最大的版本号
    """
    assert isinstance(_update_version, tuple) is True
    assert _file_type == SYS_TYPE, "The is the encrypt sys method!"

    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # 临时处理目录
    __tmp_dir = os.path.join(_dst_path, gen_tmp_filename())
    if os.path.exists(__tmp_dir) is False:
        os.makedirs(__tmp_dir)
    try:
        __tmp_tar_gz = os.path.join(
            __tmp_dir, "%s.tar.gz" % gen_tmp_filename())
        os.chdir(_abs_dir)
        __cmd = "%s -zcvf %s  %s" % (__TAR_CMD, __tmp_tar_gz, "*")
        __code = __execute_cmd(__cmd, shell=True)
        if __code != 0:
            return '压缩失败'

        __en_file = os.path.join(__tmp_dir, gen_tmp_filename())
        __cmd = "%s enc -aes-256-cbc -salt -in %s -out %s -pass file:%s" % (
            __DCMD, __tmp_tar_gz, __en_file, _pass)
        __code = __execute_cmd(__cmd)

        if __code != 0:
            return "加密失败"

        # 压缩前的文件名为 ***.up
        __tmp_file = os.path.join(_dst_path, "sys_%s%s" %
                                  (gen_tmp_filename(), __SUFFIX))
        with open(__en_file, 'rb') as __fd:
            __tmp_data = __fd.read()
        # 删除临时
        os.remove(__en_file)

        __major, __minor = _update_version

        __tmp = SysHeader()
        __tmp = __tmp.pack(_file_type=_file_type, _at=_at,
                           _av=_av, _major=__major, _minor=__minor)

        with open(__tmp_file, 'wb') as __fd:
            __fd.write(__tmp)
            __fd.write(__tmp_data)

    finally:
        shutil.rmtree(__tmp_dir, True)
    return "加密，压缩成功"


def encrypt_rule_tpl(_file_type, _at, _av, _pass, _abs_filename, _dst_path, _output_name=None):
    """
    加密 规则模板
    :param _file_type:
    :param _at:
    :param _av:
    :param _pass: 绝对路径
    :param str _abs_filename: 要加密的规则 模板
    :param str _dst_path:
    :param str _output_name: 最终输出的文件名
    :return:
        1: 加密失败
    """
    if _file_type != RULE_TPL_TYPE:
        raise "加密类型错误：%s" % _file_type

    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # 临时处理目录
    __tmp_dir = os.path.join(_dst_path, gen_tmp_filename())
    try:
        if os.path.exists(__tmp_dir) is False:
            os.makedirs(__tmp_dir)

        __en_file = os.path.join(__tmp_dir, gen_tmp_filename())
        __cmd = "%s enc -aes-256-cbc -salt -in %s -out %s -pass file:%s" % (
            __DCMD, _abs_filename, __en_file, _pass)
        __code = __execute_cmd(__cmd)

        if __code != 0:
            return 1
        if not _output_name:
            _output_name = gen_tmp_filename()

        __tmp_file = os.path.join(_dst_path, _output_name)
        with open(__en_file, 'rb') as __fd:
            __tmp_data = __fd.read()
        # 删除临时
        os.remove(__en_file)
        __tmp = RuleTPLHeader().pack(_file_type=_file_type, _at=_at, _av=_av)
        with open(__tmp_file, 'wb') as __fd:
            __fd.write(__tmp)
            __fd.write(__tmp_data)

    finally:
        shutil.rmtree(__tmp_dir, True)
    return 0


def decrypt_rule_tpl(_pass, _enc_file, _dst_path):
    """
    解密规则模板 规则模板
    :param _pass: 绝对路径
    :param str _enc_file: 要加密的规则 模板
    :param str _dst_path:
    :return:
        1:  不支持的文件类型
        2:  不支持的文件加密算法
        3:  解密失败
    """

    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # 临时处理目录
    __tmp_dir = os.path.join(_dst_path, gen_tmp_filename())
    try:
        if os.path.exists(__tmp_dir) is False:
            os.makedirs(__tmp_dir)

        with open(_enc_file, 'rb') as __fd:
            __buff = __fd.read(12)
            __file_header = RuleTPLHeader()
            __file_header.unpack(__buff)

            __tmp = __fd.read()

        if __file_header.file_type != RULE_TPL_TYPE:
            return 1, None
        if __file_header.at != ALGORITHM_NAME or __file_header.av != ALGORITHM_VERSION:
            return 2, None

        __tmp_file = os.path.join(__tmp_dir, gen_tmp_filename())
        with open(__tmp_file, 'wb') as __fd:
            __fd.write(__tmp)

        __de_file = os.path.join(__tmp_dir, gen_tmp_filename())

        __cmd = "%s enc -d -aes-256-cbc -in %s -out %s -pass file:%s" % (
            __DCMD, __tmp_file, __de_file, _pass)
        __code = __execute_cmd(__cmd)
        os.remove(__tmp_file)
        if __code != 0:
            return 3, None  # 解密失败
        with open(__de_file, 'rb') as __fd:
            __data = __fd.read()

    finally:
        shutil.rmtree(__tmp_dir, True)
    return 0, __data


def decrypt_rule(_pass, _enc_file, _dst_path, _current_version=None):
    """
    解密 规则更新文件
    :param _pass:
    :param _enc_file:
    :param _dst_path:
    :param tuple _current_version:
    :return:
        1: 不支持的文件类型
        2: 不支持的文件加密算法
        3: 解密失败
        4: 不需要更新， 版本已经是最新的
    """
    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # tmp dir
    __done_dir = os.path.join(_dst_path, gen_tmp_filename())
    if os.path.exists(__done_dir) is False:
        os.makedirs(__done_dir)
    try:
        with open(_enc_file, 'rb') as __fd:
            __buff = __fd.read(20)
            __file_header = RuleHeader()
            __file_header.unpack(__buff)
            __tmp_data = __fd.read()

        if __file_header.file_type != RULE_TYPE:
            return 1, None

        if __file_header.at != ALGORITHM_NAME or __file_header.av != ALGORITHM_VERSION:
            return 2, None

        if _current_version:
            if _current_version >= (__file_header.major, __file_header.minor):
                return 4, None

        # 解密文件
        __enc_file = os.path.join(__done_dir, gen_tmp_filename())
        with open(__enc_file, 'wb') as __fd:
            __fd.write(__tmp_data)

        __rule_file = os.path.join(
            __done_dir, gen_tmp_filename())  # 解密后的文件， 即压缩文件路径
        # 先解密
        __cmd = "%s enc -d -aes-256-cbc -in %s -out %s -pass file:%s" % (
            __DCMD, __enc_file, __rule_file, _pass)
        __code = __execute_cmd(__cmd)
        if __code != 0:
            return 3, None

        with open(__rule_file, 'rb') as __fd:
            __tmp = __fd.read()
        __tmp = json.loads(__tmp)

    finally:
        shutil.rmtree(__done_dir, True)

    return 0, __tmp


def encrypt_rule(_file_type, _at, _av, _pass, _abs_filename, _dst_path, _update_version):
    """
    :param tuple _update_version: 此更新包中 最大的版本号
    :return:
        1: 加密失败
    """
    assert isinstance(_update_version, tuple) is True
    assert _file_type == RULE_TYPE, "The is the encrypt rule method!"

    if os.path.exists(_dst_path) is False:
        os.makedirs(_dst_path)

    # 临时处理目录
    __tmp_dir = os.path.join(_dst_path, gen_tmp_filename())
    if os.path.exists(__tmp_dir) is False:
        os.makedirs(__tmp_dir)
    try:
        __en_file = os.path.join(__tmp_dir, gen_tmp_filename())
        __cmd = "%s enc -aes-256-cbc -salt -in %s -out %s -pass file:%s" % (
            __DCMD, _abs_filename, __en_file, _pass)
        __code = __execute_cmd(__cmd)
        if __code != 0:
            return 1

        # 压缩前的文件名为 ***.up
        __tmp_file = os.path.join(_dst_path, "rule_%s%s" %
                                  (gen_tmp_filename(), __SUFFIX))
        with open(__en_file, 'rb') as __fd:
            __tmp_data = __fd.read()
        # 删除临时
        os.remove(__en_file)
        __tmp = RuleHeader()
        __major, __minor = _update_version
        __tmp = __tmp.pack(_file_type=_file_type, _at=_at,
                           _av=_av, _major=__major, _minor=__minor)

        with open(__tmp_file, 'wb') as __fd:
            __fd.write(__tmp)
            __fd.write(__tmp_data)

    finally:
        shutil.rmtree(__tmp_dir, True)
    return 0


def test(*args, **kwargs):
    print("Test Callback args ...")
    print(args, kwargs)
    

def main():
    _pass = "/root/gen_key/pass.txt"
    if 0:
        if 0:
            a = encrypt_rule_tpl(_file_type=RULE_TPL_TYPE, 
                                 _at=ALGORITHM_NAME, 
                                 _av=ALGORITHM_VERSION,
                                 _pass=_pass,
                                 _abs_filename='/root/lru-dict-1.1.6.tar.gz',
                                 _dst_path='/tmp', _output_name='name1.up')

        if 1:
            a = decrypt_rule_tpl(_pass=_pass, _enc_file='/tmp/name1.up',
                                 _dst_path='/tmp')
            with open("/tmp/xxx.tar.gz", 'wb') as fd:
                fd.write(a[1])
        print(a)
    # #############################
    if 0:
        if 1:
            a = encrypt_rule(_file_type=RULE_TYPE, _at=ALGORITHM_NAME, _av=ALGORITHM_VERSION,
                             _pass=_pass,
                             _abs_filename='/root/gen_key/rules.json',
                             _dst_path='/tmp', _update_version=(1, 4))

        if 0:
            a = decrypt_rule(_pass=_pass, _enc_file='/tmp/rule_79df8173b245125b8cce2c8301e1159b.up',
                             _dst_path='/tmp', _current_version=(1, 3))
        print(a)

    if 1:
        # 文件 清单
        if 0:
            a = encrypt_sys(_file_type=SYS_TYPE, 
                            _at=ALGORITHM_NAME, 
                            _av=ALGORITHM_VERSION,
                            _pass=_pass,
                            _abs_dir='/apps/sys_update',
                            _dst_path='/tmp', _update_version=(1, 1))

        if 1:
            a = decrypt_sys(_pass=_pass, _enc_file='/tmp/sys_84b4a57dacf21d62900f78cbe868941a.up',
                            _dst_path='/tmp', _current_version=(1, 0), _callback=test)
        print(a)


if __name__ == '__main__':
    main()
