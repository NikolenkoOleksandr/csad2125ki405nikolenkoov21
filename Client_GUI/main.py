import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
from threading import Thread

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication")
        self.serial_connection = None
        self.is_connected = False

        # Port selection
        self.port_label = ttk.Label(root, text="Select Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5)

        self.port_combobox = ttk.Combobox(root, values=self.get_available_ports())
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Connect button
        self.connect_button = ttk.Button(root, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        # Text entry for sending messages
        self.send_entry = ttk.Entry(root, width=40)
        self.send_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Send button
        self.send_button = ttk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=2, padx=5, pady=5)

        # Terminal output for messages
        self.terminal = tk.Text(root, state="disabled", width=60, height=20)
        self.terminal.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    def get_available_ports(self):
        """List available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_serial(self):
        """Connect or disconnect from the selected serial port."""
        if self.is_connected:
            self.disconnect_serial()
        else:
            selected_port = self.port_combobox.get()
            if not selected_port:
                self.log_message("Error: No port selected.")
                return
            
            try:
                self.serial_connection = serial.Serial(selected_port, baudrate=115200, timeout=1)
                self.is_connected = True
                self.connect_button.config(text="Disconnect")
                self.log_message(f"Connected to {selected_port}")
                
                # Start a thread to read incoming data
                self.read_thread = Thread(target=self.read_serial, daemon=True)
                self.read_thread.start()
            except serial.SerialException as e:
                self.log_message(f"Error: Could not open port {selected_port} - {e}")

    def disconnect_serial(self):
        """Disconnect the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            self.connect_button.config(text="Connect")
            self.log_message("Disconnected from serial port.")

    def send_message(self):
        """Send a message through the serial port."""
        if not self.is_connected:
            self.log_message("Error: Not connected to any port.")
            return
        
        message = self.send_entry.get()
        if not message:
            self.log_message("Error: No message entered.")
            return
        
        try:
            self.serial_connection.write(message.encode())
            self.log_message(f"Sent: {message}")
            self.send_entry.delete(0, tk.END)
        except serial.SerialException as e:
            self.log_message(f"Error: Failed to send message - {e}")

    def read_serial(self):
        """Read messages from the serial port."""
        while self.is_connected:
            try:
                # Check if there is data waiting to be read
                if self.serial_connection and self.serial_connection.is_open and self.serial_connection.in_waiting > 0:
                    incoming_message = self.serial_connection.readline().decode("utf-8", errors="replace").strip()
                    if incoming_message:
                        self.log_message(f"Received: {incoming_message}")
            except serial.SerialException as e:
                self.log_message(f"Error: Failed to read from port - {e}")
                self.disconnect_serial()
                break
            except UnicodeDecodeError as e:
                # Handle decoding errors
                self.log_message(f"Error: Decoding error - {e}")
            except Exception as e:
                # Catch any other exceptions and log them
                self.log_message(f"Unexpected error: {e}")
                self.disconnect_serial()
                break


    def log_message(self, message):
        """Log a message to the terminal output."""
        self.terminal.config(state="normal")
        self.terminal.insert(tk.END, message + "\n")
        self.terminal.see(tk.END)
        self.terminal.config(state="disabled")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.mainloop()
