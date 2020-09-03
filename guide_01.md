# 使用和其他补充。


## 为了测试 TLSv1，TLSv1_1，TLSv1_2

```bash
ssl_dir=/etc/ssl/certs && \
    mkdir -p $ssl_dir &&  \
    openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -subj "/C=CN/ST=HB/L=WH/O=actanble/OU=dev/CN=tb245@encrypt.tsc.com/emailAddress=actanble@gmail.com" \
    -keyout $ssl_dir/nginx.key \
    -out $ssl_dir/nginx.crt
```
### Nginx 使用加密的内容
- [公网安全https + tlsv3](http://www.manongjc.com/detail/13-kmdylkxklgeezoc.html)
```

```