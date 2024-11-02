import http.server
import socketserver
import os
import json
import logging
import threading

# Configuration file
CONFIG_FILE = "config.json"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_settings():
    """Load IP address and port from configuration file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                settings = json.load(file)
                ip = settings.get("ip", "localhost")
                port = settings.get("port", 8000)
                return ip, port
        except json.JSONDecodeError as e:
            logging.error(f"Error loading JSON: {e}")
            return "localhost", 8000
        except Exception as e:
            logging.error(f"An error occurred while loading settings: {e}")
            return "localhost", 8000
    else:
        logging.warning(f"{CONFIG_FILE} not found. Using default settings.")
        return "localhost", 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        """Override log_request to log using the logging module."""
        logging.info(f"Request: {self.requestline} - Status: {code} - Size: {size}")

def run_server():
    ip, port = load_settings()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory of the script

    handler = MyHttpRequestHandler
    httpd = socketserver.TCPServer((ip, port), handler)

    logging.info(f"Serving at http://{ip}:{port}")

    try:
        httpd.serve_forever()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        httpd.server_close()
        logging.info("Server closed.")

def start_server():
    """Start the web server in a new thread."""
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Allows the thread to exit when the main program exits
    server_thread.start()
    return server_thread

if __name__ == "__main__":
    start_server()
    input("Press Enter to stop the server...\n")  # Keeps the main thread alive
