
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
pzem_shunt = {"50A": 1, "100A": 0, "200A": 2, "300A": 3}

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
            pzem_shunt = {
#                "shunt": {"50A": 1, "100A": 0, "200A": 2, "300A": 3}
                "50A": 1, "100A": 0, "200A": 2, "300A": 3
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
                        nargs='?', const=None,
                        help='Path to serial device like /dev/ttyUSB0.')
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
                        choices=['cli','influxlineprotocol'],
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
    parser.add_argument('--sethigh', type=int,
                        nargs='?', const=None,
                        help='Set high voltage alarm')
    parser.add_argument('--setlow', type=int,
                        nargs='?', const=None,
                        help='Set low voltage alarm')
    parser.add_argument('--setcurrenttype',
                        nargs='?', const=None,
                        choices=['50A','100A','200A','300A'],
                        help='Set current shunt, only for PZEM-017. Possible values: 50A, 100A, 200A, 300A')
    parser.add_argument('--setaddress', type=int,
                        nargs='?', const=None,
                        help='Set modbus address')
    parser.add_argument('--debug', type=int,
                        nargs='?', default=False, const=None,
                        help='show debugging informations'
                             'Default: %s' % False)
    if scan_additional_arguments:
        scan_additional_arguments(parser)
    args = parser.parse_args()
    return args

def output_cli(key):
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

def output_influxlineprotocol(key):
    if debug == True: print ("----> building measurement string")
    if args.measurement == MEASUREMENT:
        measurement =  str(args.address) + "_" + args.model
    if debug == True: print ("----> measurement string: " + measurement)
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

def cmd_read():
    for key in pzem_register:
        if debug == True: print ("----> Register: " + key)
        if pzem_register[key]["use"] == True:
            if debug == True: print ("----> Call register: " + key + " for CLI")
            if args.output == "cli":
                if debug == True: print("----> outputformat is cli")
                output_cli(key)
            elif args.output == "influxlineprotocol":
                if debug == True: print("----> outputformat is influxlineprotocol")
                output_influxlineprotocol(key)
            else:
                print("outputformat not found")
                print()
                show_connection_parameters()
                sys.exit(1)
        time.sleep(SLEEP)

def set_high_voltage_alarm(highvoltage):
    if debug == True: print("----> set high voltage alarm to " + str(highvoltage))
    if debug == True: print("----> using register " + str(pzem_register["U_max_alarm_set"]["port"]))
    if debug == True: print("----> using value " + str(highvoltage))
    if debug == True: print("----> using digits " + str(pzem_register["U_max_alarm_set"]["digits"]))
    if debug == True: print("----> using functioncode " + str(pzem_register["U_max_alarm_set"]["functioncode"]))
    try:
        instrument.write_register(
            registeraddress = pzem_register["U_max_alarm_set"]["port"],
            value = highvoltage,
            number_of_decimals = pzem_register["U_max_alarm_set"]["digits"],
            functioncode = 6
        )
    except TypeError: 
        print("TypeError")
        return
    except ValueError: 
        print("ValueError")
        return
    except IOError: 
        print("IOError")
        return

    time.sleep(1)
    msg = ("Voltage max alarm is set at: ")
    msg = msg + str( 
        instrument.read_register(
        functioncode = pzem_register["U_max_alarm_set"]["functioncode"],
        registeraddress = pzem_register["U_max_alarm_set"]["port"],
        number_of_decimals = pzem_register["U_max_alarm_set"]["digits"],
        signed=False
        )
    )
    print(msg)

def set_low_voltage_alarm(lowvoltage):
    if debug == True: print("----> set low voltage alarm to " + str(lowvoltage))
    if debug == True: print("----> using register " + str(pzem_register["U_min_alarm_set"]["port"]))
    if debug == True: print("----> using value " + str(lowvoltage))
    if debug == True: print("----> using digits " + str(pzem_register["U_min_alarm_set"]["digits"]))
    if debug == True: print("----> using functioncode " + str(pzem_register["U_min_alarm_set"]["functioncode"]))
    try:
        instrument.write_register(
            registeraddress = pzem_register["U_min_alarm_set"]["port"],
            value = lowvoltage,
            number_of_decimals = pzem_register["U_min_alarm_set"]["digits"],
            functioncode = 6
        )
    except TypeError: 
        print("TypeError")
        return
    except ValueError: 
        print("ValueError")
        return
    except IOError: 
        print("IOError")
        return

    time.sleep(1)
    msg = ("Voltage min alarm is set at: ")
    msg = msg + str( 
        instrument.read_register(
        functioncode = pzem_register["U_min_alarm_set"]["functioncode"],
        registeraddress = pzem_register["U_min_alarm_set"]["port"],
        number_of_decimals = pzem_register["U_min_alarm_set"]["digits"],
        signed=False
        )
    )
    print(msg)

