import csv
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Đường dẫn tĩnh tới file LOC_A101.csv
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'source_erp', 'LOC_A101.csv')

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Trả về status 200 OK
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        data = []
        try:
            # Đọc file CSV
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader) # Bỏ qua header: CID, CNTRY
                for row in reader:
                    if len(row) >= 2:
                        # Cấu trúc API trả về: [{"cid": "...", "cntry": "..."}]
                        data.append({
                            "cid": row[0],
                            "cntry": row[1]
                        })
        except Exception as e:
            data = {"error": str(e)}
            
        # Xuất JSON ra trình duyệt (hoặc SSIS)
        self.wfile.write(json.dumps(data).encode('utf-8'))

if __name__ == '__main__':
    port = 8099
    server = HTTPServer(('localhost', port), SimpleAPIHandler)
    print(f"[OK] Mock API for Logistics Location is running!")
    print(f"URL: http://localhost:{port}/")
    print(f"Press Ctrl+C to stop.")
    server.serve_forever()
