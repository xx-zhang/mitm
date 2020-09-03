# coding:utf-8
import io
import asyncio
import aiohttp
import time


class AsyncFile:

    class _ReadContent:
        """
        缓存读取的数据
        read 在子线程中进行
        用 _ReadContent().content 存储返回值
        """

        def __init__(self, content=None):
            self.content = content

    def __init__(self, path: str, open_flag: str = "r", executor=None):
        self.path = path
        self.open_flag = open_flag
        self._f = open(path, open_flag)
        self._loop = asyncio.get_event_loop()
        self._rw_lock = asyncio.Lock()
        self._executor = executor

    def _read(self, r_content: _ReadContent, over_semaphore: asyncio.Semaphore):
        r_content.content = self._f.read()
        over_semaphore.release()

    def _write(self, content, over_semaphore: asyncio.Semaphore):
        self._f.write(content)
        over_semaphore.release()

    async def read(self):
        if not self._f.readable():
            raise io.UnsupportedOperation()
        async with self._rw_lock:
            over_semaphore = asyncio.Semaphore(0)
            _read_content = self._ReadContent()
            self._loop.run_in_executor(self._executor , self._read, _read_content, over_semaphore)
            await over_semaphore.acquire()
            return _read_content.content

    async def write(self, content):
        if not self._f.writable():
            raise io.UnsupportedOperation()
        async with self._rw_lock:
            over_semaphore = asyncio.Semaphore(0)
            self._loop.run_in_executor(self._executor , self._write, content, over_semaphore)
            await over_semaphore.acquire()

    async def seek(self, offset, where=0):
        async with self._rw_lock:
            self._f.seek(offset, where)

    async def close(self):
        async with self._rw_lock:
            self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        try:
            self._f.close()
        finally:
            pass


async def get(session, url, timeout=60):
    async with session.request('GET', url, timeout=timeout) as resp:
        return await resp.read()


async def crawl(url, save_path, executor=None):
    async with aiohttp.ClientSession() as session:
        content = await get(session, url)
    if content:
        with AsyncFile(save_path, "wb", executor) as f:
            await f.write(content)


def spyder_demo():
    import os
    from concurrent.futures import ThreadPoolExecutor
    d = "./_test_imgs/"
    if not os.path.exists(d):
        os.makedirs(d)
    url="https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1551437241785&di=a827c7962549b54e2d4a84327902bf54&imgtype=0&src=http%3A%2F%2Fwww.baijingapp.com%2Fuploads%2Fcompany%2F03%2F36361%2F20170413%2F1492072091_pic_real.jpg"
    save_path = os.path.join(d, "tmp{}.jpg")
    executor=ThreadPoolExecutor(max_workers=8)
    tasks = []
    for i in range(20):
        tasks.append(crawl(url,save_path.format(i),executor))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    print("over")


if __name__=="__main__":
    pass

