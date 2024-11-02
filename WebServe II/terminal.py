import tkinter as tk
import subprocess
import os
import signal
import json
import logging

class Terminal:
    CONFIG_FILE = "config.json"  # Configuration file to store IP and port

    def __init__(self, master):
        self.master = master
        self.master.title("Terminal")
        self.output_text = tk.Text(self.master, wrap="word", state="disabled")
        self.output_text.pack(expand=True, fill="both")
        self.input_entry = tk.Entry(self.master)
        self.input_entry.pack(side="bottom", fill="x")
        self.input_entry.bind("<Return>", self.handle_input)
        self.output_text.tag_configure("prompt", foreground="blue")
        self.print_prompt()

        self.webserver_process = None  # Attribute to keep track of the web server process
        self.webserver_ip, self.webserver_port = self.load_settings()

        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_settings(self):
        """Load IP and port from configuration file or use defaults."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as file:
                    settings = json.load(file)
                    return settings.get("ip", "localhost"), settings.get("port", 8000)
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                return "localhost", 8000
        else:
            logging.warning(f"{self.CONFIG_FILE} not found. Using default settings.")
            return "localhost", 8000

    def save_settings(self):
        """Save IP and port to configuration file."""
        settings = {
            "ip": self.webserver_ip,
            "port": self.webserver_port
        }
        with open(self.CONFIG_FILE, "w") as file:
            json.dump(settings, file)

    def handle_input(self, event):
        command = self.input_entry.get()
        self.print_command(command)
        self.input_entry.delete(0, "end")
        self.execute_command(command)

    def print_prompt(self):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", ">> ", "prompt")
        self.output_text.configure(state="disabled")

    def print_command(self, command):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{command}\n")
        self.output_text.configure(state="disabled")

    def execute_command(self, command):
        command = command.lower()
        if command.startswith("--webserver change ip"):
            self.change_webserver_ip(command)
        elif command.startswith("--webserver port"):
            self.change_webserver_port(command)
        elif command == "help":
            self.print_help()
        elif command == "exit":
            self.master.destroy()
        elif command == "--webserver start":
            self.start_webserver()
        elif command == "--webserver stop":
            self.stop_webserver()
        elif command == "--webserver ip address":
            self.show_webserver_ip()
        else:
            self.print_output(f"Command '{command}' not recognized")

    def change_webserver_ip(self, command):
        parts = command.split()
        if len(parts) == 4:
            new_ip = parts[3].strip('"')
            self.webserver_ip = new_ip
            self.save_settings()
            self.print_output(f"Web server IP address changed to {self.webserver_ip}")
        else:
            self.print_output("Invalid command format. Use: --webserver change ip \"new_ip_address\"")

    def change_webserver_port(self, command):
        parts = command.split()
        if len(parts) == 3 and parts[2].isdigit():
            self.webserver_port = int(parts[2])
            self.save_settings()
            self.print_output(f"Web server port changed to {self.webserver_port}")
        else:
            self.print_output("Invalid command format. Use: --webserver port new_port")

    def print_help(self):
        help_text = (
            "Available commands:\n"
            "- help: Show available commands\n"
            "- exit: Close the terminal\n"
            "- --webserver start: Run webserver.py\n"
            "- --webserver stop: Stop the webserver.py\n"
            "- --webserver ip address: Show the IP address and port of the web server\n"
            "- --webserver change ip \"ip address\": Change the IP address of the web server\n"
            "- --webserver port new_port: Change the port of the web server\n"
        )
        self.print_output(help_text)

    def start_webserver(self):
        if self.webserver_process is None or self.webserver_process.poll() is not None:
            try:
                # Start the web server in a new thread
                self.webserver_process = subprocess.Popen(["python", "webserver.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.print_output(f"Web server started successfully at {self.webserver_ip}:{self.webserver_port}.")
            except Exception as e:
                self.print_output(f"Error starting web server: {e}")
                logging.error(f"Error starting web server: {e}")
        else:
            self.print_output("Web server is already running.")

    def stop_webserver(self):
        if self.webserver_process and self.webserver_process.poll() is None:
            self.webserver_process.terminate()  # Use terminate for graceful shutdown
            self.webserver_process = None
            self.print_output("Web server stopped successfully.")
        else:
            self.print_output("No web server is running.")

    def show_webserver_ip(self):
        self.print_output(f"Web server is running at {self.webserver_ip}:{self.webserver_port}")

    def print_output(self, output):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{output}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
        self.print_prompt()

def main():
    root = tk.Tk()
    app = Terminal(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_webserver)  # Ensure web server stops on close
    root.mainloop()

if __name__ == "__main__":
    main()
