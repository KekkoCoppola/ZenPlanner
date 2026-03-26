import http.server
import socketserver
import os
import sys

# Script utilitario per testare la demo WebAssembly in locale
PORT = 8000
# Ora siamo in ROOT del progetto
directory = os.path.dirname(os.path.abspath(__file__)) 

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"\n✅ Server Locale Avviato sulla Root!")
        print(f"👉 Link Test Live Demo: http://localhost:{PORT}/index.html")
        print("Premi CTRL+C per terminare.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nChiusura server...")
            sys.exit(0)
