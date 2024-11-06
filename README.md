### Repository details
This repository contains a project for a hardware-based Tic-Tac-Toe 3x3 game using Arduino Uno and Python TKinter. The core game logic and decision-making will be handled on the Arduino Uno, while the Python TKinter application will function as a graphical user interface, allowing users to interact with the game.

### Task details
***Game Logic:*** Implement the core game logic of a 3x3 Tic-Tac-Toe on the Arduino Uno.
**Play Modes:**
* Man vs AI: Player competes against the AI.
* Man vs Man: Two players compete against each other.
* AI vs AI: Simulate games between two AI players. There should be two AI strategies:
    1. Random Move: AI makes random moves.
    2. Win Strategy: AI makes moves based on a win-maximizing strategy. 
 
**Actions:**
* New : Start a new game.
* Save Game: Save the current game state.
* Load Game: Load a previously saved game state.


### Student details

| Student Number | Game             | config format                          |
|:---------------:|:------------------:|:-----------------------------:|
| 21   | tik-tac-toe 3x3   | INI     |

### Technology Stack and Hardware Used

#### Hardware
- **Arduino Uno**: The Arduino will handle most of the game logic, including managing inputs, processing the current game state, and sending data to the Python application.

#### Software
- **Python TKinter**: Used for creating the graphical user interface (GUI) that displays the game board and allows users to view the game progress in real time.
- **Arduino IDE**: To write and upload the logic code to the Arduino Uno, primarily using C/C++ for low-level control.
#### Programming languages
- **Python**: Used to develop the TKinter interface that will interact with the Arduino.
- **C/C++**: Used in the Arduino environment to develop the Tic-Tac-Toe game logic.
#### Communication
- **Serial Communication**: The Arduino will communicate with the Python TKinter interface through a UART serial port to send and receive game status and input data.
