import time
import PID
import matplotlib.pyplot as plt

class DistrictHeating:
    
    def __init__(self):
        self.outside_temperature = 0
        self.district_inflow = 0
        self.district_inflow_temperature = 0
        self.district_outflow_temperature = 0
        
        # The idea is to read indoor temperature from Cassandra. There is only heating_tseries to store the data related 
        # with heating system, so the indoor temperature is assumed stored here. However, this can be adjusted in the
        # future when new data structure is created.
        self.average_indoor_temperature = 0
        self.district_total_inflow = 0
        self.current_time = time.time()
        self.last_time = self.current_time
        self.inflow_temp_max = 0
        self.inflow_temp_min = 0
    
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
        
            
class BuildingTemp:
    
    def __init__(self, district_heating_ini):
        self.thermal_capacity = 0
        self.thermal_conductivity = 0
        self.irradiate_area = 0
        self.g_factor = 0
        self.solar_gain = 0
        self.heat_loss = 0
        self.disctrict_heating_gain = 0
        self.current_time = time.time()
        self.last_time = 0
        
        # Initialize indoor temperature         
        self.last_indoor_temperature = district_heating_ini.average_indoor_temperature
 
    # The method is used to estimate indoor temperature based on a simplified model
    # Net heat gain =  district heating gain + solar gain - heat losses     
    def computeTemperature(self, time_ratio, solar_radiance, water_capacity, water_density, district_heating_ini):

        self.current_time = time.time()
        
        # time_ratio is used to scale the simulation time step        
        delta_time = time_ratio
        
        # solar_gain: kWh
        # g_factor: non-dimensional factor
        # irradiate_area: m^2
        # solar_radiance: kW/m^2
        self.solar_gain = self.g_factor * self.irradiate_area * solar_radiance * delta_time
        
        # heat_loss: kWh
        # thermal_conductivity: kW/degree       
        self.heat_loss = self.thermal_conductivity * (self.last_indoor_temperature - district_heating_ini.outside_temperature) * delta_time
        
        # water_capacity: kJ/kg/degree
        # water_density: kg/m^3
        # district_total_inflow: m^3/s
        # district_heat_gain: kWh       
        self.district_heating_gain = water_capacity * water_density * district_heating_ini.district_total_inflow \
            * (district_heating_ini.district_inflow_temperature - district_heating_ini.district_outflow_temperature) * delta_time
        
        # building thermal_capacity: kWh/degree
        # Update indoor temperature by adding the temperature change due to net heat gain        
        self.last_indoor_temperature += (self.district_heating_gain + self.solar_gain - self.heat_loss) / self.thermal_capacity

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

# The method is used to simulate adjusted inflow temperature based on PID logic
# The objective is to adjust indoor temperature towards the set point

def run_building_sim(building_simulation, district_heating_ini, time_ratio, P, I, D, set_point, sample_time, total_sampling,\
        water_capacity, water_densidty, solar_radiance, outside_temperature):

    pid = PID.PID(P, I, D)
    
    pid.SetPoint = set_point
    pid.setSampleTime(sample_time) 
    pid.windup_guard = windup_guard  
    pid.setTimeRatio(time_ratio)
    
    # Initialize feedback i.e. indoor temperature   
    feedback = district_heating_ini.average_indoor_temperature
        
    feedback_list = []
    time_list = []
    output_list = []
    inflow_temp_list = []
    outside_temperature_list = []
    
    print("start testing....")
    for i in range(1, total_sampling):
        
        time_list.append(i)
        feedback_list.append(feedback)
        district_heating_ini.outside_temperature = outside_temperature[i-1]  
        
        pid.update(feedback)
        output = pid.output
        output_list.append(output)
        
        # Update manipulated_inflow_temperature based on PID output        
        manipulated_inflow_temperature = district_heating_ini.district_inflow_temperature + output
        
        # manipulated_inflow_temperature has upper and lower limits       
        if manipulated_inflow_temperature > district_heating_ini.inflow_temp_max:
            district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_max   
        elif manipulated_inflow_temperature < district_heating_ini.inflow_temp_min:
            district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_min
        else:
            district_heating_ini.district_inflow_temperature = manipulated_inflow_temperature
       
        # Simulate indoor temperature for next time point based on manipulated_inflow_temperature        
        feedback = building_simulation.computeTemperature(time_ratio, solar_radiance[i-1], water_capacity, water_densidty, district_heating_ini)      
        
        time.sleep(0.02)
    
        inflow_temp_list.append(district_heating_ini.district_inflow_temperature)
        outside_temperature_list.append(district_heating_ini.outside_temperature)
       
    print(feedback_list)
    print(output_list)
    print(time_list)
    print(inflow_temp_list)
    print(outside_temperature_list)

    # plot results

    plt.figure(1)
    plt.subplot(411)
    plt.plot(time_list, feedback_list, 'o-')
    plt.hlines(set_point, 1, len(time_list), 'red')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('indoor temperature')
    
    plt.subplot(412)
    plt.plot(time_list, output_list, 'o-')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('PID output')
    
    plt.subplot(413)
    plt.plot(time_list, inflow_temp_list, 'o-')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('Adjusted inflow temperature')

    plt.subplot(414)
    plt.plot(time_list, outside_temperature_list, 'o-')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('Outside temperature')    
    
    plt.subplots_adjust(hspace=0.5)

    plt.show()

