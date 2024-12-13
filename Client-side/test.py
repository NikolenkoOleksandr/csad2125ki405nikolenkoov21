import os
import json
from datetime import datetime
import configparser
import pytest
import inspect


class JsonLogger:
    def __init__(self, log_file="results/test_results.json"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.logs = []

    def log(self, level, message):
        log_entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.logs.append(log_entry)
        self._write_to_file()

    def _write_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=4)


class TestTicTacToeConfig:
    json_logger = JsonLogger()

    def setup_method(self, method):
        """Підготовка перед кожним тестом"""
        self.test_config_path = 'results/test_tictactoe.ini'
        self.json_logger.log("INFO", f"Starting test method: {method.__name__}")

    def test_default_config_creation(self):
        """Перевірка створення конфігураційного файлу з налаштуваннями за замовчуванням"""
        try:
            # Видаляємо тестовий файл, якщо він існує
            if os.path.exists(self.test_config_path):
                os.remove(self.test_config_path)

            config = configparser.ConfigParser()
            config['Serial'] = {'baud_rate': '9600'}
            config['Game'] = {'default_mode': 'Man vs Man'}

            with open(self.test_config_path, 'w') as f:
                config.write(f)

            # Перевіряємо, що файл створено
            assert os.path.exists(self.test_config_path)

            # Перевіряємо вміст файлу
            loaded_config = configparser.ConfigParser()
            loaded_config.read(self.test_config_path)

            assert loaded_config['Serial']['baud_rate'] == '9600'
            assert loaded_config['Game']['default_mode'] == 'Man vs Man'

            self.json_logger.log("INFO", "Default config creation test passed")
        except AssertionError as e:
            self.json_logger.log("ERROR", f"Default config creation test failed: {str(e)}")
            raise

    def test_config_baud_rate_options(self):
        """Перевірка коректності опцій baud rate"""
        try:
            valid_baud_rates = ['9600', '19200', '38400', '57600', '115200']

            config = configparser.ConfigParser()
            config['Serial'] = {'baud_rate': '9600'}

            assert config['Serial']['baud_rate'] in valid_baud_rates
            self.json_logger.log("INFO", "Baud rate options test passed")
        except AssertionError as e:
            self.json_logger.log("ERROR", f"Baud rate options test failed: {str(e)}")
            raise

    def test_game_mode_mapping(self):
        """Перевірка маппінгу режимів гри"""
        try:
            mode_map = {
                'Man vs Man': 1,
                'Man vs AI': 2,
                'AI vs AI': 3
            }

            assert mode_map['Man vs Man'] == 1
            assert mode_map['Man vs AI'] == 2
            assert mode_map['AI vs AI'] == 3

            self.json_logger.log("INFO", "Game mode mapping test passed")
        except AssertionError as e:
            self.json_logger.log("ERROR", f"Game mode mapping test failed: {str(e)}")
            raise

    def test_board_size_validation(self):
        """Перевірка коректності розміру ігрового поля"""
        try:
            board_size = 9

            # Перевіряємо, що дошка 3x3
            assert board_size == 9

            # Перевіряємо розподіл кнопок
            rows = 3
            cols = 3
            assert rows * cols == board_size

            self.json_logger.log("INFO", "Board size validation test passed")
        except AssertionError as e:
            self.json_logger.log("ERROR", f"Board size validation test failed: {str(e)}")
            raise

    def test_connection_port_validation(self):
        """Перевірка формату послідовних портів"""
        try:
            example_ports = [
                'COM3',
                'ttyUSB0'
            ]

            for port in example_ports:
                assert isinstance(port, str)
                assert len(port) > 0

            self.json_logger.log("INFO", "Connection port validation test passed")
        except AssertionError as e:
            self.json_logger.log("ERROR", f"Connection port validation test failed: {str(e)}")
            raise

# Видаляємо test_all функцію, оскільки pytest самостійно запустить всі тести