import sys
import socket
import threading # for multiple clients
import logging
import select
from colorama import Fore, Style, init

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8080
BUFFER_SIZE = 8192


# Initialize colorama
init(autoreset=True)

# Filter for printable characters
HEX_FILTER = ''.join(
    [((len(repr(chr(i))) == 3) and chr(i)) or '.' for i in range(256)]
)

def hexdump(src, length=24):
    if isinstance(src, bytes):
        src = src.decode(errors='ignore')  # Handle non-decodable bytes
    results = []
    for i in range(0, len(src), length):
        word = src[i:i + length]
        printable = ''.join((c if c in HEX_FILTER else '.') for c in word)  # Only printable characters
        hexa = ' '.join(f'{ord(c):02X}' for c in word)
        hexwidth = length * 3
        
        # Colorize the output
        address_color = Fore.CYAN
        hex_color = Fore.YELLOW
        printable_color = Fore.GREEN

        results.append(f'{address_color}{i:04x} {hex_color}{hexa:<{hexwidth}}\t{printable_color}{printable}')

    for line in results:
        print(line)

def create_connection(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        return sock
    except Exception as e:
        logger.error(f"Failed to connect to {host}:{port} - {e}")
        return None

def handle_https_tunnel(client_socket, host, port):
    try:
        # Create connection to remote server
        remote_socket = create_connection(host, port)
        if remote_socket is None:
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            return
        
        # Send success response to client
        client_socket.send(b'HTTP/1.1 200 Connection established\r\n\r\n')
        
        # Start bidirectional tunnel
        tunnel(client_socket, remote_socket)
    except Exception as e:
        logger.error(f"Error in HTTPS tunnel: {e}")
        try:
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        except:
            pass

def tunnel(client_socket, remote_socket):
    try:
        inputs = [client_socket, remote_socket]
        while inputs:
            readable, _, exceptional = select.select(inputs, [], inputs, 10)
            
            if exceptional:
                break
                
            for sock in readable:
                other = remote_socket if sock is client_socket else client_socket
                try:
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        return
                    other.send(data)
                except:
                    return
    finally:
        client_socket.close()
        remote_socket.close()

def handle_http_request(client_socket, request, host, port):
    try:
        # Create connection to remote server
        remote_socket = create_connection(host, port)
        if remote_socket is None:
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            return
        
        # Forward the request and get response
        remote_socket.send(request)
        tunnel(client_socket, remote_socket)
    except Exception as e:
        logger.error(f"Error in HTTP request: {e}")
        try:
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        except:
            pass

def extract_host_port(request_line, headers):
    try:
        # First try to get host from request line
        _, url, _ = request_line.split(' ')
        
        if url.startswith('http://'):
            url = url[7:]
        elif url.startswith('https://'):
            url = url[8:]
        
        host_port = url.split('/')[0]
        
        # If no port in URL, try to get host from Host header
        if ':' not in host_port:
            for header in headers:
                if header.lower().startswith('host:'):
                    host_port = header.split(' ')[1].strip()
                    break
        
        # Split host and port
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 443 if request_line.startswith('CONNECT') else 80
            
        return host, port
    except Exception as e:
        logger.error(f"Error extracting host and port: {e}")
        return None, None

def handle_client(client_socket):
    try:
        # Receive client request
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return
        
        hexdump(request)
        
        # Parse request
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0].decode('utf-8')
        headers = [line.decode('utf-8') for line in request_lines[1:] if line]
        
        # Extract host and port
        host, port = extract_host_port(request_line, headers)
        if not host:
            client_socket.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
            return
        
        logger.info(f"Request: {request_line}")
        
        # Handle HTTPS CONNECT request
        if request_line.startswith('CONNECT'):
            handle_https_tunnel(client_socket, host, port)
        else:
            handle_http_request(client_socket, request, host, port)
            
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass

def start_proxy():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((PROXY_HOST, PROXY_PORT))
        server_socket.listen(100)
        logger.info(f"Proxy server running on {PROXY_HOST}:{PROXY_PORT}")
        
        while True:
            client_socket, addr = server_socket.accept()
            logger.debug(f"Accepted connection from {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        logger.error(f"Error in proxy server: {e}")
    finally:
        server_socket.close()

if __name__ == '__main__':
    try:
        start_proxy()
    except KeyboardInterrupt:
        logger.info("Proxy server stopped")