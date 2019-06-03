import time
import PID
import random

class Sensor:
    
    def __init__(self, temperature_sensor_1, temperature_sensor_2, time_sensor_1, time_sensor_2):
        self.temperature_sensor_1 = temperature_sensor_1
        self.temperature_sensor_2 = temperature_sensor_2
        self.time_sensor_1 = time_sensor_1
        self.time_sensor_2 = time_sensor_2
        self.feedback = 0
    
    def setTemperatureSensor1(self, deviation_sensor_1):
        if self.temperature_sensor_1 is None:
            print('no value is received from sensor 1')
            return
        
        self.temperature_sensor_1 += deviation_sensor_1
        
    def setTemperatureSensor2(self, deviation_sensor_2):
        if self.temperature_sensor_2 is None:
            print('no value is received from sensor 2')
            return
        
        self.temperature_sensor_2 += deviation_sensor_2
    
    # The feedback to PID is considered as the average values of the two sensors
    # Other methods for calculating feedback could be designed here
    
    def setFeedback(self):
        
        if self.temperature_sensor_1 is None:
            print('no value is received from sensor 1')
            return
           
        if self.temperature_sensor_2 is None:
            print('no value is received from sensor 2')
            return
        
        self.feedback = (self.temperature_sensor_1 + self.temperature_sensor_2) / 2

class DistrictHeating:
    
    def __init__(self):
        self.outside_temperature = 0
        self.district_inflow = 0
        self.district_inflow_temperature = 0
        self.district_outflow_temperature = 0
        self.average_indoor_temperature = 0
        self.district_total_inflow = 0
        self.current_time = time.time()
        self.last_time = self.current_time
        self.inflow_temp_max = 0
        self.infleow_temp_min = 0
    
    def setOutsideTemperature(self, outside_temperature):
        self.outside_temperature = outside_temperature
        
    def setDistrictInflow(self, district_inflow):
        self.district_inflow = district_inflow
        
    def setTotalInflow(self, district_total_inflow):
        self.district_total_inflow = district_total_inflow
        
    def setDistrictInflowTemperature(self, district_inflow_temperature):
        self.district_inflow_temperature = district_inflow_temperature
    
    def setDistrictOutflowTemperature(self, district_outflow_temperature):
        self.district_outflow_temperature = district_outflow_temperature
        
    def setAverageIndoorTemperature(self, average_indoor_temperature):
        self.average_indoor_temperature = average_indoor_temperature

    def setInflowTempMax(self, inflow_temp_max):
        self.inflow_temp_max = inflow_temp_max
        
    def setInflowTempMin(self, inflow_temp_min):
        self.inflow_temp_min = inflow_temp_min   
        
def run(sensor, district_heating_ini, P, I, D, set_point, sample_time):

    pid = PID.PID(P, I, D)
    pid.SetPoint = set_point
    pid.setSampleTime(sample_time) 
    time.sleep(0.12)
    
    feedback = sensor.feedback
        
    print("start testing....")
             
    pid.update(feedback)
    output = pid.output
    
    # Update district_inflow_temperature based on PID output  
    
    district_heating_ini.district_inflow_temperature += output
        
    # manipulated_inflow_temperature has upper and lower limits
        
    if district_heating_ini.district_inflow_temperature > district_heating_ini.inflow_temp_max:
        district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_max   
    elif district_heating_ini.district_inflow_temperature < district_heating_ini.inflow_temp_min:
        district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_min
        
    print(feedback)
    print(output)
    print(district_heating_ini.district_inflow_temperature)
    print("finish")

# The main method shows an example of the test with the sensor values

if __name__ == "__main__":

    # Initiate a district heating system 
    # Input: district_inflow temperature, inflow_temp_max, inflow_temp_min
       
    district_heating_ini = DistrictHeating()
    district_heating_ini.setDistrictInflowTemperature(60)
    district_heating_ini.setInflowTempMax(70)
    district_heating_ini.setInflowTempMin(50)

    # Initiate a sensor measurement
    # Input: temperature_sensor_1, temperature_sensor_2, time_sensor_1, time_sensor_2
    # Introduce a random value to simulate indoor temperature dynamics

    sensor = Sensor(18, 16, 0, 0)
    deviation_sensor_1 = random.normalvariate(0, 0.2)
    deviation_sensor_2 = random.normalvariate(0, 0.5)
    sensor.setTemperatureSensor1(deviation_sensor_1)
    sensor.setTemperatureSensor2(deviation_sensor_2)
    sensor.setFeedback()

    # Initiate parameters

    P = 2
    I = 1
    D = 0
    sample_time = 0.01    
    set_point = 20
    
    run(sensor, district_heating_ini, P, I, D, set_point, sample_time)  

