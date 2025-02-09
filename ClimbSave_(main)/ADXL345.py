import math

class ADXL345_I2C:

    # Based on the following repository by dfrobot:
    #https://github.com/DFRobot/micropython-dflib/tree/master

    def __init__(self,i2c):
        self.TO_READ = 6
        self.addr = 0x53
        self.regAddress = 0x32
        self.i2c = i2c
        self.buff = bytearray(6)
        b = bytearray(1)
        

        # Sensor power configuration
        b[0] = 0
        self.i2c.writeto_mem(self.addr,0x2d,b)
        b[0] = 16
        self.i2c.writeto_mem(self.addr,0x2d,b)
        b[0] = 8
        self.i2c.writeto_mem(self.addr,0x2d,b)

    @property
    def xValue(self):
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        x = (int(self.buff[1]) << 8) | self.buff[0]
        if x > 32767:
            x -= 65536
        return x
    
    @property
    def yValue(self):
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        y = (int(self.buff[3]) << 8) | self.buff[2]
        if y > 32767:
            y -= 65536
        return y
     
    @property   
    def zValue(self): 
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        z = (int(self.buff[5]) << 8) | self.buff[4]
        if z > 32767:
            z -= 65536
        return z
           
    def RP_calculate(self,x,y,z):
        roll = math.atan2(y , z) * 57.3
        pitch = math.atan2((- x) , math.sqrt(y * y + z * z)) * 57.3
        return roll,pitch