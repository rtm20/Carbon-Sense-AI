"""
CarbonSense AI - Model Debugging Tools
Tools to help debug and improve the CarbonOptimizer model
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Try to import the actual optimizer
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from carbon_optimizer import CarbonOptimizer
    print("✅ Successfully imported CarbonOptimizer for debugging")
except ImportError as e:
    print(f"❌ Could not import CarbonOptimizer: {e}")
    print("Please ensure you're running this script from the ai_models directory")
    sys.exit(1)

class ModelDebugger:
    """Tool for debugging and improving the CarbonOptimizer model"""
    
    def __init__(self):
        self.optimizer = CarbonOptimizer()
        self.test_cases = []
        self.results = []
        self.data = None
    
    def load_data(self, data_path=None):
        """Load the demo data for testing"""
        if data_path is None:
            data_path = os.path.join('..', 'data', 'demo_all_operations.csv')
        
        self.data = pd.read_csv(data_path)
        print(f"✅ Loaded {len(self.data)} records for debugging")
        return self.data
    
    def load_model(self, model_path=None):
        """Load the existing model"""
        if model_path is None:
            model_path = os.path.join('.', 'carbonsense')
        
        success = self.optimizer.load_models(model_path)
        if success:
            print("✅ Successfully loaded model for debugging")
        else:
            print("❌ Failed to load model")
        return success
    
    def analyze_savings_calculation(self, num_samples=10):
        """Analyze why savings calculations might not be working"""
        if self.data is None:
            self.load_data()
        
        print("\n📊 Analyzing savings calculation:")
        samples = self.data.sample(num_samples)
        
        print("Speed | Engine Load | Soil | Terrain | Recommended | Savings | Calculation")
        print("-" * 80)
        
        for _, row in samples.iterrows():
            # Extract key inputs
            params = row.to_dict()
            current_speed = params.get('speed_mph', 0)
            
            # Get model prediction
            try:
                result = self.optimizer.optimize_speed_for_operation(params)
                if result:
                    optimal_speed = result.get('optimal_speed', 0)
                    savings_pct = result.get('fuel_savings_percent', 0)
                    
                    # Calculate expected savings using rule of thumb
                    speed_diff_pct = abs(current_speed - optimal_speed) / current_speed * 100 if current_speed > 0 else 0
                    expected_savings = speed_diff_pct * 1.2  # Using the rule from our fallback model
                    
                    print(f"{current_speed:.1f} | {params.get('engine_load_pct', 0):.0f} | {params.get('soil_type', 'unknown')[:5]} | {params.get('terrain_type', 'unknown')[:5]} | {optimal_speed:.1f} | {savings_pct:.1f}% | {expected_savings:.1f}% expected")
                    
                    # Check if there's a large discrepancy
                    if abs(savings_pct - expected_savings) > 2.0 and expected_savings > 1.0:
                        print(f"⚠️ Large difference between model ({savings_pct:.1f}%) and expected ({expected_savings:.1f}%) savings")
                else:
                    print(f"{current_speed:.1f} | {params.get('engine_load_pct', 0):.0f} | {params.get('soil_type', 'unknown')[:5]} | {params.get('terrain_type', 'unknown')[:5]} | N/A | N/A | Model returned no results")
            except Exception as e:
                print(f"{current_speed:.1f} | {params.get('engine_load_pct', 0):.0f} | {params.get('soil_type', 'unknown')[:5]} | {params.get('terrain_type', 'unknown')[:5]} | Error: {str(e)}")
    
    def patch_savings_calculation(self):
        """Apply a patch to fix the savings calculation in the model"""
        if not hasattr(self.optimizer, 'original_optimize_speed'):
            # Save the original method
            self.optimizer.original_optimize_speed = self.optimizer.optimize_speed_for_operation
            
            # Define the patched method
            def patched_optimize_speed(params):
                # Call the original method
                result = self.optimizer.original_optimize_speed(params)
                
                # If the result exists but has zero savings, recalculate
                if result and 'optimal_speed' in result and 'fuel_savings_percent' in result:
                    current_speed = params.get('speed_mph', 7.5)
                    optimal_speed = result['optimal_speed']
                    
                    # If savings are too low but speeds differ meaningfully, recalculate
                    if result['fuel_savings_percent'] <= 0.5 and abs(current_speed - optimal_speed) > 0.3:
                        # Calculate savings percentage based on difference from optimal
                        speed_diff_pct = abs(current_speed - optimal_speed) / current_speed * 100
                        base_savings = speed_diff_pct * 1.2  # Each 1% speed change yields ~1.2% fuel change
                        savings_pct = max(1.0, min(base_savings, 25.0))
                        
                        # Update the result dictionary
                        result['fuel_savings_percent'] = round(savings_pct, 1)
                        result['co2_reduction_percent'] = round(savings_pct, 1)
                        result['optimal_fuel_rate'] = params.get('fuel_rate_gph', 15) * (1 - savings_pct/100)
                        result['cost_savings_per_hour'] = round(params.get('fuel_cost_per_hour', 58.52) * savings_pct/100, 2)
                        
                        print(f"⚠️ Patched savings calculation: {current_speed:.1f} mph → {optimal_speed:.1f} mph, {savings_pct:.1f}% savings")
                
                return result
            
            # Apply the patch
            self.optimizer.optimize_speed_for_operation = patched_optimize_speed
            print("✅ Applied savings calculation patch to model")
        else:
            print("⚠️ Patch already applied")
    
    def test_model_responsiveness(self):
        """Test if the model responds to different inputs with meaningful variations"""
        print("\n🔍 Testing model responsiveness to inputs:")
        
        # Create test cases with systematic variations
        base_params = {
            'implement_width_ft': 24, 
            'field_acres': 160, 
            'weather_factor': 1.0,
            'operation_type': 'tillage',
            'fuel_cost_per_hour': 58.52,
            'fuel_rate_gph': 15,
            'speed_mph': 8.0,
            'engine_load_pct': 75,
            'soil_type': 'loam',
            'terrain_type': 'rolling'
        }
        
        # Create variations
        variations = {
            'speed_mph': [5.0, 6.5, 8.0, 10.0, 12.0],
            'engine_load_pct': [50, 70, 90],
            'soil_type': ['loam', 'clay', 'sandy'],
            'terrain_type': ['flat', 'rolling', 'hilly']
        }
        
        # Test one parameter variation at a time
        results = {}
        
        for param, values in variations.items():
            param_results = []
            print(f"\nTesting variations in {param}:")
            
            for value in values:
                test_case = base_params.copy()
                test_case[param] = value
                
                try:
                    result = self.optimizer.optimize_speed_for_operation(test_case)
                    if result:
                        optimal_speed = result.get('optimal_speed', 0)
                        savings_pct = result.get('fuel_savings_percent', 0)
                        param_results.append((value, optimal_speed, savings_pct))
                        print(f"  {param}={value}: recommended {optimal_speed:.1f} mph, {savings_pct:.1f}% savings")
                    else:
                        param_results.append((value, None, None))
                        print(f"  {param}={value}: No result")
                except Exception as e:
                    param_results.append((value, None, None))
                    print(f"  {param}={value}: Error - {str(e)}")
            
            # Analyze variation in results
            if len(param_results) > 0 and all(r[1] is not None for r in param_results):
                speeds = [r[1] for r in param_results]
                savings = [r[2] for r in param_results]
                
                speed_std = np.std(speeds)
                savings_std = np.std(savings)
                
                print(f"  Speed recommendations std: {speed_std:.2f}")
                print(f"  Savings percentage std: {savings_std:.2f}")
                
                if speed_std < 0.1:
                    print(f"⚠️ Model doesn't vary speed recommendations when {param} changes")
                if savings_std < 0.1:
                    print(f"⚠️ Model doesn't vary savings when {param} changes")
            
            results[param] = param_results
        
        return results
    
    def suggest_model_improvements(self):
        """Provide specific code-level suggestions for improving the model"""
        print("\n🔧 Code-level improvement suggestions:")
        
        print("""
