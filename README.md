# reflexgame
A micropython game to test 4 players' reflexes in a fun way. https://dvidpi.net/diy-reaction-time-game/

There's two files:
main.py - This is the full code, you can modify the pinout to your needs
main-minifed.py - This is the minified code, if for whatever reason you have low space on your MCU. Don't bother trying to figure out how to change the pinout, instead follow this one:

LED Ring: GPIO6 
Score LEDs: GPIO7 

Player 1: 
Button: GPIO4 
Button LED: GPIO8 

Player 2: 
Button: GPIO3 
Button LED: GPIO9 

Player 3: 
Button: GPIO2 
Button LED: GPIO10 

Player 4: 
Button: GPIO1 
Button LED: GPIO20

Everything else you might need to know is on the [blog post](https://dvidpi.net/diy-reaction-time-game/).
