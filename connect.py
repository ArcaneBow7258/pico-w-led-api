#Need to connect to wifi
import network
from config import  ssid, password
from time import sleep, time

import uasyncio, usocket
# # # # #
# 
# Seconds to wait before timing out the connection to wifi
timeout = 100
def connect(network_name = None, network_pass = None):
    global ssid
    global password
    if not (network_name or network_pass): # If neither netowrk_name nor netowrk_pass is set
        network_name = ssid
        network_pass = password
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.config(hostname="picow")
    wlan.active(True)
    wlan.connect(network_name, network_pass)
    start = time()
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        if ((time() - start) > timeout):
            raise TimeoutError()
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

def ap(network_name = "PicoW", network_pass = None, catchall = False):
    ap = network.WLAN(network.AP_IF)
    #ap.config(max_clients=10)
    ap.config(essid = network_name)
    if network_pass:
        print("Set password")
        ap.config(password = network_pass)
    else:
        ap.config(security=0)
    if catchall:
        print("turning on captvie portal and dns server")
    ap.active(True)
    print(f"Access point active at {network_name}.")



# I think t his was ripped off phew
# https://github.com/miguelgrinberg/microdot/discussions/141
async def _handler(socket, ip_address):
  while True:
    try:
      yield uasyncio.core._io_queue.queue_read(socket)
      request, client = socket.recvfrom(256)
      response = request[:2] # request id
      response += b"\x81\x80" # response flags
      response += request[4:6] + request[4:6] # qd/an count
      response += b"\x00\x00\x00\x00" # ns/ar count
      response += request[12:] # origional request body
      response += b"\xC0\x0C" # pointer to domain name at byte 12
      response += b"\x00\x01\x00\x01" # type and class (A record / IN class)
      response += b"\x00\x00\x00\x3C" # time to live 60 seconds
      response += b"\x00\x04" # response length (4 bytes = 1 ipv4 address)
      response += bytes(map(int, ip_address.split("."))) # ip address parts
      socket.sendto(response, client)
    except Exception as e:
      print(e)

def run_catchall(ip_address, port=53):
  print("> starting catch all dns server on port {}".format(port))
  _socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
  _socket.setblocking(False)
  _socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
  _socket.bind(usocket.getaddrinfo(ip_address, port, 0, usocket.SOCK_DGRAM)[0][-1])

  loop = uasyncio.get_event_loop()
  loop.create_task(_handler(_socket, ip_address))