FROM alpine:3.10

MAINTAINER xx-zhang <actanble@gmail.com>

RUN echo "https://mirrors.aliyun.com/alpine/v3.10/main/" > /etc/apk/repositories \
        && apk update \
        && apk add tzdata \
        && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ENV HUGO_VERSION=0.23
ENV HUGO_SITE=/srv/hugo
ENV HUGO_URL=https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_Linux-64bit.tar.gz

ADD ${HUGO_URL} /tmp/

RUN tar -xzf /tmp/*.tar.gz -C /tmp \
    && mv /tmp/hugo /usr/local/bin/ \
    && rm -rf /tmp/*

WORKDIR ${HUGO_SITE}
VOLUME ${HUGO_SITE}

FRPM

EXPOSE 1313
CMD ["hugo", "server", "--bind", "0.0.0.0"]