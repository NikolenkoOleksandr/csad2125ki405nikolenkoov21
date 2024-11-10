import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk
import serial
from main import SerialApp

class TestSerialApp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.app = SerialApp(self.root)
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.app.is_connected:
            self.app.disconnect_serial()
        self.root.destroy()

    def test_get_available_ports(self):
        """Test getting available ports."""
        with patch('serial.tools.list_ports.comports') as mock_comports:
            # Setup mock ports
            mock_ports = [
                Mock(device='COM3'),
                Mock(device='COM4')
            ]
            mock_comports.return_value = mock_ports
            
            # Get ports using the method
            ports = self.app.get_available_ports()
            
            # Assert
            self.assertEqual(ports, ['COM3', 'COM4'])

    @patch('serial.Serial')
    def test_connect_serial_success(self, mock_serial):
        """Test successful serial connection."""
        # Setup
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        
        # Execute
        self.app.port_combobox.set('COM1')
        self.app.connect_serial()
        
        # Assert
        self.assertTrue(self.app.is_connected)
        self.assertEqual(self.app.connect_button['text'], 'Disconnect')
        mock_serial.assert_called_once_with('COM1', baudrate=115200, timeout=1)

    @patch('serial.Serial')
    def test_connect_serial_failure(self, mock_serial):
        """Test serial connection failure."""
        # Setup
        mock_serial.side_effect = serial.SerialException("Connection failed")
        
        # Execute
        self.app.port_combobox.set('COM1')
        self.app.connect_serial()
        
        # Assert
        self.assertFalse(self.app.is_connected)
        self.assertEqual(self.app.connect_button['text'], 'Connect')

    def test_disconnect_serial(self):
        """Test serial disconnection."""
        # Setup
        self.app.is_connected = True
        self.app.serial_connection = Mock()
        self.app.connect_button.config(text="Disconnect")
        
        # Execute
        self.app.disconnect_serial()
        
        # Assert
        self.assertFalse(self.app.is_connected)
        self.assertEqual(self.app.connect_button['text'], 'Connect')
        self.app.serial_connection.close.assert_called_once()

    @patch('serial.Serial')
    def test_send_message_connected(self, mock_serial):
        """Test sending a message when connected."""
        # Setup
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        self.app.port_combobox.set('COM1')
        self.app.connect_serial()
        test_message = "Test message"
        self.app.send_entry.insert(0, test_message)
        
        # Execute
        self.app.send_message()
        
        # Assert
        mock_serial_instance.write.assert_called_once_with(test_message.encode())

    def test_send_message_not_connected(self):
        """Test sending a message when not connected."""
        # Setup
        self.app.is_connected = False
        self.app.send_entry.insert(0, "Test message")
        
        # Execute
        self.app.send_message()
        
        # Get terminal text and verify error message
        terminal_text = self.app.terminal.get("1.0", tk.END)
        self.assertIn("Error: Not connected to any port", terminal_text)

    def test_log_message(self):
        """Test logging messages to terminal."""
        # Execute
        test_message = "Test log message"
        self.app.log_message(test_message)
        
        # Assert
        terminal_text = self.app.terminal.get("1.0", tk.END)
        self.assertIn(test_message, terminal_text)

    @patch('main.Thread')  # Patch Thread where it's imported in main.py
    @patch('serial.Serial')
    def test_read_thread_creation(self, mock_serial, mock_thread):
        """Test that read thread is created on connection."""
        # Setup
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Execute
        self.app.port_combobox.set('COM1')
        self.app.connect_serial()
        
        # Assert
        mock_thread.assert_called_once()
        self.assertEqual(mock_thread.call_args[1]['target'], self.app.read_serial)
        self.assertTrue(mock_thread.call_args[1]['daemon'])
        mock_thread_instance.start.assert_called_once()

if __name__ == '__main__':
    with open("test_reports.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner, exit=False)