def set_current_type(currenttype):
    if args.model != "PZEM017":
        print("Model does not support external shunts")
        return
    if debug == True: print("----> set currenttype to " + currenttype)
    if debug == True: print("----> using register " + str(pzem_register["Current_Range"]["port"]))
    if debug == True: print("----> using value " + str(pzem_shunt[currenttype]) + " (" + currenttype + ")")
    if debug == True: print("----> using digits " + str(pzem_register["Current_Range"]["digits"]))
    if debug == True: print("----> using functioncode " + str(pzem_register["Current_Range"]["functioncode"]))
    if debug == True: print("----> using model " + str(args.model))

    try:
        instrument.write_register(
            registeraddress = pzem_register["Current_Range"]["port"],
            value = pzem_shunt[currenttype],
            number_of_decimals = pzem_register["Current_Range"]["digits"],
            functioncode = 6
        )
    except TypeError: 
        print("TypeError")
        sys.exit(1)
    except ValueError: 
        print("ValueError")
        sys.exit(1)
    except IOError: 
        print("IOError")
        sys.exit(1)
    reverse_pzem_shunt = dict((v,k) for k,v in pzem_shunt.items())

    time.sleep(1)
    msg = ("Currentype is set for type: ")
    msg = msg + str( 
        instrument.read_register(
        functioncode = pzem_register["Current_Range"]["functioncode"],
        registeraddress = pzem_register["Current_Range"]["port"],
        number_of_decimals = pzem_register["Current_Range"]["digits"],
        signed=False
        )
    )
    msg = msg + " (" + str( reverse_pzem_shunt[pzem_shunt[currenttype]]) + ")"
    print(msg)

def set_address(newaddress):
    if debug == True: print("----> set address")
    if debug == True: print("----> using register " + str(pzem_register["Address"]["port"]))
    if debug == True: print("----> using value " + str(newaddress))
    if debug == True: print("----> using digits " + str(pzem_register["Address"]["digits"]))
    if debug == True: print("----> using functioncode " + str(pzem_register["Address"]["functioncode"]))

    try:
        instrument.write_register(
            registeraddress = pzem_register["Address"]["port"],
            value = newaddress,
            number_of_decimals = pzem_register["Address"]["digits"],
            functioncode = 6
        )
    except TypeError: 
        print("TypeError")
        sys.exit(1)
    except ValueError: 
        print("ValueError")
        sys.exit(1)
    except IOError: 
        print("IOError")
        sys.exit(1)

    time.sleep(1)
    newinstrument = minimalmodbus.Instrument( args.device, newaddress)
    newinstrument.serial.baudrate = 9600
    newinstrument.serial.parity = serial.PARITY_EVEN
    newinstrument.serial.bytesize = 8
    newinstrument.serial.timeout = 5
    newinstrument.serial.write_timeout = 5
    newinstrument.debug = False
    newinstrument.clear_buffers_before_each_transaction = True

    msg = ("Device address is setted to: ")
    msg = msg + str( 
        newinstrument.read_register(
        functioncode = pzem_register["Address"]["functioncode"],
        registeraddress = pzem_register["Address"]["port"],
        number_of_decimals = pzem_register["Address"]["digits"],
        signed=False
        )
    )
    print(msg)


args = get_cli_arguments()

if debug == True: print ("----> Device: " + args.device)
if debug == True: print ("----> Address: " + str(args.address))
if debug == True: print ("----> Model: " + str(args.model))

if not args.device:
    print('device required')
    print()
#    helpmessage()
    args.print_help()
    sys.exit(1)
else:
    try:
        if debug == True: print("----> init modbus")
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
        if args.sethigh != None:
            if debug == True: print("----> call set high voltage alarm")
            set_high_voltage_alarm(args.sethigh)
            sys.exit(0)
        if args.setlow != None:
            if debug == True: print("----> call set low voltage alarm")
            set_low_voltage_alarm(args.setlow)
            sys.exit(0)
        if args.setcurrenttype != None:
            if debug == True: print("----> call set current shunt")
            set_current_type(args.setcurrenttype)
            sys.exit(0)
        if args.setaddress != None:
            if debug == True: print("----> call set address")
            set_address(args.setaddress)
            sys.exit(0)
        if args.sethigh == None and args.setlow == None and args.setcurrenttype == None and args.setaddress == None:
            if debug == True: print("----> read")
            cmd_read()
            sys.exit(0)


    except BaseException:
        #print(BaseException)
        #print("can not connect to device")
        #print()
        #show_connection_parameters()
        sys.exit(1)
