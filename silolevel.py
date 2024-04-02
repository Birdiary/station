import logging
import board
import busio
import time
import RPi.GPIO as GPIO

try:
    import adafruit_vl53l0x
except ModuleNotFoundError:
    print("Library adafruit-circuitpython-vl53l0x not found. Try to install via 'sudo apt install "
          "adafruit-circuitpython-vl53l0x' ")
    raise ModuleNotFoundError


class SiloLevelSensor:

    def __init__(self, gpio_gpio1: int = 4, gpio_xshut: int = 26, i2c_Address: hex = 0x29):
        """ initialize Sensor """
        self.logger = logging.getLogger('main.silolevel')
        self.gpio_gpio1: int = gpio_gpio1
        self.gpio_xshut: int = gpio_xshut

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_gpio1, GPIO.IN)
        GPIO.setup(self.gpio_xshut, GPIO.OUT)
        GPIO.output(self.gpio_xshut, True)  # enable Sensor for 1st initialisation

        # Initialize I2C and sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        try:
            self.sensor = adafruit_vl53l0x.VL53L0X(i2c=i2c, address=int(i2c_Address, 16))
            # GPIO.output(self.gpio_xshut, False)  # disable Sensor for reduce Power consumption
        except ValueError:
            print("Sensor not found under given address (normal: 0x29)")
            raise ValueError

    def read_Silolevel(self, empty_value: int = 0, full_value: int = 0):
        GPIO.output(self.gpio_xshut, True)
        time.sleep(0.0000000001)

        self.sensor = adafruit_vl53l0x.VL53L0X(busio.I2C(board.SCL, board.SDA))
        self.sensor.measurement_timing_budget = 200000

        silolevel = self.sensor.range
        print('Measured Value: ', silolevel)
        self.logger.debug('Measured Silolevel %s' % silolevel)
        GPIO.output(self.gpio_xshut, False)
        silolevel: float = 100 * (silolevel - empty_value) / (full_value - empty_value)

        if silolevel < 0.0:
            silolevel = 0
        else:
            silolevel = int(round(silolevel, 0))
        return silolevel  # value is in %

    def read_plain_value(self):
        GPIO.output(self.gpio_xshut, True)
        time.sleep(0.0000000001)
        self.sensor = adafruit_vl53l0x.VL53L0X(busio.I2C(board.SCL, board.SDA))
        self.sensor.measurement_timing_budget = 200000
        silolevel = self.sensor.range
        print('Measured Value: ', silolevel)
        self.logger.debug('Measured Silolevel %s' % silolevel)
        GPIO.output(self.gpio_xshut, False)
        return silolevel  # value is in %


if __name__ == '__main__':
    # Example usage
    gpio_gpio1_value = 4
    gpio_xshut_value = 26
    silo_sensor = SiloLevelSensor(gpio_gpio1_value, gpio_xshut_value)
    print('Silolevel %s Percent' % (silo_sensor.read_Silolevel(empty_value=210, full_value=56)))