1. Add Feature Scaling - Ensure all inputs are normalized:
```python
def preprocess_inputs(self, params):
    # Normalize numeric features
    speed = (params.get('speed_mph', 8.0) - 7.5) / 2.5  # Normalized to mean=0, std~=1
    engine_load = (params.get('engine_load_pct', 75) - 75) / 15
    
    # One-hot encode categorical features
    soil_type_map = {'loam': [1, 0, 0], 'clay': [0, 1, 0], 'sandy': [0, 0, 1]}
    terrain_type_map = {'flat': [1, 0, 0], 'rolling': [0, 1, 0], 'hilly': [0, 0, 1]}
    
    soil_features = soil_type_map.get(params.get('soil_type', 'loam'), [1, 0, 0])
    terrain_features = terrain_type_map.get(params.get('terrain_type', 'rolling'), [0, 1, 0])
    
    # Return normalized feature vector
    return [speed, engine_load] + soil_features + terrain_features
```

2. Improve Savings Calculation:
```python
def calculate_savings(self, current_speed, optimal_speed, engine_load, terrain_type):
    # Base calculation
    speed_diff_pct = abs(current_speed - optimal_speed) / current_speed * 100
    
    # Adjust based on engine load and terrain
    if terrain_type == 'hilly':
        terrain_factor = 1.2  # Hilly terrain increases savings potential
    elif terrain_type == 'flat':
        terrain_factor = 0.8  # Flat terrain reduces savings differential
    else:
        terrain_factor = 1.0
        
    # Engine load adjustment
    if engine_load > 85:
        load_factor = 1.3  # High load increases savings potential
    elif engine_load < 60:
        load_factor = 0.7  # Low load decreases savings potential
    else:
        load_factor = 1.0
    
    # Calculate final savings
    savings_pct = speed_diff_pct * 1.2 * terrain_factor * load_factor
    
    # Ensure reasonable limits
    return max(0.0, min(savings_pct, 25.0))
```

