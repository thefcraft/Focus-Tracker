import socket
import threading
import ssl
import select
import logging
from OpenSSL import crypto
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8080
BUFFER_SIZE = 8192

class CertificateAuthority:
    def __init__(self):
        # Create a CA key pair
        self.ca_key = crypto.PKey()
        self.ca_key.generate_key(crypto.TYPE_RSA, 2048)

        # Create a CA certificate
        self.ca_cert = crypto.X509()
        self.ca_cert.get_subject().CN = "MITM Proxy CA"
        self.ca_cert.set_serial_number(1000)
        self.ca_cert.gmtime_adj_notBefore(0)
        self.ca_cert.gmtime_adj_notAfter(315360000)  # Valid for 10 years
        self.ca_cert.set_issuer(self.ca_cert.get_subject())
        self.ca_cert.set_pubkey(self.ca_key)
        self.ca_cert.sign(self.ca_key, 'sha256')

        # Save CA certificate to file
        with open("ca_cert.pem", "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.ca_cert))

    def generate_cert(self, hostname):
        # Create a key pair for the fake certificate
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        # Create a certificate
        cert = crypto.X509()
        cert.get_subject().CN = hostname
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(31536000)  # Valid for 1 year
        cert.set_issuer(self.ca_cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(self.ca_key, 'sha256')

        # Create temporary files for the certificate and key
        cert_file = tempfile.NamedTemporaryFile(delete=False)
        key_file = tempfile.NamedTemporaryFile(delete=False)

        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        cert_file.close()
        key_file.close()

        return cert_file.name, key_file.name

class MITMProxy:
    def __init__(self):
        self.ca = CertificateAuthority()
        self.cert_cache = {}

    def create_ssl_context(self, hostname):
        if hostname not in self.cert_cache:
            cert_file, key_file = self.ca.generate_cert(hostname)
            self.cert_cache[hostname] = (cert_file, key_file)
        else:
            cert_file, key_file = self.cert_cache[hostname]

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        return context

    def create_connection(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            ssl_sock.connect((host, port))
            return ssl_sock
        except Exception as e:
            logger.error(f"Failed to connect to {host}:{port} - {e}")
            return None

    def handle_ssl_tunnel(self, client_socket, host, port):
        try:
            # Connect to the remote server with SSL
            remote_socket = self.create_connection(host, port)
            if not remote_socket:
                client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                return

            # Create SSL context for the client connection
            context = self.create_ssl_context(host)
            
            # Send success response for the CONNECT request
            client_socket.send(b'HTTP/1.1 200 Connection established\r\n\r\n')
            
            # Wrap client socket with SSL
            client_ssl = context.wrap_socket(client_socket, server_side=True)
            
            # Start tunneling data
            self.tunnel(client_ssl, remote_socket)
        except Exception as e:
            logger.error(f"Error in SSL tunnel: {e}")

    def tunnel(self, client_socket, remote_socket):
        try:
            while True:
                # Handle client -> remote
                try:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    logger.info(f"Client -> Remote: {data[:100]}")  # Log first 100 bytes
                    remote_socket.send(data)
                except ssl.SSLWantReadError:
                    pass

                # Handle remote -> client
                try:
                    data = remote_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    logger.info(f"Remote -> Client: {data[:100]}")  # Log first 100 bytes
                    client_socket.send(data)
                except ssl.SSLWantReadError:
                    pass
        finally:
            client_socket.close()
            remote_socket.close()

    def handle_client(self, client_socket):
        try:
            # Receive client request
            request = client_socket.recv(BUFFER_SIZE)
            if not request:
                return

            # Parse request
            first_line = request.split(b'\r\n')[0].decode('utf-8')
            method, url, version = first_line.split(' ')
            
            # Extract host and port
            if method == 'CONNECT':
                host, port = url.split(':')
                port = int(port)
                self.handle_ssl_tunnel(client_socket, host, port)
            else:
                # Handle non-SSL requests if needed
                pass
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((PROXY_HOST, PROXY_PORT))
            server_socket.listen(100)
            logger.info(f"MITM Proxy running on {PROXY_HOST}:{PROXY_PORT}")
            logger.info("CA certificate generated: ca_cert.pem")
            
            while True:
                client_socket, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            logger.error(f"Error in proxy server: {e}")
        finally:
            server_socket.close()

if __name__ == '__main__':
    proxy = MITMProxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        logger.info("Proxy server stopped")
    finally:
        # Cleanup temporary certificate files
        for cert_file, key_file in proxy.cert_cache.values():
            try:
                os.unlink(cert_file)
                os.unlink(key_file)
            except:
                pass