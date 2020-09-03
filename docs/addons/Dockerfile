FROM alpine:latest

MAINTAINER xx-zhang <actanble@gmail.com>
WORKDIR /usr/src/app
ENV ADDON_PATH /mitm/addons

# 设置alpine的镜像地址为阿里云的地址
RUN wget -qO  /get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    echo "https://mirrors.aliyun.com/alpine/v3.10/main/" > /etc/apk/repositories \
        && apk update \
        && apk add tzdata \
        && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
        && apk add --no-cache bash \
            libxml2-dev  libffi libxml2 libxslt libxslt-dev libjpeg-turbo-dev \
            python3 gcc g++ python3-dev linux-headers libffi-dev openssl-dev \
        && python3 /get-pip.py \
        && cd .. \
        && rm -f /get-pip.py \
        && rm -rf /var/cache/apk/*
# TODO alibevent-dev 没有所以被删除了, NOTE 这里

# TODO 生产环境中不要把镜像放到开源的镜像，而是推荐自己映射。

RUN git clone https://github.com/mitmproxy/mitmproxy && \
    cd mitmproxy && pip3 install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    python3 setup.py install && cd .. && rm -rf .

# TODO 安装插件依赖的包
ADD . /mitm/addons
RUN pip3 install /mitm/addons/requirements.txt

VOLUME /usr/src/app/
VOLUME /mitm/addons

USER root

CMD ['/usr/local/bin/mitmproxy  \
    --listen-port 63333  \
    --listen-host 0.0.0.0  \
    -k \
    -s /root/addons/http_handler.py']
