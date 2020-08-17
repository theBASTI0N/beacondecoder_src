import math
from binascii import hexlify

print("===================")
print("theBASTI0N")
print("beacondecoder: v0.6.2")
print("===================")

#inspired from https://github.com/Scrin/RuuviCollector
def dewPoint(temperature, relativeHumidity):
    v = math.log(relativeHumidity / 100 * equilibriumVaporPressure(temperature) / 611.2)
    return -243.5 * v / (v - 17.67)

#inspired from https://github.com/Scrin/RuuviCollector
def absoluteHumidity(temperature, relativeHumidity):
    return equilibriumVaporPressure(temperature) * relativeHumidity * 0.021674 / (273.15 + temperature)

#inspired from https://github.com/Scrin/RuuviCollector
def equilibriumVaporPressure(temperature):
    return 611.2 * math.exp(17.67 * temperature / (243.5 + temperature))

#inspired from https://github.com/Scrin/RuuviCollector
def airDensity(temperature, relativeHumidity, pressure):
    return 1.2929 * 273.15 / (temperature + 273.15) * (pressure - 0.3783 * relativeHumidity / 100 * equilibriumVaporPressure(temperature)) / 101300

#inspired from https://github.com/Scrin/RuuviCollector
def angleBetweenVectorComponentAndAxis(vectorComponent, vectorLength):
    if vectorComponent == None or vectorLength == None or vectorLength == 0:
        return None
    return math.degrees(math.acos(vectorComponent / vectorLength))

def twos_complement(hexstr,bits):
     value = int(hexstr,16)
     if value & (1 << (bits-1)):
         value -= 1 << bits
     return value

def rshift(val, n):
    return (val % 0x100000000) >> n

def decode(data, ruuviPlus=False):
    format = 0
    if '990405' in data:
        format = 5
        d = str(data)
        d = d[14:]
        temperature = twos_complement(d[2:6], 16) * 0.005
        humidity = int(d[6:10], 16) * 0.0025
        pressure = int(d[10:14], 16) + 50000
        pressure = pressure / 100
        x = twos_complement(d[14:18], 16)/1000
        y = twos_complement(d[18:22], 16)/1000
        z = twos_complement(d[22:26], 16)/1000
        totalACC = math.sqrt(x * x + y * y + z * z)
        power_bin = bin(int(d[26:30], 16))
        battery_voltage = ((int(power_bin[:13], 2)) + 1600) / 1000
        tx_power = int(power_bin[13:], 2) * 2 - 40
        mC = int(d[30:32], 16)
        measureSeq = int(d[32:36], 16)
        
        dMSG = {'dataFormat' : format,
                'temperature' : temperature,
                'humidity' : humidity,
                'pressure' : pressure,
                'accelerationX' : x, 'accelerationY' :y, 'accelerationZ' : z,
                'accelerationTotal' : totalACC,
                'batteryVoltage' : battery_voltage,
                'tx' : tx_power,
                'movementCounter' : mC,
                'measurementSequence' : measureSeq,
                }
        
        if(ruuviPlus):
            evp = equilibriumVaporPressure(temperature)
            dMSG['equilibriumVaporPressure'] = evp
            aH = absoluteHumidity(temperature, humidity)
            dMSG['absoluteHumidity'] = aH
            dP = dewPoint(temperature, humidity)
            dMSG['dewPoint'] = dP
            airD = airDensity(temperature, humidity, pressure)
            dMSG['airDensity'] = airD
            angleX = angleBetweenVectorComponentAndAxis(x, totalACC)
            angleY = angleBetweenVectorComponentAndAxis(y, totalACC)
            angleZ = angleBetweenVectorComponentAndAxis(z, totalACC)
            if (angleX is not None):
                dMSG['accelerationAngleFromX'] = angleX
            else:
                dMSG['accelerationAngleFromX'] = 0
            if (angleY is not None):
                dMSG['accelerationAngleFromY'] = angleY
            else:
                dMSG['accelerationAngleFromY'] = 0
            if (angleZ is not None):
                dMSG['accelerationAngleFromZ'] = angleZ
            else:
                dMSG['accelerationAngleFromZ'] = 0

        return dMSG
    elif '990403' in data: #Ruuvi RAWv1
        format = 3
        d = str(data)
        d = d[14:]
        humidity = int(d[2:4], 16) * 0.5
        temperature = twos_complement(d[4:6], 16) + int(d[6:8], 16) / 100
        if temperature > 128:
            temperature -= 128
            temperature = round(0 - temperature, 2)
        pressure = int(d[8:12], 16) + 50000
        pressure = pressure / 100
        x = twos_complement(d[12:16], 16)/1000
        y = twos_complement(d[16:20],16)/1000
        z = twos_complement(d[20:24], 16)/1000
        totalACC = math.sqrt(x * x + y * y + z * z)
        battery_voltage = twos_complement(d[24:28], 16)/1000
       
        dMSG = {'dataFormat' : format,
                'temperature' : temperature,
                'humidity' : humidity,
                'pressure' : pressure,
                'accelerationX' : x, 'accelerationY' :y, 'accelerationZ' : z,
                'accelerationTotal' : totalACC,
                'batteryVoltage' : battery_voltage,
                }
        
        if(ruuviPlus):
            evp = equilibriumVaporPressure(temperature)
            dMSG['equilibriumVaporPressure'] = evp
            aH = absoluteHumidity(temperature, humidity)
            dMSG['absoluteHumidity'] = aH
            dP = dewPoint(temperature, humidity)
            dMSG['dewPoint'] = dP
            airD = airDensity(temperature, humidity, pressure)
            dMSG['airDensity'] = airD
            angleX = angleBetweenVectorComponentAndAxis(x, totalACC)
            angleY = angleBetweenVectorComponentAndAxis(y, totalACC)
            angleZ = angleBetweenVectorComponentAndAxis(z, totalACC)
            if (angleX is not None):
                dMSG['accelerationAngleFromX'] = angleX
            else:
                dMSG['accelerationAngleFromX'] = 0
            if (angleY is not None):
                dMSG['accelerationAngleFromY'] = angleY
            else:
                dMSG['accelerationAngleFromY'] = 0
            if (angleZ is not None):
                dMSG['accelerationAngleFromZ'] = angleZ
            else:
                dMSG['accelerationAngleFromZ'] = 0

        return dMSG
    elif 'AAFE2000' in data:

        format = 1
        d = str(data)
        d = d.split("AAFE2000")[1]
        battery_voltage = int(d[1:4], 16) / 1000
        temp1= twos_complement(d[4:6], 8)
        temp2 = int(d[6:8], 16) / 256
        temperature = temp1 + temp2
        advCnt = int(d[8:12], 16)
        secCnt = int(d[12:16], 16)

        dMSG = {  'dataFormat' : format,
                'temperature' : temperature,
                'advCnt' : advCnt,
                'secCnt' : secCnt,
                'batteryVoltage' :battery_voltage
                }
        return dMSG
    else:
        dMSG = {  'dataFormat' : format
                }

        return dMSG
