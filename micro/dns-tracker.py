from dnslib import DNSRecord, QTYPE, RR, A, DNSHeader
import dns.resolver
import socket
import socketserver

# Get the local IP address
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

# DNS server configuration
DOMAIN_TO_IP = {
    'notporn.com.': "142.250.77.174",
    'b.com.': local_ip,
}

class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        try:
            request = DNSRecord.parse(data)
            print(f"Received request for: {str(request.q.qname)}")

            qname = str(request.q.qname)
            # qtype = QTYPE[request.q.qtype]    
            
            
            # Create a DNS response with the same ID and the appropriate flags
            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
            
            if qname in DOMAIN_TO_IP:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(DOMAIN_TO_IP[qname])))
                print(f"Resolved {qname} to {DOMAIN_TO_IP[qname]}")
            else:
                print(f"No record found for {qname}. Forwarding to default DNS.")
                # Forward the query to the default DNS
                answer = self.forward_query(data)
                if answer: reply = answer

            socket.sendto(reply.pack(), self.client_address)
        except Exception as e:
            print(f"Error handling request: {e}")
            
    def forward_query(self, data):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']  # Google Public DNS

        try:
            # Forward the query to the external DNS
            request = DNSRecord.parse(data)
            response = resolver.resolve(str(request.q.qname), request.q.qtype)
            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

            for rdata in response:
                reply.add_answer(RR(str(request.q.qname), QTYPE.A, rdata=A(rdata.address)))

            return reply
        except Exception as e:
            print(f"Error forwarding query: {e}")
            return None

if __name__ == "__main__":
    server = socketserver.UDPServer(("0.0.0.0", 53), DNSHandler)
    print("DNS Server is running...")
    server.serve_forever()