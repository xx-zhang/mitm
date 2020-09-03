# 插件开发和使用


- [插件大全](https://github.com/mitmproxy/mitmproxy/blob/master/examples)

## 使用教程
```bash

/usr/local/bin/mitmproxy  --listen-port 63333  \
    --listen-host 0.0.0.0  \
    -s /root/addons/http_handler.py

# 开始记录并且阻断http类型日志

```
## 请求字段的格式化参考

-  https://github.com/mitmproxy/mitmproxy/blob/master/mitmproxy/http.py
-  参考 https://github.com/mitmproxy/mitmproxy/blob/master/mitmproxy/net/http/response.py
-  conn 信息参考 https://github.com/mitmproxy/mitmproxy/blob/master/mitmproxy/connections.py