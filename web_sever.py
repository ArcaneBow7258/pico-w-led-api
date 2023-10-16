import network
import machine
from time import sleep, time

import socket


timeout = 100
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    start = time()
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        if ((time() - start) > timeout):
            raise TimeoutError()
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    port = 80
    address = (ip, port)
    connection = socket.socket()
    try:
        connection.bind(address)
    except OSError:
        print("Address is used, skip")
    connection.listen(1)
    return connection

def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/test?':
            print('test')
        elif request == '/off?':
            break
        html = home()
        client.send(html)
        client.close()

def home():
    html = f"""
    <!DOCTYPE html>
        <html>
            <body>
                <form action="./lighton">
                    <input type="submit" value="Light on" />
                    </form>
                <form action="./lightff">
                    <input type="submit" value="Light off" />
                    </form>
            </body>
    </html>
"""
    return str(html)

try:
    ip = connect()
    connection= open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()