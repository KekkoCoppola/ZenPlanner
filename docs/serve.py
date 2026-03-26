import http.server
import socketserver
import os
import sys

# Questo script serve solo per testare la demo in locale ed eludere i blocchi CORS del browser "file://"
PORT = 8000
# Ci assicuriamo di servire la cartella ROOT del progetto, così ../src/ etc nell'HTML funzionano regolarmente
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"\n✅ Server Locale Avviato sulla Root del repository!")
        print(f"👉 Per testare la demo WebAssembly, clicca qui: http://localhost:{PORT}/docs/")
        print("Premi CTRL+C per terminare.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nChiusura server...")
            sys.exit(0)
