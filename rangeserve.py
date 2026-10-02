"""给 SimpleHTTPRequestHandler 加上 Range(分段读取)支持。
Safari / iOS 播放本地音视频必须用它; 否则只能整文件返回, 会播放失败或无法拖动进度条。"""
import os
import re


class RangeMixin:
    def serve_static(self):
        path = self.translate_path(self.path.split("?", 1)[0])
        rng = self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)$", rng or "")
        if not (m and os.path.isfile(path)):
            return super().do_GET()
        size = os.path.getsize(path)
        a, b = m.groups()
        if a == "" and b == "":
            return super().do_GET()
        if a == "":
            start, end = max(0, size - int(b)), size - 1
        else:
            start, end = int(a), (int(b) if b else size - 1)
        end = min(end, size - 1)
        if start >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
