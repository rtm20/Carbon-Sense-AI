"""
Enhanced Telemetry Data Generator for CarbonSense AI Demo
Creates realistic, demo-ready agricultural equipment data
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random
import math

class CarbonSenseDataGenerator:
    def __init__(self):
        # EPA Standards and Real Equipment Specs
        self.co2_per_gallon_diesel = 22.4  # lbs CO2 per gallon
        self.diesel_cost_per_gallon = 3.85  # USD per gallon (current average)
        
        # John Deere 8R Series Specifications (Public Data)
        self.tractor_specs = {
            'model': 'John Deere 8370R',
            'max_hp': 370,
            'engine_displacement': 13.5,  # liters
            'fuel_tank_capacity': 265,     # gallons
            'max_fuel_flow': 25.0,         # gph at full load
            'idle_fuel_flow': 3.2,         # gph at idle
            'pto_hp': 320
        }
        
        # Implement specifications and efficiency factors
        self.implements = {
            'planter': {
                'width_ft': 24,
                'speed_range': (4.5, 8.0),
                'fuel_efficiency_factor': 0.75,  # More fuel needed for precision
                'operation_name': 'Spring Planting'
            },
            'cultivator': {
                'width_ft': 30,
                'speed_range': (6.0, 12.0),
                'fuel_efficiency_factor': 0.85,
                'operation_name': 'Field Cultivation'
            },
            'sprayer': {
                'width_ft': 60,
                'speed_range': (8.0, 15.0),
                'fuel_efficiency_factor': 0.95,  # Light load
                'operation_name': 'Chemical Application'
            },
            'tillage': {
                'width_ft': 18,
                'speed_range': (5.0, 9.0),
                'fuel_efficiency_factor': 0.60,  # Heavy load
                'operation_name': 'Deep Tillage'
            }
        }
        
        # Field characteristics (affects fuel consumption)
        self.field_conditions = {
            'soil_types': {
                'clay': {'resistance_factor': 1.2, 'moisture_sensitivity': 1.3},
                'loam': {'resistance_factor': 1.0, 'moisture_sensitivity': 1.0},
                'sand': {'resistance_factor': 0.8, 'moisture_sensitivity': 0.7}
            },
            'terrain_types': {
                'flat': {'slope_factor': 1.0},
                'rolling': {'slope_factor': 1.15},
                'hilly': {'slope_factor': 1.35}
            }
        }

    def generate_realistic_field(self, center_lat=41.5868, center_lon=-93.6250, 
                                size_acres=160, field_shape='rectangular'):
        """Generate realistic field boundaries and characteristics"""
        
        # Calculate field dimensions
        acres_to_sq_miles = 1/640
        field_sq_miles = size_acres * acres_to_sq_miles
        
        if field_shape == 'rectangular':
            # Typical midwest farm field: 2:1 ratio
            width_miles = math.sqrt(field_sq_miles * 2)
            height_miles = field_sq_miles / width_miles
        else:
            # Irregular field
            width_miles = math.sqrt(field_sq_miles) * random.uniform(0.8, 1.5)
            height_miles = field_sq_miles / width_miles
        
        # Convert to lat/lon (approximate)
        lat_per_mile = 1/69.0
        lon_per_mile = 1/(69.0 * math.cos(math.radians(center_lat)))
        
        # Generate field boundary
        boundary = [
            (center_lat + height_miles * lat_per_mile/2, center_lon - width_miles * lon_per_mile/2),
            (center_lat + height_miles * lat_per_mile/2, center_lon + width_miles * lon_per_mile/2),
            (center_lat - height_miles * lat_per_mile/2, center_lon + width_miles * lon_per_mile/2),
            (center_lat - height_miles * lat_per_mile/2, center_lon - width_miles * lon_per_mile/2)
        ]
        
        # Random field characteristics
        soil_type = random.choice(['clay', 'loam', 'sand'])
        terrain_type = random.choice(['flat', 'rolling', 'hilly'])
        
        return {
            'boundary': boundary,
            'acres': size_acres,
            'soil_type': soil_type,
            'terrain_type': terrain_type,
            'center': (center_lat, center_lon)
        }

    def generate_operation_path(self, field_info, implement_type, pattern='parallel'):
        """Generate realistic tractor operation path"""
        boundary = field_info['boundary']
        min_lat, max_lat = min(p[0] for p in boundary), max(p[0] for p in boundary)
        min_lon, max_lon = min(p[1] for p in boundary), max(p[1] for p in boundary)
        
        implement_width_ft = self.implements[implement_type]['width_ft']
        # Convert implement width to degrees (approximate)
        width_deg_lon = (implement_width_ft / 5280) / (69.0 * math.cos(math.radians(field_info['center'][0])))
        
        # Calculate number of passes needed
        field_width_deg = max_lon - min_lon
        num_passes = int(field_width_deg / width_deg_lon) + 1
        
        path_points = []
        
        for pass_num in range(num_passes):
            # Calculate current latitude for this pass
            current_lat = min_lat + (pass_num / num_passes) * (max_lat - min_lat)
            
            # Alternate direction for efficiency
            if pass_num % 2 == 0:
                lon_start, lon_end = min_lon, max_lon
            else:
                lon_start, lon_end = max_lon, min_lon
            
            # Generate points along this pass
            points_per_pass = 80
            for point_num in range(points_per_pass):
                progress = point_num / (points_per_pass - 1)
                current_lon = lon_start + progress * (lon_end - lon_start)
                
                # Add realistic GPS noise and steering variations
                lat_noise = random.normalvariate(0, 0.00002)  # ~2 meter accuracy
                lon_noise = random.normalvariate(0, 0.00002)
                
                path_points.append({
                    'lat': current_lat + lat_noise,
                    'lon': current_lon + lon_noise,
                    'pass_number': pass_num,
                    'point_in_pass': point_num
                })
        
        return path_points

    def calculate_dynamic_fuel_consumption(self, speed_mph, engine_load_pct, 
                                         implement_type, field_conditions, weather_factor=1.0):
        """Calculate realistic fuel consumption with multiple factors"""
        
        # Base fuel consumption curve (based on engine load)
        base_fuel_flow = self.tractor_specs['idle_fuel_flow']
        max_additional_flow = self.tractor_specs['max_fuel_flow'] - base_fuel_flow
        
        # Engine load affects fuel consumption exponentially
        load_factor = (engine_load_pct / 100) ** 1.3
        
        # Speed affects fuel consumption (optimal around 6-7 mph for most operations)
        optimal_speed = 6.5
        speed_efficiency = 1.0 + 0.02 * abs(speed_mph - optimal_speed)
        
        # Implement type affects fuel efficiency
        implement_efficiency = self.implements[implement_type]['fuel_efficiency_factor']
        
        # Field conditions impact
        soil_resistance = self.field_conditions['soil_types'][field_conditions['soil_type']]['resistance_factor']
        terrain_factor = self.field_conditions['terrain_types'][field_conditions['terrain_type']]['slope_factor']
        
        # Calculate final fuel consumption
        fuel_consumption = (base_fuel_flow + 
                          max_additional_flow * load_factor * 
                          speed_efficiency * 
                          (1/implement_efficiency) * 
                          soil_resistance * 
                          terrain_factor * 
                          weather_factor)
        
        return round(fuel_consumption, 2)

    def generate_complete_operation_dataset(self, implement_type='planter', 
                                          field_size_acres=160, duration_hours=8):
        """Generate complete telemetry dataset for demo"""
        
        # Generate field
        field_info = self.generate_realistic_field(size_acres=field_size_acres)
        
        # Generate operation path
        operation_path = self.generate_operation_path(field_info, implement_type)
        
        # Time calculations
        total_points = len(operation_path)
        seconds_per_point = (duration_hours * 3600) / total_points
        start_time = datetime.now() - timedelta(hours=duration_hours)
        
        # Weather conditions (affects fuel efficiency)
        weather_factor = random.uniform(0.9, 1.2)  # 10% variation for weather
        
        telemetry_records = []
        
        for i, point in enumerate(operation_path):
            current_time = start_time + timedelta(seconds=i * seconds_per_point)
            
            # Dynamic operating parameters
            speed_range = self.implements[implement_type]['speed_range']
            
            # Speed varies based on field conditions and operator behavior
            base_speed = random.uniform(speed_range[0], speed_range[1])
            
            # Adjust speed for turns and field ends
            if point['point_in_pass'] < 5 or point['point_in_pass'] > 75:  # Near field ends
                speed_mph = base_speed * 0.7  # Slow down for turns
            else:
                speed_mph = base_speed
            
            # Engine load varies with conditions
            base_load = random.uniform(55, 85)
            
            # Higher load for difficult conditions
            soil_factor = self.field_conditions['soil_types'][field_info['soil_type']]['resistance_factor']
            terrain_factor = self.field_conditions['terrain_types'][field_info['terrain_type']]['slope_factor']
            
            engine_load = min(base_load * soil_factor * terrain_factor, 95)
            
            # Calculate fuel consumption and emissions
            fuel_rate_gph = self.calculate_dynamic_fuel_consumption(
                speed_mph, engine_load, implement_type, 
                {'soil_type': field_info['soil_type'], 'terrain_type': field_info['terrain_type']},
                weather_factor
            )
            
            co2_rate_lbs_per_hour = fuel_rate_gph * self.co2_per_gallon_diesel
            fuel_cost_per_hour = fuel_rate_gph * self.diesel_cost_per_gallon
            
            # Additional realistic parameters
            rpm = 1400 + (engine_load / 100) * 700  # Realistic RPM range
            hydraulic_pressure = random.randint(1800, 2800)  # PSI
            coolant_temp = random.randint(185, 205)  # Fahrenheit
            
            # Calculate efficiency metrics
            acres_per_hour = (speed_mph * self.implements[implement_type]['width_ft']) / 43560 * 8.25
            fuel_per_acre = fuel_rate_gph / acres_per_hour if acres_per_hour > 0 else 0
            
            record = {
                'timestamp': current_time.isoformat(),
                'equipment_id': 'JD8370R_001',
                'operator_id': 'OP_001',
                'latitude': round(point['lat'], 6),
                'longitude': round(point['lon'], 6),
                'speed_mph': round(speed_mph, 1),
                'engine_load_pct': round(engine_load, 1),
                'engine_rpm': int(rpm),
                'fuel_rate_gph': fuel_rate_gph,
                'co2_rate_lbs_per_hour': round(co2_rate_lbs_per_hour, 2),
                'fuel_cost_per_hour': round(fuel_cost_per_hour, 2),
                'operation_type': implement_type,
                'operation_name': self.implements[implement_type]['operation_name'],
                'implement_width_ft': self.implements[implement_type]['width_ft'],
                'hydraulic_pressure_psi': hydraulic_pressure,
                'coolant_temp_f': coolant_temp,
                'soil_type': field_info['soil_type'],
                'terrain_type': field_info['terrain_type'],
                'field_acres': field_info['acres'],
                'pass_number': point['pass_number'],
                'acres_per_hour': round(acres_per_hour, 2),
                'fuel_per_acre': round(fuel_per_acre, 2),
                'weather_factor': round(weather_factor, 2)
            }
            
            telemetry_records.append(record)
        
        return pd.DataFrame(telemetry_records), field_info

# Demo data generation
if __name__ == "__main__":
    print("🚜 Generating CarbonSense AI Demo Dataset...")
    
    generator = CarbonSenseDataGenerator()
    
    # Generate multiple operation types for comprehensive demo
    operations = ['planter', 'cultivator', 'sprayer']
    all_data = []
    
    for operation in operations:
        print(f"📊 Generating {operation} operation data...")
        data, field_info = generator.generate_complete_operation_dataset(
            implement_type=operation,
            field_size_acres=160,
            duration_hours=8
        )
        all_data.append(data)
        
        # Save individual operation data
        filename = f"demo_{operation}_telemetry.csv"
        data.to_csv(filename, index=False)
        print(f"✅ Saved {len(data)} records to {filename}")
    
    # Combine all operations
    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data.to_csv("demo_all_operations.csv", index=False)
    
    print(f"\n🎯 Demo Dataset Summary:")
    print(f"Total Records: {len(combined_data)}")
    print(f"Operations: {', '.join(operations)}")
    print(f"Total Fuel Consumed: {combined_data['fuel_rate_gph'].sum():.1f} gallons")
    print(f"Total CO2 Emissions: {combined_data['co2_rate_lbs_per_hour'].sum():.1f} lbs")
    print(f"Total Fuel Cost: ${combined_data['fuel_cost_per_hour'].sum():.2f}")
    print(f"Average Speed: {combined_data['speed_mph'].mean():.1f} mph")
    
    print("\n✨ Demo dataset ready for CarbonSense AI!")
