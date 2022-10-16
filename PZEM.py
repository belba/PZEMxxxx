
import argparse
import sys
import time
import serial
import minimalmodbus

# Define CLI Default paramater
METER_SERIALPORT = "/dev/ttyUSB0"
METER_MODBUSADDRESS = 1
METER_MODEL="PZEMgeneric"
OUTPUTFORMAT = "cli"
MEASUREMENT = "TEST_PZEM"
SLEEP = 0
BAUDRATE = 9600

debug = False

def helpmessage():
    print('Options:')
    print('-d --device [Devicepath], Path to serial device. Default: ' + METER_SERIALPORT)
    print('-a --address [Modbusaddress], Modbusaddresss for the device. Default: ' + str(METER_MODBUSADDRESS))
    print('-m --model [Devicemodell], Default: ' + METER_MODEL)
    print('           aviable models: PZEMgeneric, PZEM003, PZEM017')
    print('-o --output [outputformat], Default: ' + OUTPUTFORMAT)
    print('           aviable output formats: cli, influxlineprotocol')
    print('-t --measurement [measurement], Default: ' + MEASUREMENT)
    print('-s --sleep [sleeptime in seconds], Default: ' + str(SLEEP))
    print('-b --baudrate [baudrate], Default: ' + str(BAUDRATE))
    print()

def show_connection_parameters():
    print("used connection parameters:")
    print("Serial device: " + args.device)
    print("Serial baudrate: " + str(args.baudrate))
    print("Modbusaddress: " + str(args.address))
    print("Model: " + args.model)
    print("Outputformat: " + args.output)
    print("Measurement: " + args.measurement)