3. Implement Custom Loss Function During Training:
```python
def custom_loss(y_true, y_pred):
    # Unpack predictions (optimal_speed, savings_percentage)
    pred_speed = y_pred[:, 0]
    pred_savings = y_pred[:, 1]
    
    # Unpack targets
    true_speed = y_true[:, 0]
    
    # Calculate expected savings based on speed difference
    current_speed = input_features[:, speed_index]  # Extract from input features
    speed_diff_pct = tf.abs(current_speed - pred_speed) / current_speed * 100
    expected_savings = speed_diff_pct * 1.2
    
    # MSE for speed prediction
    speed_loss = tf.reduce_mean(tf.square(true_speed - pred_speed))
    
    # Custom loss component that penalizes when savings are too low
    savings_loss = tf.reduce_mean(tf.square(expected_savings - pred_savings))
    
    # Add penalty for very low savings predictions
    low_savings_penalty = tf.reduce_mean(tf.maximum(0.0, 5.0 - pred_savings))
    
    # Combine losses
    return speed_loss + savings_loss + 0.5 * low_savings_penalty
```

4. Try an Ensemble Approach:
```python
def optimize_speed_for_operation(self, params):
    # Get predictions from multiple models
    regression_result = self.regression_model.predict(params)
    rule_based_result = self.rule_based_optimization(params)
    
    # Weight the results based on confidence
    if abs(params['speed_mph'] - regression_result['optimal_speed']) < 0.5:
        # If regression model suggests minimal change, trust rule-based more
        final_speed = rule_based_result['optimal_speed']
        final_savings = rule_based_result['fuel_savings_percent']
    else:
        # Otherwise blend the results
        final_speed = 0.7 * regression_result['optimal_speed'] + 0.3 * rule_based_result['optimal_speed']
        final_savings = 0.7 * regression_result['fuel_savings_percent'] + 0.3 * rule_based_result['fuel_savings_percent']
    
    return {
        'optimal_speed': round(final_speed, 1),
        'fuel_savings_percent': round(final_savings, 1),
        # Calculate other metrics based on these values
    }
```
        """)

if __name__ == "__main__":
    debugger = ModelDebugger()
    
    # Check if we can load the model and data
    if debugger.load_model() and debugger.load_data():
        # Run diagnostic functions
        debugger.analyze_savings_calculation()
        
        # Ask user if they want to apply the patch
        response = input("\nDo you want to apply the savings calculation patch? (y/n): ")
        if response.lower() == 'y':
            debugger.patch_savings_calculation()
            debugger.test_model_responsiveness()
        
        # Show improvement suggestions
        print("\nWould you like to see code-level suggestions for improving the model? (y/n): ")
        if response.lower() == 'y':
            debugger.suggest_model_improvements()
    
    print("\n✅ Debugging session complete")
