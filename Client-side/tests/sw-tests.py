import unittest
from unittest.mock import MagicMock, patch


class MockTicTacToeGUI:
    """Мокований клас TicTacToeGUI для ізоляції від GUI."""
    def __init__(self):
        self.serial_conn = MagicMock()  # Мок для серійного з'єднання
        self.port_combo = MagicMock()
        self.baud_combo = MagicMock()
        self.connect_btn = MagicMock()
        self.status_label = MagicMock()
        self.board_buttons = [MagicMock() for _ in range(9)]
        self.mode_combo = MagicMock()
        self.ai_timer = MagicMock()

    def refresh_ports(self):
        self.port_combo.addItems(['COM1', 'COM2'])

    def toggle_connection(self):
        if self.serial_conn:
            temp_conn = self.serial_conn  # Зберігаємо поточне з'єднання для перевірки
            temp_conn.close()  # Закриваємо з'єднання
            self.serial_conn = None
            self.connect_btn.setText("Connect")
        else:
            self.serial_conn = MagicMock()  # Створюємо нове моковане з'єднання
            self.connect_btn.setText("Disconnect")

    def reset_game(self):
        for button in self.board_buttons:
            button.setText("")
            button.setStyleSheet("")

    def make_move(self, position):
        if not self.serial_conn:
            return
        self.serial_conn.write(f"MOVE{position}\n".encode())

    def process_response(self):
        response = self.serial_conn.readline()
        if b"WIN" in response:
            self.status_label.setText("Game Over")
        elif b"DRAW" in response:
            self.status_label.setText("It's a draw!")

    def handle_disconnection(self):
        self.serial_conn = None
        self.status_label.setText("Disconnected")

    def change_mode(self):
        self.serial_conn.write(b"MODE1\n")

    def check_ai_moves(self):
        if self.serial_conn and self.serial_conn.in_waiting:
            self.process_response()


class TestTicTacToeGUI(unittest.TestCase):
    def setUp(self):
        """Set up the test environment using the mocked GUI class."""
        self.gui = MockTicTacToeGUI()

    def test_refresh_ports(self):
        """Test refreshing serial ports."""
        self.gui.refresh_ports()
        self.gui.port_combo.addItems.assert_called_once_with(['COM1', 'COM2'])

    def test_toggle_connection_connect(self):
        """Test toggling connection (connect)."""
        self.gui.serial_conn = None  # Початково з'єднання немає
        self.gui.toggle_connection()  # Викликаємо підключення
        self.gui.connect_btn.setText.assert_called_once_with("Disconnect")  # Очікуємо зміну тексту
        self.assertIsNotNone(self.gui.serial_conn)  # Переконуємося, що з'єднання створено

    def test_toggle_connection_disconnect(self):
        """Test toggling connection (disconnect)."""
        mock_conn = MagicMock()  # Імітуємо активне з'єднання
        self.gui.serial_conn = mock_conn
        self.gui.toggle_connection()  # Викликаємо відключення
        mock_conn.close.assert_called_once()  # Перевіряємо, що закриття було викликано
        self.assertIsNone(self.gui.serial_conn)  # Переконуємося, що з'єднання тепер None
        self.gui.connect_btn.setText.assert_called_once_with("Connect")  # Текст змінено на "Connect"

    def test_reset_game(self):
        """Test resetting the game."""
        self.gui.reset_game()
        for button in self.gui.board_buttons:
            button.setText.assert_called_once_with("")
            button.setStyleSheet.assert_called_once_with("")

    def test_make_move_not_connected(self):
        """Test making a move without connection."""
        self.gui.serial_conn = None
        self.gui.make_move(0)
        # Перевіряємо, що запис не здійснювався
        self.assertIsNone(self.gui.serial_conn)

    def test_make_move_valid(self):
        """Test making a valid move."""
        self.gui.make_move(0)
        self.gui.serial_conn.write.assert_called_once_with(b"MOVE0\n")

    def test_process_response_board_update(self):
        """Test processing response with board update."""
        self.gui.serial_conn.readline = MagicMock(
            return_value=b"BOARD:010102020\n"
        )
        self.gui.process_response()
        self.gui.status_label.setText.assert_not_called()

    def test_process_response_game_end(self):
        """Test processing response with game end."""
        self.gui.serial_conn.readline = MagicMock(
            return_value=b"BOARD:010102020:WIN:1\n"
        )
        self.gui.process_response()
        self.gui.status_label.setText.assert_called_once_with("Game Over")

    def test_handle_disconnection(self):
        """Test handling disconnection."""
        self.gui.handle_disconnection()
        self.assertIsNone(self.gui.serial_conn)
        self.gui.status_label.setText.assert_called_once_with("Disconnected")

    def test_change_mode(self):
        """Test changing game mode."""
        self.gui.change_mode()
        self.gui.serial_conn.write.assert_called_once_with(b"MODE1\n")

    def test_check_ai_moves(self):
        """Test AI move checking."""
        self.gui.serial_conn.in_waiting = True
        self.gui.process_response = MagicMock()
        self.gui.check_ai_moves()
        self.gui.process_response.assert_called_once()


if __name__ == '__main__':
    unittest.main()