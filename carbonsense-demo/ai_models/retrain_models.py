"""
CarbonSense AI - Model Retraining Script
Retrains the models with the current scikit-learn version
"""

import os
import pandas as pd
from carbon_optimizer import CarbonOptimizer

def retrain_models():
    print("🔄 Starting model retraining process...")
    
    # Initialize optimizer
    optimizer = CarbonOptimizer()
    
    try:
        # Load training data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'demo_all_operations.csv')
        training_data = pd.read_csv(data_path)
        print(f"📊 Loaded {len(training_data)} training records")
        
        # Train the models
        print("\n🤖 Training models...")
        fuel_score, co2_score = optimizer.train_optimization_models(training_data)
        print(f"✅ Training complete:")
        print(f"   Fuel model R² score: {fuel_score:.3f}")
        print(f"   CO2 model R² score: {co2_score:.3f}")
        
        # Save the models
        models_path = os.path.join(os.path.dirname(__file__), 'carbonsense')
        optimizer.save_models(models_path)
        print("✅ Models saved successfully")
        
        # Test the models with sample data
        test_operation = {
            'speed_mph': 7.5,
            'engine_load_pct': 78,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.1,
            'operation_type': 'planter',
            'soil_type': 'loam',
            'terrain_type': 'rolling'
        }
        
        print("\n🧪 Testing models with sample operation...")
        optimization = optimizer.optimize_speed_for_operation(test_operation)
        if optimization:
            print(f"✅ Test successful:")
            print(f"   Input speed: {test_operation['speed_mph']} mph")
            print(f"   Optimal speed: {optimization['optimal_speed']} mph")
            print(f"   Fuel savings: {optimization['fuel_savings_percent']}%")
            print(f"   CO2 reduction: {optimization['co2_reduction_percent']}%")
        else:
            print("❌ Test failed: No optimization results")
            
    except Exception as e:
        print(f"❌ Error during retraining: {str(e)}")
        raise

if __name__ == "__main__":
    retrain_models()
