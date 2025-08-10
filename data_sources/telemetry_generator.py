"""
Synthetic Agricultural Telemetry Data Generator for CarbonSense AI
Creates realistic tractor operation data for demonstration purposes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

class TractorTelemetryGenerator:
    def __init__(self):
        # EPA Standard: 22.4 lbs CO2 per gallon of diesel
        self.co2_per_gallon = 22.4
        
        # Typical tractor specifications (based on John Deere 8R series)
        self.engine_specs = {
            'max_horsepower': 370,
            'displacement_liters': 13.5,
            'fuel_tank_capacity': 265,  # gallons
            'max_fuel_flow': 25,  # gallons per hour at full load
        }
        
        # Field operation types and their characteristics
        self.operations = {
            'planting': {'speed_range': (4, 8), 'fuel_efficiency': 0.8, 'implement_width': 24},
            'cultivation': {'speed_range': (5, 12), 'fuel_efficiency': 0.9, 'implement_width': 30},
            'harvesting': {'speed_range': (3, 6), 'fuel_efficiency': 0.6, 'implement_width': 12},
            'spraying': {'speed_range': (8, 15), 'fuel_efficiency': 0.95, 'implement_width': 60}
        }

    def generate_field_boundary(self, center_lat=41.5868, center_lon=-93.6250, size_acres=160):
        """Generate realistic field boundary coordinates (default: Iowa location)"""
        # Convert acres to approximate lat/lon boundaries
        # 1 acre ≈ 0.00156 square miles ≈ 0.0015 degrees lat/lon
        field_size = np.sqrt(size_acres) * 0.012  # rough conversion
        
        # Create rectangular field with some irregularity
        corners = [
            (center_lat + field_size/2, center_lon - field_size/2),
            (center_lat + field_size/2, center_lon + field_size/2),
            (center_lat - field_size/2, center_lon + field_size/2),
            (center_lat - field_size/2, center_lon - field_size/2)
        ]
        
        return corners

    def generate_operation_path(self, field_boundary, operation_type='planting', passes=20):
        """Generate realistic tractor path through field"""
        min_lat = min([corner[0] for corner in field_boundary])
        max_lat = max([corner[0] for corner in field_boundary])
        min_lon = min([corner[1] for corner in field_boundary])
        max_lon = max([corner[1] for corner in field_boundary])
        
        # Generate back-and-forth pattern typical of field operations
        path_points = []
        for i in range(passes):
            if i % 2 == 0:  # Even passes: left to right
                start_lon, end_lon = min_lon, max_lon
            else:  # Odd passes: right to left
                start_lon, end_lon = max_lon, min_lon
            
            current_lat = min_lat + (i / passes) * (max_lat - min_lat)
            
            # Generate points along this pass
            for j in range(50):  # 50 points per pass
                lon = start_lon + (j / 49) * (end_lon - start_lon)
                # Add some noise for realistic GPS variation
                lat_noise = random.uniform(-0.0001, 0.0001)
                lon_noise = random.uniform(-0.0001, 0.0001)
                path_points.append((current_lat + lat_noise, lon + lon_noise))
        
        return path_points

    def calculate_fuel_consumption(self, speed_mph, engine_load_pct, operation_type):
        """Calculate realistic fuel consumption based on operating conditions"""
        base_consumption = self.engine_specs['max_fuel_flow']
        operation_efficiency = self.operations[operation_type]['fuel_efficiency']
        
        # Fuel consumption increases with engine load and speed
        load_factor = engine_load_pct / 100
        speed_factor = min(speed_mph / 10, 1.2)  # Diminishing returns at high speed
        
        fuel_rate = base_consumption * load_factor * speed_factor * (1 / operation_efficiency)
        return round(fuel_rate, 2)

    def generate_telemetry_data(self, operation_type='planting', duration_hours=8, 
                              field_size_acres=160, output_file=None):
        """Generate complete telemetry dataset for a field operation"""
        
        # Generate field and path
        field_boundary = self.generate_field_boundary(size_acres=field_size_acres)
        operation_path = self.generate_operation_path(field_boundary, operation_type)
        
        # Calculate time intervals
        total_points = len(operation_path)
        time_interval = (duration_hours * 3600) / total_points  # seconds per point
        
        telemetry_data = []
        start_time = datetime.now() - timedelta(hours=duration_hours)
        
        for i, (lat, lon) in enumerate(operation_path):
            current_time = start_time + timedelta(seconds=i * time_interval)
            
            # Generate realistic operating parameters
            speed_range = self.operations[operation_type]['speed_range']
            speed = random.uniform(speed_range[0], speed_range[1])
            
            # Engine load varies with terrain and conditions
            base_load = random.uniform(60, 85)
            terrain_factor = random.uniform(0.9, 1.1)
            engine_load = min(base_load * terrain_factor, 100)
            
            # Calculate fuel consumption and emissions
            fuel_rate = self.calculate_fuel_consumption(speed, engine_load, operation_type)
            co2_rate = fuel_rate * self.co2_per_gallon  # lbs CO2 per hour
            
            # RPM correlates with engine load
            rpm = 1400 + (engine_load / 100) * 800  # Range: 1400-2200 RPM
            
            record = {
                'timestamp': current_time.isoformat(),
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'speed_mph': round(speed, 1),
                'engine_load_pct': round(engine_load, 1),
                'engine_rpm': int(rpm),
                'fuel_rate_gph': fuel_rate,
                'co2_rate_lbs_per_hour': round(co2_rate, 2),
                'operation_type': operation_type,
                'implement_width_ft': self.operations[operation_type]['implement_width'],
                'hydraulic_pressure_psi': random.randint(2000, 3000),
                'coolant_temp_f': random.randint(180, 210)
            }
            
            telemetry_data.append(record)
        
        # Convert to DataFrame
        df = pd.DataFrame(telemetry_data)
        
        # Save to file if specified
        if output_file:
            if output_file.endswith('.csv'):
                df.to_csv(output_file, index=False)
            elif output_file.endswith('.json'):
                df.to_json(output_file, orient='records', indent=2)
        
        return df

    def generate_optimization_scenarios(self, base_data):
        """Generate before/after scenarios showing optimization benefits"""
        optimized_data = base_data.copy()
        
        # Scenario 1: Speed optimization
        speed_optimized = optimized_data[optimized_data['speed_mph'] > 7].copy()
        speed_optimized['speed_mph'] = 6.2  # Optimal speed
        speed_optimized['fuel_rate_gph'] = speed_optimized['fuel_rate_gph'] * 0.82  # 18% reduction
        speed_optimized['co2_rate_lbs_per_hour'] = speed_optimized['fuel_rate_gph'] * self.co2_per_gallon
        
        # Scenario 2: Route optimization (reduced overlap, better patterns)
        route_optimized = optimized_data.copy()
        route_optimized['fuel_rate_gph'] = route_optimized['fuel_rate_gph'] * 0.85  # 15% reduction from better routing
        route_optimized['co2_rate_lbs_per_hour'] = route_optimized['fuel_rate_gph'] * self.co2_per_gallon
        
        return {
            'baseline': base_data,
            'speed_optimized': speed_optimized,
            'route_optimized': route_optimized
        }

# Example usage
if __name__ == "__main__":
    generator = TractorTelemetryGenerator()
    
    # Generate sample data for spring planting
    print("Generating synthetic telemetry data for spring planting operation...")
    planting_data = generator.generate_telemetry_data(
        operation_type='planting',
        duration_hours=8,
        field_size_acres=160,
        output_file='spring_planting_telemetry.csv'
    )
    
    print(f"Generated {len(planting_data)} data points")
    print("\nSample data:")
    print(planting_data.head())
    
    # Calculate summary statistics
    total_fuel = planting_data['fuel_rate_gph'].mean() * 8  # 8 hour operation
    total_co2 = total_fuel * generator.co2_per_gallon
    avg_speed = planting_data['speed_mph'].mean()
    
    print(f"\nOperation Summary:")
    print(f"Total Fuel Consumed: {total_fuel:.1f} gallons")
    print(f"Total CO2 Emissions: {total_co2:.1f} lbs")
    print(f"Average Speed: {avg_speed:.1f} mph")
    print(f"Average Fuel Rate: {planting_data['fuel_rate_gph'].mean():.1f} gph")
