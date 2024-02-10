import serial
import re
from datetime import datetime
import requests 

# target_host = 'http://192.168.1.200'
target_host = 'http://localhost:5000'

start_url = target_host + '/start' 

a = serial.Serial('//dev/tty.usbserial-14130', baudrate=2400)

a.write(b'I am writing to a XEN console, as it is my only convenient serial device\r\n')

while 1:
        b = ""
        b = a.read_until(b'\r').decode('utf-8')

        corrected = b[0] == 'c'
        unknown = '?' in b  
        setting = b[0] == 'n'

        if corrected or unknown or setting: 
            print('IGNORIEREN')
        else:
            start_number = re.search("^.\d\d\d\d", b).group()[1:]
            time_format = "%H:%M:%S.%f"
            time_str = re.search("\d\d:\d\d:\d\d.\d\d", b).group()
            time_object = datetime.strptime(time_str, time_format)
            runtime_ms = int((time_object - datetime(1900, 1, 1)).total_seconds() * 1000)
            print(start_number)
            print(runtime_ms)
            if 'C1' in b:
              print("ZIEL!")
            else:
                if 'C' in b:
                  if 'C0' in b:
                    print("START!")
                    # Sending a POST request with data
                    data = { 'start_number': start_number }
                    print(data)
                    response = requests.post(start_url, data=data)
                  else:
                    print("Zwischenzeit")
        # print (' '.join(( '%02x'%x for x in b )), ':', b)