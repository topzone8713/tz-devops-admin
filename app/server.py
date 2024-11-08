from http.server import HTTPServer
import argparse
import http.server
import base64
import logging
from controller import Controller
import os
from jproperties import Properties

configs = Properties()
filePath = '.env'
if not os.path.isfile(filePath):
    filePath = '../.env'
with open(filePath, 'rb') as f:
    configs.load(f)
env = configs.properties

auth_realm = env.get('auth_realm')
auth_users = {
    env.get('user'): env.get('password'),
    env.get('dev'): env.get('dev_password'),
}

APP_VERSION = '0.2'
# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')


class AuthHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    controller = Controller()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(AuthHTTPRequestHandler, self).end_headers()

    def do_GET(self):
        # and self.server.server_address[0] != '0.0.0.0'
        # if self.path != '/health':
        #     username = self.authenticate()
        #     if username is None:
        #         return
        #     self.username = username
        self.controller.do_GET(self)

    def do_POST(self):
        self.controller.do_POST(self)

    def authenticate(self):
        auth_header = self.headers.get('Authorization')
        if auth_header is None:
            self.send_response(401)
            self.send_header('WWW-Authenticate', f'Basic realm="{auth_realm}"')
            self.end_headers()
            return None

        auth_type, auth_payload = auth_header.split()
        if auth_type != 'Basic':
            return None

        try:
            username, password = base64.b64decode(auth_payload).decode('utf-8').split(':')
        except:
            return None

        if username not in auth_users or password != auth_users[username]:
            self.send_response(401)
            self.send_header('WWW-Authenticate', f'Basic realm="{auth_realm}"')
            self.end_headers()
            return None

        return username


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="0.0.0.0",  # localhost
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()

    server = http.server.HTTPServer((args.listen, args.port), AuthHTTPRequestHandler)
    print('server running on port {0}'.format(args.port))
    server.serve_forever()
