#!/usr/bin/env python3
import socket
import signal
import sys
from time import sleep
import re
import json

HTML_template = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>test</title>
    </head>
    <body>
        {}
    </body>
</html>
'''

# Define the server's IP address and port
HOST = '127.0.0.1'  # IP address to bind to (localhost)
PORT = 8082         # Port to listen on
# Create a socket that uses IPv4 and TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(5)  # Backlog for multiple simultaneous connections
print(f"Server is listening on {HOST}:{PORT}")
# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)
    # Register the signal handler

with open('products.json', 'r') as fp:
    products = json.load(fp)

if not products:
    print("Couldn't load the products.json file.")
    sys.exit(0)

def render_products_page():
    html = r"List of products:</br>"
    for i, p in enumerate(products):
        html += r"<a href='/product/{}'> {} </a></br>".format(i, p['name'])

    return html

def render_product_page(i):
    p = products[int(i)]
    return r'''
    <table>
    <tr>
    <td>Name</td>
    <td>{}</td>
    </tr>

    <tr>
    <td>Author</td>
    <td>{}</td>
    </tr>

    <tr>
    <td>Price</td>
    <td>{}</td>
    </tr>

    <tr>
    <td>Description</td>
    <td>{}</td>
    </tr>
    <table>
    '''.format(p['name'], p['author'], p['price'], p['description'])


signal.signal(signal.SIGINT, signal_handler)
# Function to handle client requests
def handle_request(client_socket):
    # Receive and print the client's request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")
    # Parse the request to get the HTTP method and path
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]
    # Initialize the response content and status code
    response_content = ''
    status_code = 200

    # Define a simple routing mechanism
    if path == '/home':
        response_content = 'Home page.'
    elif path == '/about':
        response_content = 'About page.'
    elif path == '/contacts':
        response_content = 'Contacts page.'
    elif path == '/products':
        response_content = render_products_page()
    elif re.compile(r"/product/\d+").fullmatch(path):
        print(path)
        i = path.split('/')[-1]
        response_content = render_product_page(i)

    else:
        response_content = '404 Not Found'
        status_code = 404

    # Prepare the HTTP response
    response = f"HTTP/1.0 {status_code} OK\r\nContent-type:text/html;charset=utf8\r\n\r\n{HTML_template.format(response_content)}"
    client_socket.send(response.encode('utf-8'))
    # Close the client socket
    client_socket.close()

while True:
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    try:
        # Handle the client's request in a separate thread
        handle_request(client_socket)
    except KeyboardInterrupt:
        # Handle Ctrl+C interruption here (if needed)
        pass
