# coding:utf-8
from uuid import uuid4
from http_helper.content_type import get_suffix
from http_helper.filestore import filestore


def bytes2str(b_data):
    """
    bytes to str 将bytes类型强制转化为utf-8字符串
    :param b_data:
    :return:
    """
    if type(b_data) in (tuple, list):
        return [bytes2str(x) for x in b_data]
    return str(b_data, encoding='utf-8') if type(b_data) == bytes else b_data


def force_parse2str(content, headers, host, flow_id=None):
    """
    强行转化 请求体或者响应体，如果强行转化失败，那么就存储为二进制进行文件提取传输。
    :param content:
    :param headers:
    :param host:
    :param flow_id:
    :return:
    """
    try:
        # TODO 这里限制最多保存2048个字节。
        return bytes2str(content)[0:2048]
    except:
        # TODO 强行转化为字符串失败后进行文件提取。
        _local_type = headers['Content-Type'] if 'Content-Type' in headers.keys() else ''
        _suffix = get_suffix(_local_type)
        _filename = filestore(content, str(host), date=None, suffix=_suffix)
        return str(_filename)


def push_header_todict(flow_headers):
    """
    将请求头或者响应头中的字段格式化我们需要的字典类型，并且和zeek字段进行串接。
    :param flow_headers:
    :return:
    """
    _names = list(flow_headers)
    _values = [flow_headers[x] for x in _names]
    return {_names[i]: _values[i] for i in range(len(_names))}


def parse_tls(flow):
    """
    将https或者http的连接信息转化下
    # TODO https://github.com/mitmproxy/mitmproxy/blob/b6e8c83a08313f8340efdc44ae52f6b5f9e200bd/mitmproxy/connections.py#L15
    :param flow: 就是web流量
    :return:
    """
    client_conn = flow.client_conn
    server_conn = flow.server_conn
    _client_conn = dict(
            id=bytes2str(client_conn.id),
            address=bytes2str(client_conn.address),
            # clientcert=bytes2str(client_conn.clientcert),
            # mitmcert=bytes2str(client_conn.mitmcert),
            tls_established=bytes2str(client_conn.tls_established),
            timestamp_start=bytes2str(client_conn.timestamp_start),
            timestamp_end=bytes2str(client_conn.timestamp_end),
            timestamp_tls_setup=bytes2str(client_conn.timestamp_tls_setup),
            sni=bytes2str(client_conn.sni),
            cipher_name=bytes2str(client_conn.cipher_name),
            alpn_proto_negotiated=bytes2str(client_conn.alpn_proto_negotiated),
            tls_version=bytes2str(client_conn.tls_version),
            # tls_extensions=bytes2str(client_conn.tls_extensions),
        )

    _server_conn = (dict(
            id=bytes2str(server_conn.id),
            address=bytes2str(server_conn.address),
            ip_address=bytes2str(server_conn.ip_address),
            # cert=bytes2str(server_conn.cert),
            sni=bytes2str(server_conn.sni),
            alpn_proto_negotiated=bytes2str(server_conn.alpn_proto_negotiated),
            tls_version=bytes2str(server_conn.tls_version),
            source_address=bytes2str(server_conn.source_address),
            tls_established=bytes2str(server_conn.tls_established),
            timestamp_start=bytes2str(server_conn.timestamp_start),
            timestamp_tcp_setup=bytes2str(server_conn.timestamp_tcp_setup),
            timestamp_tls_setup=bytes2str(server_conn.timestamp_tls_setup),
            timestamp_end=bytes2str(server_conn.timestamp_end),
            via=bytes2str(server_conn.via)
        ))
    # TODO 将重要的连接信息剥离出来
    remote_ip, remote_port = _client_conn['address']
    server_ip, server_port = _server_conn['ip_address']
    return dict(
        c_conn=_client_conn,
        s_conn=_server_conn,
        remote_ip=remote_ip,
        remote_port=remote_port,
        server_ip=server_ip,
        server_port=server_port
    )


def parse_http(flow):
    flow_id = str(uuid4())
    intercepted = flow.intercepted
    # error_info = str(flow.error)

    request = flow.request
    host = request.host
    server_port = request.port
    path = request.path
    method = bytes2str(request.method)
    scheme = bytes2str(request.scheme)
    authority = bytes2str(request.authority)
    http_version = bytes2str(request.http_version)
    request_start_ts = request.timestamp_start
    request_end_ts = request.timestamp_end
    upload_time = request_end_ts - request_start_ts
    request_headers = push_header_todict(request.headers)
    request_body = force_parse2str(request.content, request_headers, host, flow_id)

    response = flow.response
    status_code = response.status_code
    response_reson = response.reason
    response_start_ts = response.timestamp_start
    response_end_ts = response.timestamp_end
    response_timedelta = response_end_ts - response_start_ts
    response_headers = push_header_todict(response.headers)
    response_body = force_parse2str(response.content, response_headers, host, flow_id)

    try:
        _trailers = dict(
            request_trailers=bytes2str(request.trailers),
            response_trailers=bytes2str(response.trailers)
        )
    except:
        # from opssdk.xlog import logging
        _trailers = dict(
            request_trailers=None,
            response_trailers=None
        )
        print(request.trailers)

    # TODO 补充，专门为请求头和响应头增加raw
    request_header_raw = "{request_method} {request_url} {http_version}\r\n{request_headers}\r\n\r\n{request_body}\r\n".format(
        request_method=method, request_url=path, http_version=http_version,
        request_headers='\r\n'.join(["{k}:{v}".format(k="-".join([y.capitalize() for y in x[0].split('-')]),
                                                      v=x[1]) for x in request_headers.items()]),
        request_body=request_body
    )

    response_header_raw = "{request_method} {request_url} {status_code}\r\n{response_headers}\r\n\r\n{response_body}".format(
        request_method=method,
        request_url=path,
        status_code=status_code,
        response_headers='\r\n'.join(["{k}:{v}".format(k="-".join([y.capitalize() for y in x[0].split('-')]),
                                                       v=x[1]) for x in response_headers.items()]),
        response_body=response_body
    )

    _message = dict(
        flow_id=flow_id,
        flow_time=request_start_ts,
        server_time=response_start_ts,
        request_headers=request_headers,
        response_headers=response_headers,
        request_header_raw=request_header_raw,
        response_header_raw=response_header_raw,
        host=host,
        port=server_port,
        request_body=request_body,
        response_body=response_body,
        upload_time=upload_time,
        response_time=response_timedelta,
        response_reson=response_reson,
        scheme=scheme,
        authority=authority,
        intercepted=intercepted,
        # error_info=error_info,
        # TODO 2020-9-1 增加了连接信息
        **parse_tls(flow)
    )

    return _message
