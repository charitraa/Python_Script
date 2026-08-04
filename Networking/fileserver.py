#!/usr/bin/env python3
"""Simple LAN file server. Browse and download files/folders from any device on the same network."""
import http.server
import socketserver
import socket
import os
import sys

PORT = 5173
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s - %s\n" % (self.log_date_time_string(), self.address_string(), format % args))

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            self.log_message("client disconnected")

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def main():
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    with ThreadedTCPServer(("0.0.0.0", port), Handler) as httpd:
        ip = get_lan_ip()
        print("=" * 60)
        print(f"Serving: {DIRECTORY}")
        print(f"Local:   http://127.0.0.1:{port}/")
        print(f"LAN:     http://{ip}:{port}/")
        print("=" * 60)
        print("On another device on the same Wi-Fi/network, open the LAN URL")
        print("in a browser. Click files to download, folders to browse.")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
