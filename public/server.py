from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import webbrowser
from pathlib import Path
import sys
import json
import os
import mimetypes

class ReportRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, report_path=None, **kwargs):
        self.report_path = report_path
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def do_GET(self):
        if self.path.endswith('report.json'):
            try:
                with open(self.report_path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(f.read())
                return
            except Exception as e:
                print(f"Error reading report file: {str(e)}")
                self.send_error(500, f"Error reading report file: {str(e)}")
                return

        if self.path == '/':
            self.path = '/design1.html'

        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            relative_path = self.path.lstrip('/')
            file_path = os.path.join(current_dir, relative_path)

            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                self.send_error(404, "File not found")
                return

            file_type, _ = mimetypes.guess_type(file_path)
            if file_type is None:
                file_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-type', file_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
            return

        except Exception as e:
            print(f"Error serving file: {str(e)}")
            self.send_error(500, f"Error serving file: {str(e)}")
            return

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server(report_path, port=8000):
    try:
        report_file = os.path.abspath(report_path)
        if not os.path.exists(report_file):
            print(f"Error: Report file not found: {report_file}")
            sys.exit(1)

        handler = lambda *args, **kwargs: ReportRequestHandler(*args, report_path=report_file, **kwargs)
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Server running at http://localhost:{port}/")
            print(f"Serving report: {report_path}")
            webbrowser.open(f'http://localhost:{port}/')
            httpd.serve_forever()

    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Port {port} is in use, trying port {port + 1}")
            run_server(report_path, port + 1)
        else:
            raise e
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <report_path>")
        sys.exit(1)
    
    report_path = sys.argv[1]
    print(f"Report : {report_path}")
    run_server(report_path) 