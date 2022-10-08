"""
@author: Nicholas - Created on Wed Aug 22 02:32:47 2018
@author: Suhash - Updated on Oct 07 2022
"""

import time
import numpy as np
import serial

def read_ports():
    """Find ports with DMM connection.

    Returns:
        list str: DMM ports.
    """
    ports = []
    for comport in serial.tools.list_ports.comports():
        #if comport.vid
        #if comport.location
        #if 'USB-to-Serial' in comport.description
        if comport.pid:
            ports.append(comport.device)

    return ports

def read_DMMs(conf, dmms=None, sleepTime=0.5, meas_time=10000, val_range="AUTO", val_res=0.001):
    """Take specified measurement from multiple DMMs at every period for a set amount of time.

    Args:
        conf (str): Measurement mode. Look at set_CONF function for options.
        dmms (list DMM34401A, optional): DMM objects. Defaults to None.
        sleepTime (float, optional): Sleep time between measurements in sec. Defaults to 0.5.
        meas_time (int, optional): Total measurement time in sec. Defaults to 10000.
        val_range (str, optional): Approximate measurement range in standard units. Defaults to "AUTO".
        val_res (float, optional): Measurement resolution in standard units. Defaults to 0.001.

    Returns:
        np.array: Array of collected measurements
    """
    # Find all DMM ports and create objects if DMMs are not provided
    if not dmms:
        dmms = init_DMMs()
    # If a single DMM is given not in a list, reformat to a list
    elif not isinstance(dmms, list):
        dmms = list(dmms)

    # Set measurement mode on DMMs
    for dmm in dmms:
        dmm.set_CONF(conf, val_range, val_res)

    time.sleep(2)
    print("Start Reading")
    output = []

    # Start time
    tic = time.time()
    toc = tic

    # Read DMMs
    try:
        while (toc - tic) < meas_time:
            # A pause is required between reads
            time.sleep(sleepTime)

            toc = time.time()
            measurements = []
            for dmm in dmms:
                measurements.append(dmm.read_meas())

            vals = [(toc-tic)] + measurements
            print(*vals, sep='\t')
            output.append(vals)

        return np.array(output)

    except KeyboardInterrupt:
        # End measurements
        return np.array(output)


def init_DMMs():
    """Create objects for all connected DMMs.

    Returns:
        list DMM34401A: DMM objects.
    """
    dmms = []
    ports = read_ports()
    for port in ports:
        dmm = DMM34401A(port)
        dmms.append(dmm)

    return dmms

def del_DMMs(dmms):
    """Remove all DMM objects.

    Args:
        dmms(list DMM34401A): DMM objects.
    """
    for dmm in dmms:
        del dmm


class DMM34401A:
    """DMM object."""

    def __init__(self, port_num, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, bytesize=serial.EIGHTBITS, xonxoff=True):
        self.ser = serial.Serial(port = port_num,
                                 baudrate = baudrate,
                                 parity = parity,
                                 stopbits = stopbits,
                                 bytesize = bytesize,
                                 xonxoff = xonxoff)

        time.sleep(0.5)
        if self.ser.is_open:
            self.ser.write("SYSTem:REMote\n".encode())


    def __del__(self):
        """Close serial port upon object delection."""
        self.ser.close()

    def read_ID(self):
        output = self.ser.write("*IDN?\n".encode())
        return output

    def set_CONF(self, conf, val_range="AUTO", val_res=0.001):
        """Set DMM to measurement mode.

        Args:
            conf (str): Measurement mode.
            val_range (str or int, optional): Approximate range of measurement in standard units. Defaults to "AUTO".
            val_res (float, optional): Measurement resolution in standard units. Defaults to 0.001.
        """

        if conf is "DCV": # DC voltage
            self.ser.write(f"CONF:VOLT:DC {val_range}, {val_res}\n".encode())
        elif conf is "ACV": # AC voltage
            self.ser.write(f"CONF:VOLT:AC {val_range}, {val_res}\n".encode())
        elif conf is "DCI": # DC current
            self.ser.write(f"CONF:CURR:DC {val_range}, {val_res}\n".encode())
        elif conf is "ACI": # AC current
            self.ser.write(f"CONF:CURR:AC {val_range}, {val_res}\n".encode())
        elif conf is "RES2": # 2-wire resistance
            self.ser.write(f"CONF:RES {val_range}, {val_res}\n".encode())
        elif conf is "RES4": # 4-wire resistance
            self.ser.write(f"CONF:FRES {val_range}, {val_res}\n".encode())
        elif conf is "FREQ": # Frequency
            self.ser.write(f"CONF:FREQ {val_range}, {val_res}\n".encode())
        elif conf is "PER": # Period
            self.ser.write(f"CONF:PER {val_range}, {val_res}\n".encode())
        else:
            pass

    def set_TRIG(self, val="IMM"):
        """Set trigger for measurement..

        Args:
            val (str, optional): Trigger source. Can be IMMediate, BUS, or EXTernal. Defaults to "IMM".
        """
        self.ser.write(f"TRIG:SOUR {val}\n".encode())

    def read_meas(self):
        """Take a measurement from the DMM.

        Returns:
            float: DMM measurement.
        """
        try:
            self.ser.write("READ?\n".encode())
            temp = self.ser.readline()
            output = float(temp[:-2])
        except ValueError:
            print(temp)
            temp = self.ser.readline()
            output = float(temp[:-2])

        return output
