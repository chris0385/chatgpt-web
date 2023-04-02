import http.server
import ssl
import http.client


HOST = "api.openai.com"
PORT = 5174
#PORT = 5176
TOKEN="YOUR TOKEN HERE"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        self.send_response(200)
        self.end_headers()
        self.connection = ssl.wrap_socket(self.connection, server_side=True)

    def intercept(self):
        # Parse the incoming request headers
        headers = self.headers
        auth_header = headers.get('Authorization')
        # Modify the Authorization header
        if auth_header:
            new_auth_header = 'Bearer '+TOKEN
            headers.replace_header('Authorization', new_auth_header)
        headers.replace_header('Host', HOST)
        del headers['Accept-Encoding']

    def do_GET(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('GET')
        self.write_response(response)


    def do_POST(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('POST')
        self.write_response(response)

    def do_PUT(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('PUT')
        self.write_response(response)

    def do_DELETE(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('DELETE')
        self.write_response(response)

    def do_OPTIONS(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('OPTIONS')
        self.write_response(response)

    def do_HEAD(self):
        self.intercept()
        # Forward the modified request to the target server
        response = self.proxy_request('HEAD')
        self.write_response(response)

    def write_response(self, response):
        # Send the modified response back to the original client
        self.send_response(response.status)

        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        print("== RESPONSE")
        for header, value in response.getheaders():
            if header.lower().startswith('access-control-allow-'):
                continue
            print(header,":", value)
            self.send_header(header, value)
        self.end_headers()
        body = response.read()
        self.wfile.write(body)
        print(body)
        response.close()

    def get_request_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(content_length)

    def proxy_request(self, method):
        # Forward the request to the target server
        # and receive the response
        # ...
        conn = http.client.HTTPSConnection(HOST, timeout=30)
        print("== REQUEST:", method, self.path, self.headers)
        body = self.get_request_body()
        conn.request(method, self.path, body=body, headers=self.headers)
        response = conn.getresponse()
        # Optionally modify the response
        return response

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, ProxyHandler)
    httpd.serve_forever()