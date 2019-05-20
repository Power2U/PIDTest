import time
import PID

# District heating
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
        
class BuildingTemp:
    def __init__(self):
        self.thermal_capacity = 0
        self.thermal_conductivity = 0
        self.irradiate_area = 0
        #g_factor: non-dimensional factor
        self.g_factor = 0
        self.solar_gain = 0
        self.heat_loss = 0
        self.disctrict_heating_gain = 0
        self.current_time = time.time()
        self.last_time = self.current_time
        self.last_indoor_temperature = 0
        
        
    def computeTemperature(self, time_ratio, solar_radiance, district_heating_ini):

        self.current_time = time.time()
        delta_time = (self.current_time - self.last_time) * time_ratio
        
        self.solar_gain = self.g_factor * self.irradiate_area * solar_radiance * delta_time
        self.heat_loss = self.thermal_conductivity * (self.last_indoor_temperature - district_heating_ini.outside_temperature) * delta_time
        # Thermal capacity of water = 4186 J/kg/degree
        # Density of water = 997 kg/m^3
        self.district_heating_gain = 4186 * 997 * district_heating_ini.district_total_inflow \
            * (district_heating_ini.district_inflow_temperature - district_heating_ini.district_outflow_temperature) * delta_time
        self.last_indoor_temperature = self.last_indoor_temperature + (self.disctrict_heating_gain \
            + self.solar_gain - self.heat_loss) / self.thermal_capacity

        # Remember last time and last error for next calculation
        self.last_time = self.current_time
        
        return self.last_indoor_temperature
    
    def setThermalCapacity(self, thermal_capacity):
        self.thermal_capacity = thermal_capacity
        
    def setThermalConductivity(self, thermal_conductivity):
        self.thermal_conductivity = thermal_conductivity
        
    def setIrradiateArea(self, irradiate_area):
        self.irradiate_area = irradiate_area
    
    def setGFactor(self, g_factor):
        self.g_factor = g_factor

def run(building_simulation, district_heating_ini, time_ratio, P, I, D, set_point, sample_time, total_sampling, solar_radiance):

    pid = PID.PID(P, I, D)
    
    pid.SetPoint = set_point
    pid.setSampleTime(sample_time)   
    feedback = district_heating_ini.average_indoor_temperature
    district_inflow_temperature = district_heating_ini.district_inflow_temperature
        
    feedback_list = []
    time_list = []
    output_list = []
    
    print("start testing....")
    for i in range(1, total_sampling):
        pid.update(feedback)
        output = pid.output
        district_inflow_temperature += district_inflow_temperature + output
        #time_ratio, solar_radiance, outside_temperature, district_total_inflow, district_inflow_temperature, district_outflow_temperature
        feedback = building_simulation.computeTemperature(time_ratio, solar_radiance, district_heating_ini)      
        time.sleep(0.02)
        
        feedback_list.append(feedback)
        output_list.append(output)
        time_list.append(i)
        
    print(feedback_list, output_list, time_list)
            
if __name__ == "__main__":
        
    building_simulation = BuildingTemp()
    building_simulation.setThermalCapacity(1000)
    building_simulation.setThermalConductivity(1.13)
    building_simulation.setGFactor(0.15)
    building_simulation.setIrradiateArea(10)

    district_heating_ini = DistrictHeating()
    district_heating_ini.setAverageIndoorTemperature(18)
    district_heating_ini.setDistrictInflowTemperature(60)
    district_heating_ini.setDistrictOutflowTemperature(30)
    district_heating_ini.setDistrictInflow(0.1)
    district_heating_ini.setTotalInflow(10)
    
    P = 1.4
    I = 1
    D = 0.001
    set_point = 20
    sample_time = 0.01
    total_sampling = 10
    time_ratio = 30 * 60 / 0.02
    solar_radiance = 10
    
    run(building_simulation, district_heating_ini, time_ratio, P, I, D, set_point, sample_time, total_sampling, solar_radiance)
    
    print("finish")
