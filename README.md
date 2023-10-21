# pico-w-led-webserver
RPi Pico W LED controller for my wardrobe. 
Running MicroPython.
Using WS2812B Addressible LED's (60/m)
Running Raspberry Pi Webserver as a websight to contact Pico W. Otherwise, you can just connect to local host and call GET/POST from other ways.
- Check out Raspberry-Pi-Webserver Repo on Profile to see.
**Important Note**: When you wanna upload production versions, upload a _Main.py_  or _Boot.py_ instead.
- I'd probably make a Main.py that imports/runs app.py but checks a variable whether or not to actually run it.

# Set-up
- Use Thonny or Pico-W's bootloader function to install MicroPython (google it)
- Development done in VS Code using MicroPico Extension to connect to Pico
- If not using lib/adding more MicroPython Libraries, follow this [link](https://github.com/micropython/micropython/blob/master/mpy-cross/README.md).
    - Note: You can simply upload the .py libraries on your own, but for efficiency of your Microcontroller .mpy is better.
- Using _MicroPico_ in VS Code, open microdot_asyncio, CTRL + SHIFT + P -> "Upload Current File to Pico" to get library on Pico W so you don't error out when running code using MicroPico run function.
    - Alternatively, you can just right-click any file and press "Upload project to Pico", but might get some bload.
- You're on your own on soldering and power set-up, but plenty of tutorials on there

# Common Errors
- If you keep disconnecting to your Pico W with MicroPico, use command "MicrPico: Switch Pico" and should work
- You might get an error running code consecutively saying port is already in use. Simply hit the reset button on bottom of VS Code after Stopping Web Server
    - I might fix this later    