#    The method is used to simulate manipulated inflow temperature base on PID logic
#    The objective is to adjust indoor temperature within a temperature range

def run_building_sim_range(building_simulation, district_heating_ini, time_ratio, P, I, D, upLim, lowLim, sample_time, total_sampling,\
        solar_radiance, water_capacity, water_densidty):
 
    pid = PID.PID(P, I, D)
     
    pid.upLim = upLim
    pid.lowLim = lowLim
    pid.setSampleTime(sample_time) 
    pid.windup_guard = windup_guard  
     
    # Initialize indoor temperature     
    feedback = district_heating_ini.average_indoor_temperature
         
    feedback_list = []
    time_list = []
    output_list = []
    inflow_temp_list = []
    outside_temperature_list = []
     
    print("start testing....")
     
    for i in range(1, total_sampling):
        time_list.append(i)
        feedback_list.append(feedback)
        district_heating_ini.outside_temperature = outside_temperature[i-1]  
         
           
        pid.update_range(feedback)
        output = pid.output
        output_list.append(output)

        # Update manipulated_inflow_temperature based on PID output  
        manipulated_inflow_temperature = district_heating_ini.district_inflow_temperature + output
         
        # manipulated_inflow_temperature has upper and lower limits         
        if manipulated_inflow_temperature > district_heating_ini.inflow_temp_max:
            district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_max   
        elif manipulated_inflow_temperature < district_heating_ini.inflow_temp_min:
            district_heating_ini.district_inflow_temperature = district_heating_ini.inflow_temp_min
        else:
            district_heating_ini.district_inflow_temperature = manipulated_inflow_temperature
        
        # Simulate indoor temperature for next time point based on manipulated_inflow_temperature         
        feedback = building_simulation.computeTemperature(time_ratio, solar_radiance[i-1], water_capacity, water_densidty, district_heating_ini)      
         
        time.sleep(0.02)
             
        inflow_temp_list.append(district_heating_ini.district_inflow_temperature)
        outside_temperature_list.append(district_heating_ini.outside_temperature)
         
    print(feedback_list)
    print(output_list)
    print(time_list)
    print(inflow_temp_list)
    print(outside_temperature_list)
 
    # plot results
 
    plt.figure(1)
    plt.subplot(411)
    plt.plot(time_list, feedback_list, 'b--')
    plt.hlines(upLim, 1, len(time_list), 'red')
    plt.hlines(lowLim, 1, len(time_list), 'red')
 
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('indoor temperature')
     
    plt.subplot(412)
    plt.plot(time_list, output_list, 'b--')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('PID output')
     
    plt.subplot(413)
    plt.plot(time_list, inflow_temp_list, 'b--')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('Adjusted inflow temperature')
 
    plt.subplot(414)
    plt.plot(time_list, outside_temperature_list, 'b--')
    plt.ylabel('$^\circ$C').set_rotation(0)
    plt.title('Outside temperature')
     
    plt.subplots_adjust(hspace=0.5)
 
    plt.show()  
              
# The method shows an example for simulation

if __name__ == "__main__":

# Initialize a district heating system 
       
    district_heating_ini = DistrictHeating()
    district_heating_ini.setAverageIndoorTemperature(20.5)
    district_heating_ini.setDistrictInflowTemperature(60)
    district_heating_ini.setDistrictOutflowTemperature(30)
    district_heating_ini.setTotalInflow(0.001)
    district_heating_ini.setInflowTempMax(80)
    district_heating_ini.setInflowTempMin(40)
    district_heating_ini.setOutsideTemperature(0)

# Initialize a building envelope
    
    building_simulation = BuildingTemp(district_heating_ini)
    building_simulation.setThermalCapacity(12)
    building_simulation.setThermalConductivity(5)

    building_simulation.setGFactor(0.15)
    building_simulation.setIrradiateArea(20)

# Set other parameters

    P = 2
    I = 0
    D = 0
    sample_time = 0.001
    total_sampling = 25
    windup_guard = 10
    
    set_point = 20
    upLim = 21
    lowLim = 19
    time_ratio = 1

    solar_radiance = [0, 0, 0, 0, 0, 0, 0, 0, 0.2, 0.2, 1, 1, 1, 0.1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    outside_temperature = [-5, -5, -4, -4, -4, -3, -3, -3, -2, -2, -2, -1, 0, 0, 0, -2, -3, -3, -3, -4, -4, -5, -5, -5] 
    water_capacity = 4.18
    water_density = 997
    
    run_building_sim(building_simulation, district_heating_ini, time_ratio, P, I, D, set_point, sample_time, total_sampling, \
        water_capacity, water_density, solar_radiance, outside_temperature)
    
#    run_building_sim_range(building_simulation, district_heating_ini, time_ratio, P, I, D, upLim, lowLim, sample_time, total_sampling, \
#        solar_radiance, water_capacity, water_density)    

    print("finish")