# Define Registersets for the different Models
def get_pzem_register(pzem_model="PZEMgeneric"):
    if pzem_model == "PZEMgeneric":
            pzem_register = {
                "U": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "I": {"port": 1, "digits": 2, "Unit": "A", "use": True, "writeable": False, "functioncode": 4},
                "P": {"port": 2, "digits": 1, "Unit": "W", "use": True, "writeable": False, "functioncode": 4},
                "P_sum": {"port": 4, "digits": 0, "Unit": "Wh", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_stat": {"port": 6, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_min_alarm_stat": {"port": 7, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_set": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "U_min_alarm_set": {"port": 1, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "Address": {"port": 2, "digits": 0, "Unit": None, "use": True, "writeable": True, "functioncode": 3},
                "Current_Range": {"port": 3, "digits": 0, "Unit": "A", "use": True, "writeable": True, "functioncode": 3},
            }

    elif pzem_model == "PZEM003":
            pzem_register = {
                "U": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "I": {"port": 1, "digits": 2, "Unit": "A", "use": True, "writeable": False, "functioncode": 4},
                "P": {"port": 2, "digits": 1, "Unit": "W", "use": True, "writeable": False, "functioncode": 4},
                "P_sum": {"port": 4, "digits": 0, "Unit": "Wh", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_stat": {"port": 6, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_min_alarm_stat": {"port": 7, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_set": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "U_min_alarm_set": {"port": 1, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "Address": {"port": 2, "digits": 0, "Unit": None, "use": True, "writeable": True, "functioncode": 3},
            }
    elif pzem_model == "PZEM017":
            pzem_register = {
                "U": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "I": {"port": 1, "digits": 2, "Unit": "A", "use": True, "writeable": False, "functioncode": 4},
                "P": {"port": 2, "digits": 1, "Unit": "W", "use": True, "writeable": False, "functioncode": 4},
                "P_sum": {"port": 4, "digits": 0, "Unit": "Wh", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_stat": {"port": 6, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_min_alarm_stat": {"port": 7, "digits": 0, "Unit": "V", "use": True, "writeable": False, "functioncode": 4},
                "U_max_alarm_set": {"port": 0, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "U_min_alarm_set": {"port": 1, "digits": 2, "Unit": "V", "use": True, "writeable": True, "functioncode": 3},
                "Address": {"port": 2, "digits": 0, "Unit": None, "use": True, "writeable": True, "functioncode": 3},
                "Current_Range": {"port": 3, "digits": 0, "Unit": "A", "use": True, "writeable": True, "functioncode": 3},
            }
    else:
        print("model not found")
        sys.exit(1)
    return pzem_register

def get_cli_arguments(scan_additional_arguments=None):
    parser = argparse.ArgumentParser()
    parser.prog='pzem'
    parser.description='get all paramater of a pzem-smartmeter device'  

    parser.add_argument('-d', '--device',
                        nargs='?', default=METER_SERIALPORT, const=None,
                        help='Path to serial device like /dev/ttyUSB0.'
                             'Default: %s' % METER_SERIALPORT)
    parser.add_argument('-a', '--address', type=int, 
                        nargs='?', default=METER_MODBUSADDRESS, const=None,
                        help='Modbusaddress of the device.'
                             'Default: %s' % METER_MODBUSADDRESS)
    parser.add_argument('-m', '--model',
                        nargs='?', default=METER_MODEL, const=None,
                        help='Modell of the device'
                             'Default: %s' % METER_MODEL)
    parser.add_argument('-o', '--output',
                        nargs='?', default=OUTPUTFORMAT, const=None,
                        help='Output format: cli, influxlineprotocol'
                             'Default: %s' % OUTPUTFORMAT)
    parser.add_argument('-t', '--measurement',
                        nargs='?', default=MEASUREMENT, const=None,
                        help='measurement string'
                             'Default: %s' % MEASUREMENT)
    parser.add_argument('-s', '--sleep', type=int,
                        nargs='?', default=SLEEP, const=None,
                        help='sleeptime'
                             'Default: %s' % SLEEP)
    parser.add_argument('--set-address', type=int,
                        nargs='?', default=METER_MODBUSADDRESS, const=None,
                        help='Set modbus address'
                             'Default: %s' % METER_MODBUSADDRESS)
    parser.add_argument('--debug', type=int,
                        nargs='?', default=False, const=None,
                        help='show debugging informations'
                             'Default: %s' % False)
    if scan_additional_arguments:
        scan_additional_arguments(parser)
    args = parser.parse_args()
    return args

def output_cli():
    msg = (key + ": " )
    msg = msg + str( 
        instrument.read_register(
        functioncode=pzem_register[key]["functioncode"],
        registeraddress=pzem_register[key]["port"],
        number_of_decimals=pzem_register[key]["digits"],
        signed=False
        )
    )
    if pzem_register[key]["functioncode"] == 4 : msg = msg + pzem_register[key]["Unit"]
    print(msg)

def output_influxlineprotocol():
    msg = (measurement + ",address=" + str(args.address))
    msg = msg + ",model='" + args.model + "'"
    msg = msg + " " + key + "=" + str(
        instrument.read_register(
        functioncode=pzem_register[key]["functioncode"],
        registeraddress=pzem_register[key]["port"],
        number_of_decimals=pzem_register[key]["digits"],
        signed=False
        )
    )   
    print(msg)

args = get_cli_arguments()

if debug == True: print ("Device: " + args.device)
if debug == True: print ("Address: " + str(args.address))
if debug == True: print ("Model: " + str(args.model))

if not args.device:
    print('device required')
    print()
    helpmessage()
    sys.exit(1)
else:
    try:
        instrument = minimalmodbus.Instrument( args.device, args.address)
        instrument.serial.baudrate = 9600
        instrument.serial.parity = serial.PARITY_EVEN
        instrument.serial.bytesize = 8
        #instrument.serial.stopbits = serial.STOPBITS_TWO
        instrument.serial.timeout = 5
        instrument.serial.write_timeout = 5
        instrument.debug = False
        instrument.clear_buffers_before_each_transaction = True
        pzem_register = get_pzem_register(args.model)
        if debug == True: print ("building measurement string")
        if args.measurement == MEASUREMENT:
            measurement =  str(args.address) + "_" + args.model
        if debug == True: print ("measurement string: " + measurement)
        for key in pzem_register:
            if debug == True: print ("Register: " + key)
            if pzem_register[key]["use"] == True:
                if debug == True: print ("Call register: " + key + " for CLI")
                if args.output == "cli":
                    if debug == True: print("using modbus...")
                    output_cli()
                elif args.output == "influxlineprotocol":
                    output_influxlineprotocol()
                else:
                    print("outputformat not found")
                    print()
                    show_connection_parameters()
                    sys.exit(1)
            time.sleep(SLEEP)
    except BaseException:
        #print(BaseException)
        #print("can not connect to device")
        #print()
        #show_connection_parameters()
        sys.exit(1)
