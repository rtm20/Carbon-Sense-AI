"""
CarbonSense AI - Model Diagnostics Tool
Tool to analyze and diagnose issues with the CarbonOptimizer model
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from tabulate import tabulate

# Make sure we can import the optimizer
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class ModelDiagnostics:
    """
    A comprehensive diagnostic tool for the CarbonOptimizer model.
    This tool analyzes model performance, data quality, and suggests improvements.
    """
    
    def __init__(self, optimizer=None):
        """Initialize with an optional optimizer instance"""
        self.optimizer = optimizer
        self.diagnostic_results = {}
        self.test_cases = []
        
    def load_optimizer(self, optimizer_path=None):
        """Load the optimizer from the specified path or use default"""
        try:
            # First try importing the patched version if it exists
            try:
                from ai_models.optimizer_hotfix import PatchedCarbonOptimizer
                self.optimizer = PatchedCarbonOptimizer()
                print("✅ Loaded patched optimizer")
                return True
            except ImportError:
                # If patched version doesn't exist, try the original
                from ai_models.carbon_optimizer import CarbonOptimizer
                self.optimizer = CarbonOptimizer()
                print("✅ Loaded original optimizer")
                return True
        except ImportError as e:
            print(f"❌ Could not load optimizer: {str(e)}")
            return False
    
    def generate_test_cases(self, num_cases=20):
        """Generate a diverse set of test cases for model evaluation"""
        self.test_cases = []
        
        # Define ranges for parameters
        speed_range = [(5.0, 12.0)]  # mph
        load_range = [(50, 95)]  # % 
        implement_widths = [15, 24, 32, 45]  # feet
        field_sizes = [80, 160, 320, 640]  # acres
        operations = ['tillage', 'planting', 'harvesting']
        soil_types = ['clay', 'loam', 'sandy']
        terrain_types = ['flat', 'rolling', 'hilly']
        weather_factors = [0.8, 1.0, 1.2]  # below normal, normal, above normal
        
        # Generate test cases with diverse parameters
        for i in range(num_cases):
            # Select parameters with some randomization
            speed = np.random.uniform(*speed_range[0])
            load = np.random.randint(*load_range[0])
            implement_width = np.random.choice(implement_widths)
            field_acres = np.random.choice(field_sizes)
            operation = np.random.choice(operations)
            soil = np.random.choice(soil_types)
            terrain = np.random.choice(terrain_types)
            weather = np.random.choice(weather_factors)
            
            # Calculate estimated fuel rate based on parameters
            # Basic formula: higher speed + higher load + larger implement = more fuel
            base_fuel_rate = 10.0  # gph
            speed_factor = speed / 7.0  # 7.0 mph is baseline
            load_factor = load / 70.0  # 70% is baseline
            width_factor = implement_width / 24.0  # 24 ft is baseline
            
            fuel_rate = base_fuel_rate * speed_factor * load_factor * width_factor
            fuel_cost_per_gallon = 3.75
            fuel_cost_per_hour = fuel_rate * fuel_cost_per_gallon
            
            # Create the test case
            test_case = {
                'speed_mph': round(speed, 1),
                'engine_load_pct': load,
                'implement_width_ft': implement_width,
                'field_acres': field_acres,
                'weather_factor': weather,
                'operation_type': operation,
                'soil_type': soil,
                'terrain_type': terrain,
                'fuel_rate_gph': round(fuel_rate, 2),
                'fuel_cost_per_hour': round(fuel_cost_per_hour, 2)
            }
            
            self.test_cases.append(test_case)
        
        print(f"✅ Generated {num_cases} diverse test cases")
        return self.test_cases
    
    def run_diagnostics(self):
        """Run comprehensive diagnostics on the model"""
        if not self.optimizer:
            print("❌ No optimizer loaded. Please load optimizer first.")
            return False
        
        # Generate test cases if needed
        if not self.test_cases:
            self.generate_test_cases()
        
        # Store diagnostics results
        self.diagnostic_results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'optimizer_type': self.optimizer.__class__.__name__,
            'test_cases': len(self.test_cases),
            'model_performance': {},
            'data_analysis': {},
            'savings_analysis': {}
        }
        
        # Run model on test cases
        results = []
        for i, test_case in enumerate(self.test_cases):
            try:
                result = self.optimizer.optimize_speed_for_operation(test_case)
                if result:
                    result['test_case_id'] = i
                    result['input'] = test_case
                    results.append(result)
                else:
                    print(f"⚠️ No result for test case {i}")
            except Exception as e:
                print(f"❌ Error processing test case {i}: {str(e)}")
        
        # No results? Return early
        if not results:
            print("❌ No results from optimizer for any test case")
            self.diagnostic_results['model_performance']['status'] = "Failed - No results"
            return False
        
        # Analyze the results
        self._analyze_model_performance(results)
        self._analyze_data_quality(results)
        self._analyze_savings_calculation(results)
        
        # Print summary
        self.print_diagnostic_summary()
        
        return True
    
    def _analyze_model_performance(self, results):
        """Analyze model performance metrics"""
        # Extract key metrics
        speeds = [r['input']['speed_mph'] for r in results]
        optimal_speeds = [r['optimal_speed'] for r in results]
        savings = [r['fuel_savings_percent'] for r in results]
        
        # Calculate performance metrics
        speed_diffs = [abs(optimal - original) for original, optimal in zip(speeds, optimal_speeds)]
        avg_speed_diff = sum(speed_diffs) / len(speed_diffs)
        max_speed_diff = max(speed_diffs)
        min_speed_diff = min(speed_diffs)
        
        # Count unique recommendations
        unique_speeds = len(set([round(s, 1) for s in optimal_speeds]))
        unique_savings = len(set([round(s, 1) for s in savings]))
        
        # Calculate response metrics
        meaningful_changes = sum(1 for diff in speed_diffs if diff > 0.2)
        meaningful_savings = sum(1 for s in savings if s > 0.5)
        
        # Store the metrics
        self.diagnostic_results['model_performance'] = {
            'avg_speed_difference': round(avg_speed_diff, 2),
            'max_speed_difference': round(max_speed_diff, 2),
            'min_speed_difference': round(min_speed_diff, 2),
            'unique_speed_recommendations': unique_speeds,
            'unique_savings_values': unique_savings,
            'cases_with_meaningful_changes': meaningful_changes,
            'cases_with_meaningful_savings': meaningful_savings,
            'response_rate': f"{(meaningful_changes / len(results)) * 100:.1f}%",
            'savings_rate': f"{(meaningful_savings / len(results)) * 100:.1f}%"
        }
    
    def _analyze_data_quality(self, results):
        """Analyze data quality and potential issues"""
        # Extract input parameters across all test cases
        inputs = [r['input'] for r in results]
        
        # Create a dataframe for analysis
        df = pd.DataFrame(inputs)
        
        # Check for missing values
        missing_values = df.isnull().sum().sum()
        
        # Check for parameter distributions
        param_stats = {}
        for col in df.columns:
            if df[col].dtype in [np.float64, np.int64]:
                param_stats[col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
            else:
                value_counts = df[col].value_counts().to_dict()
                param_stats[col] = {
                    'unique_values': len(value_counts),
                    'distribution': {str(k): int(v) for k, v in value_counts.items()}
                }
        
        # Store the data quality metrics
        self.diagnostic_results['data_analysis'] = {
            'missing_values': missing_values,
            'parameter_stats': param_stats,
            'num_parameters': len(df.columns)
        }
    
    def _analyze_savings_calculation(self, results):
        """Analyze how savings are calculated from speed changes"""
        # Extract key values
        data_points = []
        for r in results:
            input_speed = r['input']['speed_mph']
            optimal_speed = r['optimal_speed']
            savings = r['fuel_savings_percent']
            engine_load = r['input']['engine_load_pct']
            terrain = r['input']['terrain_type']
            soil = r['input']['soil_type']
            
            speed_diff = abs(optimal_speed - input_speed)
            speed_diff_pct = speed_diff / input_speed * 100
            
            data_points.append({
                'input_speed': input_speed,
                'optimal_speed': optimal_speed,
                'speed_diff': speed_diff,
                'speed_diff_pct': speed_diff_pct,
                'savings': savings,
                'engine_load': engine_load,
                'terrain': terrain,
                'soil': soil
            })
        
        # Create a dataframe for analysis
        df = pd.DataFrame(data_points)
        
        # Analyze speed difference vs. savings
        correlation = df['speed_diff_pct'].corr(df['savings'])
        
        # Check for zero savings despite speed changes
        zero_savings = sum(1 for _, row in df.iterrows() 
                           if row['speed_diff'] > 0.2 and row['savings'] <= 0.5)
        
        # Analyze factor influence
        terrain_impact = df.groupby('terrain')['savings'].mean().to_dict()
        soil_impact = df.groupby('soil')['savings'].mean().to_dict()
        
        # Analyze savings distribution
        savings_distribution = {
            'zero_or_negligible': sum(1 for s in df['savings'] if s <= 0.5),
            'low': sum(1 for s in df['savings'] if 0.5 < s <= 5),
            'medium': sum(1 for s in df['savings'] if 5 < s <= 15),
            'high': sum(1 for s in df['savings'] if s > 15)
        }
        
        # Store the savings analysis
        self.diagnostic_results['savings_analysis'] = {
            'speed_savings_correlation': correlation,
            'zero_savings_despite_changes': zero_savings,
            'terrain_impact': {str(k): float(v) for k, v in terrain_impact.items()},
            'soil_impact': {str(k): float(v) for k, v in soil_impact.items()},
            'savings_distribution': savings_distribution
        }
    
    def print_diagnostic_summary(self):
        """Print a summary of diagnostic results"""
        results = self.diagnostic_results
        
        print("\n==== CarbonSense AI Model Diagnostics ====")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Optimizer: {results['optimizer_type']}")
        print(f"Test Cases: {results['test_cases']}")
        
        print("\n--- Model Performance ---")
        perf = results['model_performance']
        perf_table = []
        for key, value in perf.items():
            perf_table.append([key, value])
        print(tabulate(perf_table, headers=["Metric", "Value"]))
        
        print("\n--- Savings Analysis ---")
        savings = results['savings_analysis']
        
        print(f"Speed-Savings Correlation: {savings['speed_savings_correlation']:.2f}")
        print(f"Cases with Zero Savings Despite Speed Changes: {savings['zero_savings_despite_changes']}")
        
        print("\nSavings Distribution:")
        dist_table = []
        for key, value in savings['savings_distribution'].items():
            dist_table.append([key, value, f"{(value/results['test_cases'])*100:.1f}%"])
        print(tabulate(dist_table, headers=["Category", "Count", "Percentage"]))
        
        print("\n--- Recommendations ---")
        if savings['speed_savings_correlation'] < 0.5:
            print("⚠️ Low correlation between speed changes and savings")
            print("   Recommendation: Revise savings calculation formula")
        
        if savings['zero_savings_despite_changes'] > 0:
            print(f"⚠️ Found {savings['zero_savings_despite_changes']} cases with speed changes but no savings")
            print("   Recommendation: Debug savings calculation logic")
        
        if perf['unique_savings_values'] < 3:
            print(f"⚠️ Only {perf['unique_savings_values']} unique savings values")
            print("   Recommendation: Improve savings calculation precision")
        
        print("\n==== End of Diagnostics ====")
    
    def save_results(self, file_path=None):
        """Save diagnostic results to a JSON file"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"model_diagnostics_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(self.diagnostic_results, f, indent=2)
        
        print(f"✅ Diagnostics saved to {file_path}")
        return file_path
    
    def plot_analysis(self, save_path=None):
        """Generate visualizations of the diagnostic results"""
        if not self.diagnostic_results:
            print("❌ No diagnostic results available")
            return
        
        # Create a figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        
        # Extract data
        data_points = []
        for i, test_case in enumerate(self.test_cases):
            try:
                result = self.optimizer.optimize_speed_for_operation(test_case)
                if result:
                    data_points.append({
                        'input_speed': test_case['speed_mph'],
                        'optimal_speed': result['optimal_speed'],
                        'savings': result['fuel_savings_percent'],
                        'engine_load': test_case['engine_load_pct'],
                        'terrain': test_case['terrain_type']
                    })
            except Exception:
                pass
        
        df = pd.DataFrame(data_points)
        
        # Plot 1: Input Speed vs Optimal Speed
        axs[0, 0].scatter(df['input_speed'], df['optimal_speed'], alpha=0.7)
        axs[0, 0].plot([min(df['input_speed']), max(df['input_speed'])], 
                    [min(df['input_speed']), max(df['input_speed'])], 'r--')
        axs[0, 0].set_xlabel('Input Speed (mph)')
        axs[0, 0].set_ylabel('Optimal Speed (mph)')
        axs[0, 0].set_title('Input vs Optimal Speed')
        axs[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Speed Difference vs Savings
        speed_diff = abs(df['optimal_speed'] - df['input_speed'])
        axs[0, 1].scatter(speed_diff, df['savings'], alpha=0.7)
        axs[0, 1].set_xlabel('Speed Difference (mph)')
        axs[0, 1].set_ylabel('Fuel Savings (%)')
        axs[0, 1].set_title('Speed Difference vs Savings')
        axs[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Engine Load vs Savings
        axs[1, 0].scatter(df['engine_load'], df['savings'], alpha=0.7)
        axs[1, 0].set_xlabel('Engine Load (%)')
        axs[1, 0].set_ylabel('Fuel Savings (%)')
        axs[1, 0].set_title('Engine Load vs Savings')
        axs[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Savings Distribution by Terrain
        if len(df) > 0:
            terrain_groups = df.groupby('terrain')['savings']
            terrain_data = [group[1].tolist() for group in terrain_groups]
            terrain_labels = [group[0] for group in terrain_groups]
            
            if terrain_data:
                axs[1, 1].boxplot(terrain_data, labels=terrain_labels)
                axs[1, 1].set_xlabel('Terrain Type')
                axs[1, 1].set_ylabel('Fuel Savings (%)')
                axs[1, 1].set_title('Savings Distribution by Terrain')
                axs[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save or display the figure
        if save_path:
            plt.savefig(save_path)
            print(f"✅ Analysis plots saved to {save_path}")
        else:
            plt.show()

def main():
    """Main function to run diagnostics"""
    print("🔍 CarbonSense AI Model Diagnostics Tool 🔍")
    
    # Create diagnostics tool
    diagnostics = ModelDiagnostics()
    
    # Load optimizer
    if not diagnostics.load_optimizer():
        print("❌ Exiting: Failed to load optimizer")
        return
    
    # Generate test cases
    diagnostics.generate_test_cases(20)
    
    # Run diagnostics
    if not diagnostics.run_diagnostics():
        print("❌ Exiting: Diagnostics failed")
        return
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"model_diagnostics_{timestamp}.json"
    diagnostics.save_results(results_file)
    
    # Generate plots
    plot_file = f"model_analysis_{timestamp}.png"
    try:
        diagnostics.plot_analysis(plot_file)
    except Exception as e:
        print(f"⚠️ Could not generate plots: {str(e)}")
    
    print("\n🔧 Next Steps:")
    print("1. Review the diagnostic results for model issues")
    print("2. Apply the optimizer hotfix if savings calculation issues are found")
    print("3. Follow the model improvement plan for long-term fixes")

if __name__ == "__main__":
    main()
