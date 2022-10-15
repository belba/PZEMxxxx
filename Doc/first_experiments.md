
First experiments are using mbpoll

Change address of modbus:

    mbpoll -a 1 -b 9600 -t 4 -m rtu -r 3 /dev/ttyUSB0 3

CLI response:

    mbpoll 1.0-0 - FieldTalk(tm) Modbus(R) Master Simulator
    Copyright © 2015-2019 Pascal JEAN, https://github.com/epsilonrt/mbpoll
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type 'mbpoll -w' for details.

    Protocol configuration: Modbus RTU
    Slave configuration...: address = [1]
                            start reference = 3, count = 1
    Communication.........: /dev/ttyUSB0,       9600-8E1 
                            t/o 1.00 s, poll rate 1000 ms
    Data type.............: 16-bit register, output (holding) register table

    Written 1 references.


Call some measurments:

    mbpoll -a 3 -b 9600 -t 3 -m rtu -r 1 -c 8 /dev/ttyUSB0

CLI response:

    mbpoll 1.0-0 - FieldTalk(tm) Modbus(R) Master Simulator
    Copyright © 2015-2019 Pascal JEAN, https://github.com/epsilonrt/mbpoll
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type 'mbpoll -w' for details.

    Protocol configuration: Modbus RTU
    Slave configuration...: address = [3]
                            start reference = 1, count = 8
    Communication.........: /dev/ttyUSB0,       9600-8E1 
                            t/o 1.00 s, poll rate 1000 ms
    Data type.............: 16-bit register, input register table

    -- Polling slave 3... Ctrl-C to stop)
    [1]: 	507
    [2]: 	0
    [3]: 	0
    [4]: 	0
    [5]: 	18
    [6]: 	0
    [7]: 	0
    [8]: 	65535 (-1)

