#!/usr/bin/bash -1
import sys
import requests
import json
from datetime import (datetime, timedelta)
import bluetooth._bluetooth as bluez
from bluetooth_utils import (toggle_device, enable_le_scan,
    parse_le_advertising_events,
    disable_le_scan, raw_packet_to_str)

# Use 0 for hci0
dev_id = 0
toggle_device(dev_id, True)

try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print("Cannot open bluetooth device %i" % dev_id)
    raise

# Set filter to "True" to see only one packet per device
enable_le_scan(sock, filter_duplicates=False)

post_times={}

try:
    def le_advertise_packet_handler(mac, adv_type, data, rssi):
        data_str = raw_packet_to_str(data)

        # Check for ATC preamble
        if data_str[6:10] == '1a18':
            time_x_mins_ago = datetime.now() - timedelta(minutes = 15)
            if mac not in post_times or post_times[mac]<time_x_mins_ago: 
                post_times[mac] = datetime.now()
                temp = int(data_str[22:26], 16) / 10
                hum = int(data_str[26:28], 16)
                batt = int(data_str[28:30], 16)
                print("%s - Device: %s Temp: %sc Humidity: %s%% Batt: %s%%" % \
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mac, temp, hum, batt))

                url = "https://script.google.com/macros/s/AKfycbzPLP8tD-g-BmOhSc9abgyERrLnSjzGmr3QfT5Pz7u9ToNLh6oZ7f7mNuFFWbBVb6xXBg/exec"

                data = json.dumps(
                    {"mac": mac, 
                    "temp": temp,
                    "humidity": hum,
                    "battery": batt,
                    "UTCtimestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
                )
                try: 
                    r = requests.post(url, data, timeout=5, verify=True) 
                    print(r)
                    r.raise_for_status() 
                except requests.exceptions.HTTPError as errh: 
                    print("HTTP Error") 
                    print(errh.args[0]) 
                except requests.exceptions.ReadTimeout as errrt: 
                    print("Time out") 
                except requests.exceptions.ConnectionError as conerr: 
                    print("Connection error") 
                except requests.exceptions.RequestException as errex: 
                    print("Exception request") 

    # Called on new LE packet
    parse_le_advertising_events(sock,
        handler=le_advertise_packet_handler,
        debug=False)
# Scan until Ctrl-C
except KeyboardInterrupt:
    disable_le_scan(sock)