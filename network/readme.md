# 网络设置以及代理

- [透明代理](https://docs.mitmproxy.org/stable/howto-transparent/)

## 内核修改
- `/etc/sysctl.conf`
```bash 
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1

sysctl -w net.ipv4.conf.all.send_redirects=0
```
## iptables 设置 
```bash 
# 本地访问的目的端口进行重定向。
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080
ip6tables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
ip6tables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080
```

## 运行
- 

## 参考 