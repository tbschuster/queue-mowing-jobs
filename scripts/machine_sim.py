#!/usr/bin/env python3

# This is a simple implementation of a machine in the field. The main purpose
# is to simulate a machine that can receive tasks and complete them. Simulator
# also supports pause/resume and does send back events and telemetry to backend.

# The payload of the telemetry can be modified as you see fit. Same with the
# structure on incoming commands.

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import threading
import time
from urllib import request, error

logging.basicConfig(level=logging.INFO)

# Feel free to change MACHINE_ID as needed
MACHINE_ID = "f2e5e2cd-7e76-4dbd-92eb-057986bff93e"

class MachineSimulator:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.state = "Idle"
        self.current_field = None
        self.current_eta = 0 # time in seconds until complete
        # start update thread
        threading.Thread(target=self._post_update).start()
    
    def start_mowing(self, field_id):
        self.state = "Mowing"
        self.current_field = field_id
        self.current_eta = 30 # seconds job will take
        threading.Thread(target=self._simulate_mowing, args=(field_id,)).start()

    def stop_mowing(self):
        self.state = "Idle"
        self.current_eta = 0 # time in seconds until complete
    
    def _simulate_mowing(self, field_id):
        while True:
            if self.state == "Paused":
                print(f"Machine {self.machine_id} paused mowing field {field_id}, ETA: {self.current_eta}")
                time.sleep(1)
                continue
            elif self.state == "Idle":
                print(f"Machine moving to Idle")
                break
            elif self.state == "Mowing":
                print(f"Machine {self.machine_id} mowing field {field_id}, ETA: {self.current_eta}s")
                self.current_eta = self.current_eta - 1

                if self.current_eta < 0:
                    print(f"Machine {self.machine_id} finished mowing field {field_id}")
                    self.current_eta = 0
                    self.state = "Idle"
                    self.current_field = None
                    break
                else:
                    time.sleep(1)
                    continue
    
    def pause(self):
        self.state = "Paused"
    
    def resume(self):
        self.state = "Mowing" if self.current_field else "Idle"
    
    def get_status(self):
        return {
            "machine_id": self.machine_id,
            "state": self.state,
            "current_field": self.current_field
        }

    def _post_update(self):
        while True:
            time.sleep(2)

            try:
                payload = {
                    "state": self.state,
                    "current_field": "" if self.current_field is None else self.current_field,
                    "timestamp": time.time()
                }

                # Convert payload to JSON bytes
                json_data = json.dumps(payload).encode('utf-8')

                # Create request
                url = f"http://127.0.0.1:8000/api/v1/machines/{self.machine_id}/incoming_machine_telem"
                req = request.Request(
                    url,
                    data=json_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                # Send request
                with request.urlopen(req, timeout=5) as response:
                    print(f"Update telem to backend, payload: {json_data}")
                    response_data = response.read().decode('utf-8')
        
            except error.HTTPError as e:
                print(f"[Machine {self.machine_id}] HTTP Error {e.code}: {e.reason}")
            except error.URLError as e:
                print(f"[Machine {self.machine_id}] URL Error: {e.reason}")
            except Exception as e:
                print(f"[Machine {self.machine_id}] Failed to contact backend: {e}")
        

machine = MachineSimulator(machine_id=MACHINE_ID)

class MachineRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == '/status':
            self._send_json(machine.get_status())
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == '/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            command = data.get('command')
            
            if command == 'start_mowing':
                field_id = data.get('field_id')
                machine.start_mowing(field_id)
                self._send_json({"status": "success", "state": machine.state})

            elif command == 'stop':
                machine.stop_mowing()
                self._send_json({"status": "success", "state": machine.state})
            
            elif command == 'pause':
                machine.pause()
                self._send_json({"status": "success", "state": machine.state})
            
            elif command == 'resume':
                machine.resume()
                self._send_json({"status": "success", "state": machine.state})
            
            else:
                self._send_json({"error": "Unknown command"}, 400)
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        print(f"[Machine {machine.machine_id}] {format % args}")

def run_server(port=5001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MachineRequestHandler)
    print(f"Machine simulator running on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server(port=5001)