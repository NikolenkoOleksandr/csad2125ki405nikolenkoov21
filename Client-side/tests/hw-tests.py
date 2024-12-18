# -*- coding: utf-8 -*-
"""
Unit tests for the Arduino-based Tic-Tac-Toe game.
"""

import unittest
import serial
import time
import argparse
import sys


class TestTicTacToeHardware(unittest.TestCase):
    """Unit tests for the Arduino-based Tic-Tac-Toe game"""

    @classmethod
    def setUpClass(cls):
        """Initialize the serial connection to Arduino"""
        if not hasattr(cls, 'port') or not hasattr(cls, 'baudrate'):
            raise ValueError("Port and baudrate must be provided to run the tests.")

        try:
            cls.serial_connection = serial.Serial(port=cls.port, baudrate=cls.baudrate, timeout=3)
            time.sleep(2)  # Allow Arduino to reset
            print(f"Connected to Arduino on port {cls.port} at {cls.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Unable to connect to the specified serial port: {cls.port}. Tests will be skipped.\n{e}")
            cls.serial_connection = None

    @classmethod
    def tearDownClass(cls):
        """Close the serial connection to Arduino"""
        if cls.serial_connection:
            cls.serial_connection.close()
            print(f"Closed connection to Arduino on port {cls.port}.")

    def setUp(self):
        """Skip tests if the serial connection is not established"""
        if not self.__class__.serial_connection:
            self.skipTest("Arduino is not connected. Skipping test.")

    def send_command(self, command):
        """Send a command to Arduino and read the response"""
        try:
            self.serial_connection.write((command + '\n').encode('utf-8'))
            time.sleep(0.5)
            response = self.serial_connection.read_all().decode('utf-8').strip()
            print(f"Sent: {command}, Received: {response}")
            return response
        except Exception as e:
            self.fail(f"Error sending command '{command}': {e}")

    def test_reset_game(self):
        """Test resetting the game"""
        response = self.send_command("RESET")
        self.assertIn("OK:RESET", response, "Reset command did not return expected response.")

    def test_set_game_mode(self):
        """Test setting game mode"""
        for mode in [1, 2, 3]:
            response = self.send_command(f"MODE{mode}")
            self.assertIn("OK:MODE_SET", response, f"Failed to set game mode to {mode}.")

    def test_valid_move(self):
        """Test a valid move"""
        self.send_command("RESET")  # Ensure the board is reset
        self.serial_connection.reset_input_buffer()  # Clear input buffer

        self.send_command("MOVE0")
        time.sleep(1)  # Wait after command
        response = self.serial_connection.read_all().decode('utf-8').strip()

        print(f"Response after MOVE0: {response}")
        self.assertIn("BOARD:", response, "Valid move did not update the board.")
        self.assertIn(":CONTINUE", response, "Game did not continue after a valid move.")

    def test_invalid_move(self):
        """Test an invalid move"""
        self.send_command("RESET")
        self.send_command("MOVE0")
        response = self.send_command("MOVE0")
        self.assertIn("ERR:INVALID_MOVE", response, "Invalid move did not return an error.")

    def test_win_condition(self):
        """Test a win condition for player X"""
        self.send_command("RESET")
        self.send_command("MODE1")
        self.send_command("MOVE0")
        self.send_command("MOVE3")
        self.send_command("MOVE1")
        self.send_command("MOVE4")
        response = self.send_command("MOVE2")
        self.assertIn(":WIN:1", response, "Winning move did not return expected response.")

    def test_draw_condition(self):
        """Test a draw condition"""
        self.send_command("RESET")
        self.send_command("MODE1")
        moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]
        for move in moves[:-1]:
            self.send_command(f"MOVE{move}")
        response = self.send_command(f"MOVE{moves[-1]}")
        self.assertIn(":DRAW", response, "Draw game did not return expected response.")

    def test_ai_move(self):
        """Test an AI move in Man vs AI mode"""
        self.send_command("RESET")
        self.send_command("MODE2")
        response = self.send_command("MOVE0")
        self.assertIn("BOARD:", response, "AI move did not update the board.")
        self.assertIn(":CONTINUE", response, "Game did not continue after AI move.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Unit tests for the Arduino-based Tic-Tac-Toe game.")
    parser.add_argument('--port', type=str, help="The serial port to connect to (e.g., COM6 or /dev/ttyUSB0).")
    parser.add_argument('--baudrate', type=int, help="The baud rate for serial communication (e.g., 9600).")
    args = parser.parse_args()

    if not args.port or not args.baudrate:
        print("Port and baudrate are required to run the tests. Skipping tests.")
        sys.exit(0)

    return args


def main():
    args = parse_arguments()
    TestTicTacToeHardware.port = args.port
    TestTicTacToeHardware.baudrate = args.baudrate
    unittest.main(argv=sys.argv[:1])


if __name__ == "__main__":
    main()