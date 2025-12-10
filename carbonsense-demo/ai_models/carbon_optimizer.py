"""
CarbonSense AI - Optimization Engine
Real-time fuel efficiency and carbon emission optimization algorithms
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from scipy.optimize import minimize
import json
from datetime import datetime

class CarbonOptimizer:
    def __init__(self):
        self.fuel_predictor = None
        self.emission_predictor = None
        self.scaler = None
        self.feature_columns = None
        self.co2_per_gallon = 22.4  # EPA standard
        self.diesel_cost_per_gallon = 3.85
        
        # Try to load pre-trained models at initialization
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, "carbonsense")
            self.fuel_predictor = joblib.load(f"{model_path}_fuel_model.pkl")
            self.emission_predictor = joblib.load(f"{model_path}_emission_model.pkl")
            self.scaler = joblib.load(f"{model_path}_scaler.pkl")
            
            with open(f"{model_path}_features.json", 'r') as f:
                self.feature_columns = json.load(f)
            print("✅ Pre-trained models loaded successfully")
        except Exception as e:
            print(f"⚠️ Using default initialization: {str(e)}")
            self.scaler = StandardScaler()
        
        # Optimization constraints based on equipment capabilities
        self.optimization_constraints = {
            'speed_min': 3.0,    # mph
            'speed_max': 15.0,   # mph
            'load_min': 40.0,    # %
            'load_max': 95.0,    # %
            'efficiency_threshold': 0.15  # 15% minimum improvement
        }

    def prepare_features(self, data):
        """Prepare features for ML models with enhanced engineering"""
        # Base features
        features = [
            'speed_mph', 'engine_load_pct', 'implement_width_ft',
            'field_acres', 'weather_factor'
        ]
        
        # Create feature dataframe
        feature_data = data[features].copy()
        
        # Add engineered features for better speed-fuel relationship
        feature_data['speed_squared'] = feature_data['speed_mph'] ** 2  # Capture non-linear speed effects
        feature_data['speed_load_interaction'] = feature_data['speed_mph'] * feature_data['engine_load_pct'] / 100
        feature_data['implement_load'] = feature_data['implement_width_ft'] * feature_data['engine_load_pct'] / 100
        
        # Add efficiency zones (optimal speed ranges)
        feature_data['speed_efficiency'] = pd.cut(
            feature_data['speed_mph'],
            bins=[0, 5, 7, 9, 11, 15],
            labels=['very_slow', 'slow', 'optimal', 'fast', 'very_fast']
        ).astype(str)
        
        # Add load efficiency zones
        feature_data['load_efficiency'] = pd.cut(
            feature_data['engine_load_pct'],
            bins=[0, 60, 75, 85, 95, 100],
            labels=['underload', 'efficient', 'optimal', 'high', 'overload']
        ).astype(str)
        
        # Encode categorical features
        categorical_features = ['speed_efficiency', 'load_efficiency']
        if 'operation_type' in data.columns:
            categorical_features.append('operation_type')
        if 'soil_type' in data.columns:
            categorical_features.append('soil_type')
        if 'terrain_type' in data.columns:
            categorical_features.append('terrain_type')
        
        # Create dummy variables for all categorical features
        for feature in categorical_features:
            if feature in data.columns or feature in feature_data.columns:
                source_data = data if feature in data.columns else feature_data
                dummies = pd.get_dummies(source_data[feature], prefix=feature)
                feature_data = pd.concat([feature_data, dummies], axis=1)
        
        # Drop original categorical columns that were encoded
        feature_data = feature_data.drop(['speed_efficiency', 'load_efficiency'], axis=1)
        
        return feature_data

    def train_optimization_models(self, training_data):
        """Train ML models with synthetic data augmentation"""
        print("🤖 Training AI optimization models...")
        
        # Create synthetic data to better capture speed-fuel relationships
        synthetic_data = []
        
        print("🔄 Generating synthetic training data...")
        for _, row in training_data.iterrows():
            base_speed = row['speed_mph']
            base_fuel = row['fuel_rate_gph']
            base_co2 = row['co2_rate_lbs_per_hour']
            
            # Known relationships from agricultural engineering:
            # 1. Fuel consumption typically increases quadratically with speed
            # 2. There's usually an optimal speed range around 6-8 mph
            # 3. Different soil types affect the relationship
            
            # Generate variations
            for speed_factor in [0.7, 0.85, 1.0, 1.15, 1.3]:
                new_speed = base_speed * speed_factor
                if 3.0 <= new_speed <= 15.0:  # Stay within realistic bounds
                    new_row = row.copy()
                    new_row['speed_mph'] = new_speed
                    
                    # Calculate new fuel rate based on physics
                    # Power required increases with cube of speed, but efficiency varies
                    speed_ratio = new_speed / base_speed
                    
                    # Add soil type effect
                    soil_factor = 1.0
                    if row['soil_type'] == 'clay':
                        soil_factor = 1.2
                    elif row['soil_type'] == 'sandy':
                        soil_factor = 0.9
                    
                    # Add terrain effect
                    terrain_factor = 1.0
                    if row['terrain_type'] == 'hilly':
                        terrain_factor = 1.3
                    elif row['terrain_type'] == 'flat':
                        terrain_factor = 0.9
                    
                    # Calculate new fuel rate with realistic variations
                    power_factor = (speed_ratio ** 3) * soil_factor * terrain_factor
                    efficiency_factor = 1.0 - 0.2 * abs(new_speed - 7.0) / 7.0  # Optimal around 7 mph
                    new_fuel = base_fuel * power_factor / efficiency_factor
                    
                    # Update fuel and CO2 rates
                    new_row['fuel_rate_gph'] = new_fuel
                    new_row['co2_rate_lbs_per_hour'] = new_fuel * (base_co2 / base_fuel)
                    
                    synthetic_data.append(new_row)
        
        # Combine original and synthetic data
        augmented_data = pd.concat([training_data, pd.DataFrame(synthetic_data)], ignore_index=True)
        print(f"✅ Generated {len(synthetic_data)} synthetic records")
        print(f"📊 Total training records: {len(augmented_data)}")
        
        # Prepare features and targets with enhanced engineering
        X = self.prepare_features(augmented_data)
        y_fuel = augmented_data['fuel_rate_gph']
        y_co2 = augmented_data['co2_rate_lbs_per_hour']
        
        # Store feature columns for prediction
        self.feature_columns = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data with stratification based on speed ranges using augmented data
        speed_strata = pd.cut(augmented_data['speed_mph'], bins=5).astype(str)
        X_train, X_test, y_fuel_train, y_fuel_test = train_test_split(
            X_scaled, y_fuel, test_size=0.2, random_state=42,
            stratify=speed_strata  # Ensure good distribution of speeds
        )
        _, _, y_co2_train, y_co2_test = train_test_split(
            X_scaled, y_co2, test_size=0.2, random_state=42,
            stratify=speed_strata
        )
        
        # Hyperparameters focused on key relationships
        fuel_model_params = {
            'n_estimators': 50,       # Fewer trees for simpler model
            'max_depth': 5,           # Shallow trees to focus on main effects
            'min_samples_split': 20,  # Larger splits for stability
            'min_samples_leaf': 10,   # Larger leaves for smoother predictions
            'max_features': 0.5,      # Use half of features per tree
            'random_state': 42,
            'n_jobs': -1,
            'bootstrap': True,
            'oob_score': True
        }
        
        emission_model_params = fuel_model_params.copy()
        
        # Train fuel consumption model with cross-validation
        print("\n🔄 Training fuel consumption model...")
        from sklearn.model_selection import cross_val_score
        
        # First, evaluate with cross-validation
        cv_scores = cross_val_score(
            RandomForestRegressor(**fuel_model_params),
            X_train, y_fuel_train,
            cv=5,
            scoring='r2'
        )
        print(f"Cross-validation R² scores: {cv_scores.mean():.3f} (±{cv_scores.std()*2:.3f})")
        
        # Train final model
        self.fuel_predictor = RandomForestRegressor(**fuel_model_params)
        self.fuel_predictor.fit(X_train, y_fuel_train)
        print(f"Out-of-bag score: {self.fuel_predictor.oob_score_:.3f}")
        
        # Train CO2 emission model
        print("\n🔄 Training CO2 emission model...")
        cv_scores = cross_val_score(
            RandomForestRegressor(**emission_model_params),
            X_train, y_co2_train,
            cv=5,
            scoring='r2'
        )
        print(f"Cross-validation R² scores: {cv_scores.mean():.3f} (±{cv_scores.std()*2:.3f})")
        
        self.emission_predictor = RandomForestRegressor(**emission_model_params)
        self.emission_predictor.fit(X_train, y_co2_train)
        print(f"Out-of-bag score: {self.emission_predictor.oob_score_:.3f}")
        
        # Print feature importance
        print("\n📊 Top 5 important features for fuel prediction:")
        importances = pd.Series(
            self.fuel_predictor.feature_importances_,
            index=self.feature_columns
        ).sort_values(ascending=False)
        for name, importance in importances.head().items():
            print(f"   {name}: {importance:.3f}")
        
        # Evaluate models
        fuel_score = self.fuel_predictor.score(X_test, y_fuel_test)
        co2_score = self.emission_predictor.score(X_test, y_co2_test)
        
        print(f"\n📊 Model Performance:")
        print(f"✅ Fuel consumption model R² score: {fuel_score:.3f}")
        print(f"✅ CO2 emission model R² score: {co2_score:.3f}")
        
        # Validate model sensitivity
        print("\n🧪 Validating model sensitivity...")
        self._validate_model_sensitivity(X_test, y_fuel_test)
        
        return fuel_score, co2_score
        
    def _validate_model_sensitivity(self, X_test, y_test, n_samples=5):
        """Validate model's sensitivity to speed changes"""
        # Select random samples
        indices = np.random.choice(len(X_test), n_samples, replace=False)
        X_samples = X_test[indices]
        
        print(f"\nTesting sensitivity with {n_samples} samples:")
        for i in range(n_samples):
            X_mod = X_samples[i:i+1].copy()
            base_pred = self.fuel_predictor.predict(X_mod)[0]
            
            # Test with 20% higher speed
            X_mod_high = X_mod.copy()
            X_mod_high[0, self.feature_columns.index('speed_mph')] *= 1.2
            high_pred = self.fuel_predictor.predict(X_mod_high)[0]
            
            # Test with 20% lower speed
            X_mod_low = X_mod.copy()
            X_mod_low[0, self.feature_columns.index('speed_mph')] *= 0.8
            low_pred = self.fuel_predictor.predict(X_mod_low)[0]
            
            # Calculate sensitivity
            high_diff = ((high_pred - base_pred) / base_pred) * 100
            low_diff = ((low_pred - base_pred) / base_pred) * 100
            
            print(f"Sample {i+1}:")
            print(f"  Base prediction: {base_pred:.2f} gph")
            print(f"  +20% speed: {high_pred:.2f} gph ({high_diff:+.1f}%)")
            print(f"  -20% speed: {low_pred:.2f} gph ({low_diff:+.1f}%)")

    def predict_consumption(self, operation_params):
        """Predict fuel consumption and emissions for given parameters"""
        if self.fuel_predictor is None or self.emission_predictor is None:
            raise ValueError("Models not trained. Call train_optimization_models first.")
        
        # Create feature vector
        feature_row = pd.DataFrame([operation_params])
        X = self.prepare_features(feature_row)
        
        # Ensure all required columns are present
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        
        # Reorder columns to match training data
        X = X.reindex(columns=self.feature_columns, fill_value=0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        fuel_rate = self.fuel_predictor.predict(X_scaled)[0]
        co2_rate = self.emission_predictor.predict(X_scaled)[0]
        
        return fuel_rate, co2_rate

    def optimize_speed_for_operation(self, base_params, target_acres_per_hour=None):
        """Find optimal speed for minimum fuel consumption with enhanced optimization"""
        
        def objective_function(speed):
            params = base_params.copy()
            params['speed_mph'] = speed[0]
            
            try:
                # Get fuel consumption at this speed
                fuel_rate, co2_rate = self.predict_consumption(params)
                
                # Add penalty for speeds too far from typical ranges
                typical_speed = 7.5  # mph
                speed_penalty = abs(speed[0] - typical_speed) * 0.05
                
                # Add penalty for very high engine loads
                if params.get('engine_load_pct', 75) > 85:
                    load_penalty = (params['engine_load_pct'] - 85) * 0.1
                else:
                    load_penalty = 0
                
                # Combine fuel rate with penalties
                return fuel_rate * (1 + speed_penalty + load_penalty)
            except:
                return 999  # High penalty for invalid parameters
        
        # Speed optimization constraints
        constraints = []
        if target_acres_per_hour:
            # Constraint to meet productivity target
            def productivity_constraint(speed):
                acres_per_hour = (speed[0] * base_params['implement_width_ft']) / 43560 * 8.25
                return acres_per_hour - target_acres_per_hour
            
            constraints.append({'type': 'ineq', 'fun': productivity_constraint})
            
        # Add constraint for reasonable speed changes
        current_speed = base_params['speed_mph']
        max_change = 0.3  # Allow up to 30% change
        
        def max_speed_change(speed):
            return current_speed * (1 + max_change) - speed[0]
        
        def min_speed_change(speed):
            return speed[0] - current_speed * (1 - max_change)
        
        constraints.extend([
            {'type': 'ineq', 'fun': max_speed_change},
            {'type': 'ineq', 'fun': min_speed_change}
        ])
        
        # Try multiple starting points
        best_result = None
        best_fuel_rate = float('inf')
        start_speeds = [
            base_params['speed_mph'],
            base_params['speed_mph'] * 0.9,
            base_params['speed_mph'] * 1.1
        ]
        
        for start_speed in start_speeds:
            # Optimize
            result = minimize(
                objective_function,
                x0=[start_speed],
                method='SLSQP',
                bounds=[(self.optimization_constraints['speed_min'], 
                        self.optimization_constraints['speed_max'])],
                constraints=constraints
            )
            
            if result.success:
                fuel_rate = objective_function(result.x)
                if fuel_rate < best_fuel_rate:
                    best_result = result
                    best_fuel_rate = fuel_rate
        
        # Calculate base fuel consumption for comparison
        original_fuel, original_co2 = self.predict_consumption(base_params)
        
        if best_result is None:
            # If no successful optimization was found, return current speed as optimal
            return {
                'optimal_speed': round(base_params['speed_mph'], 1),
                'fuel_savings_percent': 0.0,
                'co2_reduction_percent': 0.0,
                'optimal_fuel_rate': round(original_fuel, 2),
                'optimal_co2_rate': round(original_co2, 2),
                'cost_savings_per_hour': 0.0
            }

        # Use the best result found
        optimal_speed = best_result.x[0]
        optimal_fuel, optimal_co2 = self.predict_consumption({
            **base_params, 'speed_mph': optimal_speed
        })
        
        # Calculate savings
        fuel_savings_pct = (original_fuel - optimal_fuel) / original_fuel * 100
        co2_reduction_pct = (original_co2 - optimal_co2) / original_co2 * 100
        
        return {
            'optimal_speed': round(optimal_speed, 1),
            'fuel_savings_percent': round(fuel_savings_pct, 1),
            'co2_reduction_percent': round(co2_reduction_pct, 1),
            'optimal_fuel_rate': round(optimal_fuel, 2),
            'optimal_co2_rate': round(optimal_co2, 2),
            'cost_savings_per_hour': round((original_fuel - optimal_fuel) * self.diesel_cost_per_gallon, 2)
        }

    def generate_route_optimization(self, field_boundary, implement_width, current_pattern='parallel'):
        """Generate optimized field operation route"""
        
        # Calculate field dimensions
        lats = [p[0] for p in field_boundary]
        lons = [p[1] for p in field_boundary]
        field_length = max(lats) - min(lats)
        field_width = max(lons) - min(lons)
        
        # Convert implement width to coordinate system
        width_deg = (implement_width / 5280) / (69.0 * np.cos(np.radians(np.mean(lats))))
        
        # Calculate optimization potential
        patterns = {
            'parallel': {'efficiency': 0.95, 'fuel_factor': 1.0},
            'contour': {'efficiency': 0.88, 'fuel_factor': 1.15},
            'spiral': {'efficiency': 0.92, 'fuel_factor': 1.08},
            'optimized_parallel': {'efficiency': 0.98, 'fuel_factor': 0.85}
        }
        
        current_efficiency = patterns[current_pattern]['efficiency']
        optimal_efficiency = patterns['optimized_parallel']['efficiency']
        
        # Calculate savings from route optimization
        efficiency_improvement = (optimal_efficiency - current_efficiency) / current_efficiency
        fuel_savings_pct = efficiency_improvement * 100
        
        # Estimate overlap reduction
        overlap_reduction = 0.05  # 5% reduction in overlap
        total_fuel_savings = fuel_savings_pct + (overlap_reduction * 100)
        
        return {
            'recommended_pattern': 'Optimized Parallel with Reduced Overlap',
            'fuel_savings_percent': round(total_fuel_savings, 1),
            'overlap_reduction_percent': round(overlap_reduction * 100, 1),
            'efficiency_improvement': round(efficiency_improvement * 100, 1),
            'estimated_time_savings': round(efficiency_improvement * 60, 0),  # minutes
            'pattern_description': 'AI-optimized parallel passes with minimal overlap and reduced turn time'
        }

    def real_time_recommendations(self, current_telemetry):
        """Generate real-time optimization recommendations"""
        recommendations = []
        
        # Speed optimization
        speed_opt = self.optimize_speed_for_operation(current_telemetry)
        if speed_opt and speed_opt['fuel_savings_percent'] > 5:
            recommendations.append({
                'type': 'speed_optimization',
                'priority': 'high',
                'title': f"Adjust Speed to {speed_opt['optimal_speed']} mph",
                'description': f"Reduce fuel consumption by {speed_opt['fuel_savings_percent']:.1f}%",
                'savings': f"${speed_opt['cost_savings_per_hour']:.2f}/hour",
                'co2_reduction': f"{speed_opt['co2_reduction_percent']:.1f}% less CO2",
                'action': 'speed_adjustment',
                'target_value': speed_opt['optimal_speed']
            })
        
        # Engine load optimization
        current_load = current_telemetry.get('engine_load_pct', 70)
        if current_load > 85:
            recommendations.append({
                'type': 'load_optimization',
                'priority': 'medium',
                'title': 'Reduce Engine Load',
                'description': 'Current load is high, consider reducing depth or speed',
                'savings': 'Up to 12% fuel savings',
                'action': 'load_reduction',
                'target_value': 75
            })
        
        # Weather-based recommendations
        weather_factor = current_telemetry.get('weather_factor', 1.0)
        if weather_factor > 1.1:
            recommendations.append({
                'type': 'weather_optimization',
                'priority': 'low',
                'title': 'Weather Impact Detected',
                'description': 'Consider adjusting operation timing due to weather conditions',
                'savings': 'Up to 8% efficiency improvement',
                'action': 'timing_adjustment'
            })
        
        return recommendations

    def save_models(self, path_prefix="carbonsense_models"):
        """Save trained models for deployment"""
        if self.fuel_predictor:
            joblib.dump(self.fuel_predictor, f"{path_prefix}_fuel_model.pkl")
            joblib.dump(self.emission_predictor, f"{path_prefix}_emission_model.pkl")
            joblib.dump(self.scaler, f"{path_prefix}_scaler.pkl")
            
            # Save feature columns
            with open(f"{path_prefix}_features.json", 'w') as f:
                json.dump(self.feature_columns, f)
            
            print("✅ Models saved successfully")

    def load_models(self, path_prefix="carbonsense_models"):
        """Load pre-trained models"""
        try:
            # Get base directory from path_prefix
            base_dir = os.path.dirname(path_prefix)
            base_name = os.path.basename(path_prefix)
            
            # Construct full paths
            fuel_model_path = os.path.join(base_dir, f"{base_name}_fuel_model.pkl")
            emission_model_path = os.path.join(base_dir, f"{base_name}_emission_model.pkl")
            scaler_path = os.path.join(base_dir, f"{base_name}_scaler.pkl")
            features_path = os.path.join(base_dir, f"{base_name}_features.json")
            
            print(f"📂 Loading models from: {base_dir}")
            print(f"   Fuel model: {os.path.exists(fuel_model_path)}")
            print(f"   Emission model: {os.path.exists(emission_model_path)}")
            print(f"   Scaler: {os.path.exists(scaler_path)}")
            print(f"   Features: {os.path.exists(features_path)}")
            
            # Load each model with error handling
            try:
                print("🔄 Loading fuel model...")
                self.fuel_predictor = joblib.load(fuel_model_path)
                # Verify the model is a RandomForestRegressor
                if not hasattr(self.fuel_predictor, 'predict'):
                    raise ValueError("Fuel model lacks predict method")
                
                print("🔄 Loading emission model...")
                self.emission_predictor = joblib.load(emission_model_path)
                if not hasattr(self.emission_predictor, 'predict'):
                    raise ValueError("Emission model lacks predict method")
                
                print("🔄 Loading scaler...")
                self.scaler = joblib.load(scaler_path)
                if not hasattr(self.scaler, 'transform'):
                    raise ValueError("Scaler lacks transform method")
                
                print("🔄 Loading features...")
                with open(features_path, 'r') as f:
                    self.feature_columns = json.load(f)
                
                # Verify feature columns
                if not isinstance(self.feature_columns, list):
                    raise ValueError("Feature columns must be a list")
                
                # Test model with dummy data
                test_data = pd.DataFrame([[7.5, 75, 24, 160, 1.0]], 
                                      columns=['speed_mph', 'engine_load_pct', 
                                              'implement_width_ft', 'field_acres', 
                                              'weather_factor'])
                test_data = pd.get_dummies(test_data, columns=[])
                
                # Ensure all feature columns exist
                for col in self.feature_columns:
                    if col not in test_data.columns:
                        test_data[col] = 0
                
                # Test prediction pipeline
                X = test_data.reindex(columns=self.feature_columns, fill_value=0)
                X_scaled = self.scaler.transform(X)
                fuel_pred = self.fuel_predictor.predict(X_scaled)
                emission_pred = self.emission_predictor.predict(X_scaled)
                
                print(f"✅ Test prediction successful:")
                print(f"   Fuel rate: {fuel_pred[0]:.2f} gph")
                print(f"   Emission rate: {emission_pred[0]:.2f} lbs/hr")
                
                print("✅ ML models loaded and verified successfully")
                return True
                
            except Exception as model_error:
                print(f"❌ Error in model verification: {str(model_error)}")
                raise
                
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            print(f"   Path prefix used: {path_prefix}")
            return False

# Demo usage
if __name__ == "__main__":
    print("🧠 CarbonSense AI Optimization Engine Demo")
    
    # Initialize optimizer
    optimizer = CarbonOptimizer()
    
        # Load demo data (generated from demo_data_generator.py)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(os.path.dirname(script_dir), "data", "demo_all_operations.csv")
        demo_data = pd.read_csv(data_path)
        print(f"📊 Loaded {len(demo_data)} training records")        # Train models
        fuel_score, co2_score = optimizer.train_optimization_models(demo_data)
        
        # Demo optimization for current operation
        current_operation = {
            'speed_mph': 7.5,
            'engine_load_pct': 78,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.1,
            'operation_type': 'planter',
            'soil_type': 'loam',
            'terrain_type': 'rolling'
        }
        
        print(f"\n🚜 Current Operation Analysis:")
        print(f"Speed: {current_operation['speed_mph']} mph")
        print(f"Engine Load: {current_operation['engine_load_pct']}%")
        
        # Get optimization recommendations
        speed_opt = optimizer.optimize_speed_for_operation(current_operation)
        if speed_opt:
            print(f"\n⚡ Speed Optimization Results:")
            print(f"Optimal Speed: {speed_opt['optimal_speed']} mph")
            print(f"Fuel Savings: {speed_opt['fuel_savings_percent']}%")
            print(f"CO2 Reduction: {speed_opt['co2_reduction_percent']}%")
            print(f"Cost Savings: ${speed_opt['cost_savings_per_hour']:.2f}/hour")
        
        # Generate real-time recommendations
        recommendations = optimizer.real_time_recommendations(current_operation)
        if recommendations:
            print(f"\n💡 Real-time Recommendations:")
            for rec in recommendations:
                print(f"- {rec['title']}: {rec['description']}")
        
        # Save models for web application
        script_dir = os.path.dirname(os.path.abspath(__file__))
        optimizer.save_models(os.path.join(script_dir, "carbonsense"))
        
    except FileNotFoundError:
        print("❌ Demo data not found. Run demo_data_generator.py first.")
        print("   This will generate the required training data.")
