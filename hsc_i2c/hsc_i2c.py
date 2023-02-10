# -*- coding: utf-8 -*-
from smbus2 import SMBus


class honeywell_hsc:
    """Honeywell HSC Pressure Sensor Reader"""

    output_max = 14745.0  # (90% of 214 counts or 0x3999)
    output_min = 1638.0  # (10% of 214 counts or 0x0666)

    def __init__(
        self,
        i2c_addr: int,
        max_pressure: int = 100,
        auto_calibrate: bool = True
    ) -> None:
        """To use you needs pass the i2c address your sensor is listed on for
        honeywell this is hardwired see HSC docmentation / part number to
        solve. Otherwise use "i2cdetect -y 1" from shell
        
        Args:
            i2c_addr (int): Address for sensor
            max_pressure (int, optional): Default 100, but set to the max
                                            pressure your sensor is rated for
            auto_calibrate (bool, optional): Weather or not to caliabrate the
                                                sensor on init assuming no
                                                pressure is currently applied
                                                and current sensor reading
                                                should be 0.

        """

        self.i2c_addr = i2c_addr
        self.max_pressure = max_pressure

        self.i2c = SMBus(1)

        self._sensor_data = None
        self.pressure = None
        self.status = None
        self._output_counts = None

        if auto_calibrate:
            self.calibrate()

    @property
    def sensor_data(self) -> list:
        """Returns the first for blocks from the sensor"""
        self._sensor_data = self.i2c.read_i2c_block_data(self.i2c_addr, 0, 4)

        return self._sensor_data

    def calibrate(self):
        """
            Sets the output_min to the current output_count of the sensor.
            I used this to set sensor ready starting point at 0 sense it
            appears as if Atmospheric affects the starting point
        """
        if self._output_counts is None:
            self.get_pressure()

        self.output_min = self._output_counts

    def get_pressure(self, sensor_data: list = None) -> float:
        """
            Parses the first two data bytes from the sensor data and
            converts output to pressure using formula found in API Comms pdf

            Args:
                sensor_data (list, optional): If sensor data is passed new
                                                 data will not be pulled from
                                                 the sensor
        """
        if sensor_data is None:
            sensor_data = self.sensor_data

        self._output_counts = ((sensor_data[0] & 0x3F) * 256) + sensor_data[1]
        self.pressure = (self._output_counts-self.output_min) \
            * self.max_pressure / (self.output_max-self.output_min)

        return self.pressure

    def get_status(self, sensor_data: list = None) -> float:
        """
            Parses the first data bytes from the sensor data and 
            converts gets the status bits

            Args:
                sensor_data (list, optional): If sensor data is passed new
                                                data will  not be pulled from
                                                the sensor
        """
        if sensor_data is None:
            sensor_data = self.sensor_data

        self.status = (sensor_data[0] & 0xC0) / 64