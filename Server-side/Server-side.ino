#include <EEPROM.h>

/**
 * @defgroup server_side Server Side
 * @brief Documentation for the server-side firmware.
 * @{
 */

/**
 * @enum GameMode
 * @brief Enum representing game modes.
 */
enum GameMode {
  MAN_VS_MAN = 1,
  MAN_VS_AI = 2,
  AI_VS_AI = 3
};

/** @brief Game board representation (0: empty, 1: X, 2: O). */
int board[9] = {0,0,0,0,0,0,0,0,0};

/** @brief Current game mode. */
GameMode currentMode = MAN_VS_MAN;

/** @brief Indicates whether it is the first player's turn. */
bool isFirstPlayerTurn = true;

/** @brief Flag to control AI vs AI game flow. */
bool aiGameRunning = false;  // New flag to control AI vs AI game flow

/**
 * @brief Helper function to check if three positions match.
 * @param a Index of the first position.
 * @param b Index of the second position.
 * @param c Index of the third position.
 * @return True if all three positions match; otherwise, false.
 */
 bool checkLine(int a, int b, int c) {
  return (board[a] != 0) && (board[a] == board[b]) && (board[b] == board[c]);
}

/**
 * @brief Check for the winner.
 * @return 1 if player X wins, 2 if player O wins, 0 if no winner.
 */
int checkWinner() {
  // Check rows
  for(int i = 0; i < 9; i += 3)
    if(checkLine(i, i+1, i+2)) return board[i];
    
  // Check columns
  for(int i = 0; i < 3; i++)
    if(checkLine(i, i+3, i+6)) return board[i];
    
  // Check diagonals
  if(checkLine(0, 4, 8)) return board[0];
  if(checkLine(2, 4, 6)) return board[2];
  
  return 0;
}


/**
 * @brief Check if the game board is full.
 * @return True if the board is full; otherwise, false.
 */
bool isBoardFull() {
  for(int i = 0; i < 9; i++)
    if(board[i] == 0) return false;
  return true;
}

/**
 * @brief Calculate the AI's move.
 * @param player The player for which the move is calculated (1: X, 2: O).
 * @return The index of the calculated move, or -1 if no move is possible.
 */
int calculateAIMove(int player) {
  // First check if AI can win
  for(int i = 0; i < 9; i++) {
    if(board[i] == 0) {
      board[i] = player;
      if(checkWinner() == player) {
        board[i] = 0;
        return i;
      }
      board[i] = 0;
    }
  }
  
  // Check if opponent can win and block
  int opponent = (player == 1) ? 2 : 1;
  for(int i = 0; i < 9; i++) {
    if(board[i] == 0) {
      board[i] = opponent;
      if(checkWinner() == opponent) {
        board[i] = 0;
        return i;
      }
      board[i] = 0;
    }
  }
  
  // Take center if available
  if(board[4] == 0) return 4;
  
  // Take corner
  int corners[] = {0, 2, 6, 8};
  for(int i = 0; i < 4; i++) {
    if(board[corners[i]] == 0)
      return corners[i];
  }
  
  // Take any available space
  for(int i = 0; i < 9; i++)
    if(board[i] == 0) return i;
    
  return -1;
}


/**
 * @brief Process the received command.
 * @param command The received command as a string.
 */
void processCommand(String command) {
  // Обробка команди тесту підключення
  if(command == "<test_connection/>") {
    Serial.println("<connection_ok/>");
    return;
  }

  if(command.startsWith("MODE")) {
    currentMode = (GameMode)command.substring(4).toInt();
    memset(board, 0, sizeof(board));
    isFirstPlayerTurn = true;
    aiGameRunning = false;  // Reset AI game state on mode change
    Serial.println("OK:MODE_SET");
    return;
  }
  
  if(command.startsWith("MOVE")) {
    int position = command.substring(4).toInt();
    if(position < 0 || position > 8 || board[position] != 0) {
      Serial.println("ERR:INVALID_MOVE");
      return;
    }
    
    if(currentMode == MAN_VS_MAN) {
      board[position] = isFirstPlayerTurn ? 1 : 2;
      isFirstPlayerTurn = !isFirstPlayerTurn;
    } else {
      board[position] = 1;
    }
    
    String response = "BOARD:";
    for(int i = 0; i < 9; i++)
      response += String(board[i]);
      
    int winner = checkWinner();
    if(winner > 0) {
      Serial.println(response + ":WIN:" + String(winner));
      return;
    }
    if(isBoardFull()) {
      Serial.println(response + ":DRAW");
      return;
    }
    
    if(currentMode != MAN_VS_MAN) {
      int aiMove = calculateAIMove(2);
      if(aiMove >= 0) {
        board[aiMove] = 2;
        response = "BOARD:";
        for(int i = 0; i < 9; i++)
          response += String(board[i]);
          
        winner = checkWinner();
        if(winner > 0) {
          Serial.println(response + ":WIN:" + String(winner));
          return;
        }
        if(isBoardFull()) {
          Serial.println(response + ":DRAW");
          return;
        }
      }
    }
    
    Serial.println(response + ":CONTINUE");
    return;
  }
  
  if(command == "RESET") {
    memset(board, 0, sizeof(board));
    isFirstPlayerTurn = true;
    aiGameRunning = (currentMode == AI_VS_AI);  // Start AI game only on reset
    Serial.println("OK:RESET");
    return;
  }
}

/**
 * @brief Arduino setup function.
 */
void setup() {
  Serial.begin(9600);
  while(!Serial) {
    ; // Wait for serial port to connect
  }
}

/**
 * @brief Arduino main loop function.
 */
void loop() {
  if(Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // AI vs AI mode logic
  if(currentMode == AI_VS_AI && aiGameRunning && !isBoardFull() && checkWinner() == 0) {
    delay(1000);  // Add delay between moves
    
    // X's move
    int aiMove = calculateAIMove(1);
    if(aiMove >= 0) {
      board[aiMove] = 1;
      String response = "BOARD:";
      for(int i = 0; i < 9; i++)
        response += String(board[i]);
        
      int winner = checkWinner();
      if(winner > 0) {
        Serial.println(response + ":WIN:" + String(winner));
        aiGameRunning = false;  // Stop AI game on win
        return;
      }
      if(isBoardFull()) {
        Serial.println(response + ":DRAW");
        aiGameRunning = false;  // Stop AI game on draw
        return;
      }
      
      // O's move
      aiMove = calculateAIMove(2);
      if(aiMove >= 0) {
        board[aiMove] = 2;
        response = "BOARD:";
        for(int i = 0; i < 9; i++)
          response += String(board[i]);
          
        winner = checkWinner();
        if(winner > 0) {
          Serial.println(response + ":WIN:" + String(winner));
          aiGameRunning = false;  // Stop AI game on win
          return;
        }
        if(isBoardFull()) {
          Serial.println(response + ":DRAW");
          aiGameRunning = false;  // Stop AI game on draw
          return;
        }
        
        Serial.println(response + ":CONTINUE");
      }
    }
  }
}