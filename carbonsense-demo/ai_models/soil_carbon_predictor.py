"""
CarbonSense AI - Soil Carbon Emission Prediction Model
Predicts CO2 and N2O emissions based on soil nutrients, properties, and environmental factors
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoilCarbonPredictor:
    """
    Advanced ML model for predicting soil carbon emissions from agricultural data
    """
    
    def __init__(self):
        self.co2_model = None
        self.n2o_model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'nitrogen_ppm', 'phosphorus_ppm', 'potassium_ppm',
            'soil_ph', 'organic_carbon_pct', 'moisture_pct',
            'temperature_c', 'bulk_density', 'clay_pct', 'sand_pct',
            'crop_type_encoded', 'tillage_intensity', 'fertilizer_rate_kg_ha',
            'days_since_fertilization', 'precipitation_mm'
        ]
        self.crop_types = {
            'corn': 0, 'soybean': 1, 'wheat': 2, 'cotton': 3, 
            'rice': 4, 'barley': 5, 'oats': 6, 'alfalfa': 7
        }
        
    def generate_synthetic_training_data(self, n_samples=10000):
        """
        Generate realistic synthetic soil and emission data for training
        Based on agricultural research and emission factor databases
        """
        np.random.seed(42)
        
        # Generate soil nutrient data (typical ranges for agricultural soils)
        data = {
            'nitrogen_ppm': np.random.normal(45, 15, n_samples).clip(5, 150),
            'phosphorus_ppm': np.random.normal(25, 8, n_samples).clip(3, 80),
            'potassium_ppm': np.random.normal(180, 40, n_samples).clip(50, 400),
            'soil_ph': np.random.normal(6.2, 0.8, n_samples).clip(4.5, 8.5),
            'organic_carbon_pct': np.random.normal(2.5, 0.7, n_samples).clip(0.5, 6.0),
            'moisture_pct': np.random.normal(22, 6, n_samples).clip(8, 45),
            'temperature_c': np.random.normal(18, 8, n_samples).clip(-5, 35),
            'bulk_density': np.random.normal(1.3, 0.15, n_samples).clip(1.0, 1.7),
            'clay_pct': np.random.normal(25, 12, n_samples).clip(5, 60),
            'sand_pct': np.random.normal(45, 15, n_samples).clip(15, 85),
            'crop_type_encoded': np.random.randint(0, 8, n_samples),
            'tillage_intensity': np.random.randint(1, 4, n_samples),  # 1=no-till, 2=reduced, 3=conventional
            'fertilizer_rate_kg_ha': np.random.normal(120, 30, n_samples).clip(0, 250),
            'days_since_fertilization': np.random.randint(0, 180, n_samples),
            'precipitation_mm': np.random.normal(25, 15, n_samples).clip(0, 100)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate realistic CO2 emissions (kg CO2-eq per hectare per day)
        # Based on soil respiration models and research literature
        co2_base = (
            df['organic_carbon_pct'] * 2.5 +  # Higher organic carbon = more respiration
            (df['temperature_c'] * 0.3).clip(0, None) +  # Temperature effect
            df['moisture_pct'] * 0.2 +  # Moisture effect
            (df['nitrogen_ppm'] * 0.05) +  # Nitrogen effect
            df['tillage_intensity'] * 3  # Tillage disturbance
        )
        
        # Add realistic variability and environmental factors
        df['co2_emissions_kg_ha_day'] = (
            co2_base * np.random.normal(1.0, 0.15, n_samples) + 
            np.random.normal(0, 2, n_samples)  # Random variation
        ).clip(2, 45)
        
        # Calculate N2O emissions (kg N2O per hectare per day)
        # Based on IPCC emission factors and agricultural research
        n2o_base = (
            (df['nitrogen_ppm'] * 0.008) +  # Direct relationship with N content
            (df['fertilizer_rate_kg_ha'] * 0.002) +  # Fertilizer contribution
            (df['moisture_pct'] * 0.003) +  # Wet conditions increase N2O
            (df['clay_pct'] * 0.001) +  # Soil texture effect
            np.where(df['days_since_fertilization'] < 30, 0.5, 0.1)  # Post-fertilization spike
        )
        
        df['n2o_emissions_kg_ha_day'] = (
            n2o_base * np.random.normal(1.0, 0.2, n_samples) + 
            np.random.normal(0, 0.05, n_samples)
        ).clip(0.01, 2.5)
        
        return df
    
    def train_models(self, retrain=False):
        """
        Train CO2 and N2O emission prediction models
        """
        if not retrain and self.co2_model is not None and self.n2o_model is not None:
            return
            
        logger.info("Generating training data...")
        df = self.generate_synthetic_training_data()
        
        # Prepare features and targets
        X = df[self.feature_names]
        y_co2 = df['co2_emissions_kg_ha_day']
        y_n2o = df['n2o_emissions_kg_ha_day']
        
        # Split data
        X_train, X_test, y_co2_train, y_co2_test, y_n2o_train, y_n2o_test = train_test_split(
            X, y_co2, y_n2o, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train CO2 model
        logger.info("Training CO2 emission model...")
        self.co2_model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.co2_model.fit(X_train_scaled, y_co2_train)
        
        # Train N2O model
        logger.info("Training N2O emission model...")
        self.n2o_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            random_state=42
        )
        self.n2o_model.fit(X_train_scaled, y_n2o_train)
        
        # Evaluate models
        co2_pred = self.co2_model.predict(X_test_scaled)
        n2o_pred = self.n2o_model.predict(X_test_scaled)
        
        co2_r2 = r2_score(y_co2_test, co2_pred)
        n2o_r2 = r2_score(y_n2o_test, n2o_pred)
        
        logger.info(f"CO2 Model R² Score: {co2_r2:.3f}")
        logger.info(f"N2O Model R² Score: {n2o_r2:.3f}")
        
        # Save models
        self.save_models()
        
        return {
            'co2_r2': co2_r2,
            'n2o_r2': n2o_r2,
            'co2_rmse': np.sqrt(mean_squared_error(y_co2_test, co2_pred)),
            'n2o_rmse': np.sqrt(mean_squared_error(y_n2o_test, n2o_pred))
        }
    
    def predict_emissions(self, soil_data):
        """
        Predict CO2 and N2O emissions for given soil conditions
        
        Args:
            soil_data (dict): Dictionary containing soil parameters
            
        Returns:
            dict: Predicted emissions and analysis
        """
        # Ensure models are trained
        if self.co2_model is None or self.n2o_model is None:
            if not self.load_models():
                self.train_models()
        
        # Prepare input data
        input_data = []
        for feature in self.feature_names:
            if feature in soil_data:
                input_data.append(soil_data[feature])
            else:
                # Use default values for missing features
                defaults = {
                    'nitrogen_ppm': 45, 'phosphorus_ppm': 25, 'potassium_ppm': 180,
                    'soil_ph': 6.2, 'organic_carbon_pct': 2.5, 'moisture_pct': 22,
                    'temperature_c': 18, 'bulk_density': 1.3, 'clay_pct': 25,
                    'sand_pct': 45, 'crop_type_encoded': 0, 'tillage_intensity': 2,
                    'fertilizer_rate_kg_ha': 120, 'days_since_fertilization': 30,
                    'precipitation_mm': 25
                }
                input_data.append(defaults[feature])
        
        # Scale input
        input_scaled = self.scaler.transform([input_data])
        
        # Make predictions (with null checks)
        if self.co2_model is not None and self.n2o_model is not None:
            co2_emission = self.co2_model.predict(input_scaled)[0]
            n2o_emission = self.n2o_model.predict(input_scaled)[0]
            
            # Convert N2O to CO2 equivalent (N2O has 298x warming potential)
            n2o_co2_equiv = n2o_emission * 298
            total_co2_equiv = co2_emission + n2o_co2_equiv
            
            # Calculate feature importance for this prediction
            co2_importance = dict(zip(self.feature_names, self.co2_model.feature_importances_))
            n2o_importance = dict(zip(self.feature_names, self.n2o_model.feature_importances_))
        else:
            # Fallback values if models aren't available
            co2_emission = 15.0
            n2o_emission = 0.5
            n2o_co2_equiv = n2o_emission * 298
            total_co2_equiv = co2_emission + n2o_co2_equiv
            co2_importance = {}
            n2o_importance = {}
        
        return {
            'co2_emissions_kg_ha_day': float(co2_emission),
            'n2o_emissions_kg_ha_day': float(n2o_emission),
            'n2o_co2_equivalent_kg_ha_day': float(n2o_co2_equiv),
            'total_co2_equivalent_kg_ha_day': float(total_co2_equiv),
            'co2_feature_importance': co2_importance,
            'n2o_feature_importance': n2o_importance,
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def get_recommendations(self, soil_data, current_predictions):
        """
        Generate actionable recommendations to reduce soil emissions
        """
        recommendations = []
        
        # Analyze current conditions
        nitrogen = soil_data.get('nitrogen_ppm', 45)
        phosphorus = soil_data.get('phosphorus_ppm', 25)
        ph = soil_data.get('soil_ph', 6.2)
        moisture = soil_data.get('moisture_pct', 22)
        tillage = soil_data.get('tillage_intensity', 2)
        fertilizer_rate = soil_data.get('fertilizer_rate_kg_ha', 120)
        
        # High nitrogen recommendations
        if nitrogen > 60:
            recommendations.append({
                'type': 'fertilizer_management',
                'priority': 'high',
                'title': 'Reduce Nitrogen Application',
                'description': f'Soil nitrogen is high ({nitrogen:.1f} ppm). Consider reducing fertilizer rate by 15-20% to minimize N₂O emissions.',
                'potential_reduction': '12-18% N₂O reduction',
                'implementation': 'Precision fertilizer application with soil testing'
            })
        
        # pH optimization
        if ph < 5.5 or ph > 7.5:
            recommendations.append({
                'type': 'soil_management',
                'priority': 'medium',
                'title': 'Optimize Soil pH',
                'description': f'Current pH ({ph:.1f}) is outside optimal range. Target pH 6.0-7.0 for reduced emissions.',
                'potential_reduction': '8-12% total emissions reduction',
                'implementation': 'Apply lime (if acidic) or sulfur (if alkaline)'
            })
        
        # Tillage recommendations
        if tillage >= 3:
            recommendations.append({
                'type': 'tillage_management',
                'priority': 'high',
                'title': 'Reduce Tillage Intensity',
                'description': 'Conventional tillage increases soil CO₂ emissions. Consider no-till or reduced tillage practices.',
                'potential_reduction': '15-25% CO₂ reduction',
                'implementation': 'Transition to no-till with cover crops'
            })
        
        # Moisture management
        if moisture > 35:
            recommendations.append({
                'type': 'water_management',
                'priority': 'medium',
                'title': 'Improve Drainage',
                'description': f'High soil moisture ({moisture:.1f}%) increases N₂O emissions. Consider drainage improvements.',
                'potential_reduction': '10-15% N₂O reduction',
                'implementation': 'Install tile drainage or raised beds'
            })
        
        return recommendations
    
    def save_models(self):
        """Save trained models and scaler"""
        import os
        os.makedirs('ai_models', exist_ok=True)
        
        joblib.dump(self.co2_model, 'ai_models/soil_co2_model.pkl')
        joblib.dump(self.n2o_model, 'ai_models/soil_n2o_model.pkl')
        joblib.dump(self.scaler, 'ai_models/soil_scaler.pkl')
        
        # Save feature names and metadata
        metadata = {
            'feature_names': self.feature_names,
            'crop_types': self.crop_types,
            'model_version': '1.0',
            'training_date': datetime.now().isoformat()
        }
        
        with open('ai_models/soil_model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Soil carbon models saved successfully")
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            self.co2_model = joblib.load('ai_models/soil_co2_model.pkl')
            self.n2o_model = joblib.load('ai_models/soil_n2o_model.pkl')
            self.scaler = joblib.load('ai_models/soil_scaler.pkl')
            
            with open('ai_models/soil_model_metadata.json', 'r') as f:
                metadata = json.load(f)
                self.feature_names = metadata['feature_names']
                self.crop_types = metadata['crop_types']
            
            logger.info("Soil carbon models loaded successfully")
            return True
        except FileNotFoundError:
            logger.warning("Pre-trained models not found. Will train new models.")
            return False

# Initialize global predictor
soil_predictor = SoilCarbonPredictor()

def get_soil_predictor():
    """Get the global soil carbon predictor instance"""
    return soil_predictor

if __name__ == "__main__":
    # Training and testing
    predictor = SoilCarbonPredictor()
    
    print("Training soil carbon emission models...")
    results = predictor.train_models(retrain=True)
    print(f"Training completed! Results: {results}")
    
    # Test prediction
    test_soil = {
        'nitrogen_ppm': 55,
        'phosphorus_ppm': 30,
        'potassium_ppm': 200,
        'soil_ph': 6.5,
        'organic_carbon_pct': 3.2,
        'moisture_pct': 25,
        'temperature_c': 20,
        'crop_type_encoded': 0,  # corn
        'tillage_intensity': 2,
        'fertilizer_rate_kg_ha': 140
    }
    
    prediction = predictor.predict_emissions(test_soil)
    print("\nTest Prediction:")
    print(f"CO₂ emissions: {prediction['co2_emissions_kg_ha_day']:.2f} kg/ha/day")
    print(f"N₂O emissions: {prediction['n2o_emissions_kg_ha_day']:.3f} kg/ha/day")
    print(f"Total CO₂ equivalent: {prediction['total_co2_equivalent_kg_ha_day']:.2f} kg/ha/day")
    
    recommendations = predictor.get_recommendations(test_soil, prediction)
    print(f"\nRecommendations: {len(recommendations)} suggestions generated")
