import sys
import os
import unittest
import pandas as pd

# Add parent directory to path to import optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_models.carbon_optimizer import CarbonOptimizer

class TestOptimizerEdgeCases(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test case"""
        self.optimizer = CarbonOptimizer()
        # Load actual demo data
        try:
            self.test_data = pd.read_csv("data/demo_all_operations.csv")
            print(f"📊 Loaded {len(self.test_data)} test records")
        except FileNotFoundError:
            raise unittest.SkipTest("Demo data not found. Run demo_data_generator.py first.")
        
        # Train models with real data
        self.optimizer.train_optimization_models(self.test_data)

    def test_normal_operation(self):
        """Test optimization under normal conditions"""
        test_params = {
            'speed_mph': 7.5,
            'engine_load_pct': 75,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.0,
            'operation_type': 'planter',
            'soil_type': 'loam',
            'terrain_type': 'flat'
        }
        result = self.optimizer.optimize_speed_for_operation(test_params)
        
        # Check that all required fields are present
        required_fields = ['optimal_speed', 'fuel_savings_percent', 'co2_reduction_percent',
                         'optimal_fuel_rate', 'optimal_co2_rate', 'cost_savings_per_hour']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check value ranges
        self.assertTrue(3.0 <= result['optimal_speed'] <= 15.0)
        self.assertIsInstance(result['fuel_savings_percent'], float)
        self.assertIsInstance(result['cost_savings_per_hour'], float)

    def test_edge_case_constraints(self):
        """Test optimization with challenging constraints"""
        test_params = {
            'speed_mph': 7.5,
            'engine_load_pct': 75,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.0,
            'operation_type': 'planter',
            'soil_type': 'loam',
            'terrain_type': 'flat'
        }
        
        # Test with high target acres per hour
        result = self.optimizer.optimize_speed_for_operation(
            test_params, target_acres_per_hour=50.0
        )
        self.assertIsNotNone(result)
        
        # Verify result is within physical constraints
        self.assertTrue(3.0 <= result['optimal_speed'] <= 15.0)
        self.assertIsInstance(result['fuel_savings_percent'], float)
        self.assertGreaterEqual(result['fuel_savings_percent'], -100.0)  # Can't save more than 100%
        self.assertLess(result['fuel_savings_percent'], 100.0)  # Can't save more than 100%

    def test_boundary_conditions(self):
        """Test optimization at boundary conditions"""
        test_cases = [
            # Minimum speed
            {
                'speed_mph': 3.0,
                'engine_load_pct': 75,
                'implement_width_ft': 24,
                'field_acres': 160,
                'weather_factor': 1.0
            },
            # Maximum speed
            {
                'speed_mph': 15.0,
                'engine_load_pct': 75,
                'implement_width_ft': 24,
                'field_acres': 160,
                'weather_factor': 1.0
            },
            # Maximum load
            {
                'speed_mph': 7.5,
                'engine_load_pct': 95,
                'implement_width_ft': 24,
                'field_acres': 160,
                'weather_factor': 1.0
            }
        ]
        
        for case in test_cases:
            result = self.optimizer.optimize_speed_for_operation(case)
            self.assertIsNotNone(result)
            self.assertTrue(3.0 <= result['optimal_speed'] <= 15.0)

if __name__ == '__main__':
    unittest.main()
