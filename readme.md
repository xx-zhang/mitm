# 正向代理无敌神器

- [mitmproxy](https://github.com/mitmproxy/mitmproxy)

```bash 
 pip3 install mitmproxy==5.2 --index-url https://pypi.tuna.tsinghua.edu.cn/simple
 kafka_python==2.0.1 
 #pycryptodome
```

## 基本使用
- [插件](./addons)
```bash 
# 代理后访问 mitm.it
```

## 优雅方式启动
- 设置代理的认证 `upstream_auth=username:password`
```bash
/usr/local/bin/mitmproxy  \
    --listen-port 63333  \
    --listen-host 0.0.0.0  \
    --ssl_version_client=all \
    --ssl_version_server=all \
    -s /root/addons/http_handler.py
# Choices: all, secure, SSLv2, SSLv3, TLSv1, TLSv1_1, TLSv1_2
```

## 设置

```bash

https://github.com/mitmproxy/mitmproxy/tree/master/examples/contrib 
学习github上开源的插件技能后续的功能开发。
```

## web全被动扫描器。自动试探和收录。
