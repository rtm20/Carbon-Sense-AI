"""
CarbonSense AI - Hotfix Integration Script
Integrates the patched optimizer into the application
"""

import os
import sys
import importlib
import shutil
from datetime import datetime

def apply_hotfix():
    """Apply the optimizer hotfix to the application"""
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ai_models_dir = os.path.join(base_dir, 'ai_models')
    
    # Check if the hotfix exists
    hotfix_path = os.path.join(ai_models_dir, 'optimizer_hotfix.py')
    if not os.path.exists(hotfix_path):
        print(f"❌ Hotfix file not found at {hotfix_path}")
        return False
    
    # Check if the original optimizer exists
    optimizer_path = os.path.join(ai_models_dir, 'carbon_optimizer.py')
    if not os.path.exists(optimizer_path):
        print(f"❌ Original optimizer not found at {optimizer_path}")
        return False
    
    # Backup the original optimizer
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{optimizer_path}.backup_{backup_time}"
    try:
        shutil.copy2(optimizer_path, backup_path)
        print(f"✅ Original optimizer backed up to {backup_path}")
    except Exception as e:
        print(f"❌ Failed to backup optimizer: {str(e)}")
        return False
    
    # Test the patched optimizer
    print("\n📊 Testing the patched optimizer...")
    try:
        # Add ai_models directory to path if not already there
        if ai_models_dir not in sys.path:
            sys.path.insert(0, ai_models_dir)
        
        # Dynamically import the hotfix
        hotfix_module = importlib.import_module('optimizer_hotfix')
        
        # Run the test function
        hotfix_module.test_patched_optimizer()
        print("✅ Test completed")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("⚠️ Hotfix NOT applied. Original optimizer is still in place.")
        return False
    
    # Ask for confirmation to apply the hotfix
    confirm = input("\n⚠️ Would you like to apply the patched optimizer? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Hotfix application cancelled. Original optimizer is still in place.")
        return False
    
    # Apply the hotfix by modifying the application to use the patched optimizer
    app_path = os.path.join(base_dir, 'app.py')
    if os.path.exists(app_path):
        try:
            # Read the app file
            with open(app_path, 'r') as file:
                content = file.read()
            
            # Check if the import statement exists
            original_import = "from ai_models.carbon_optimizer import CarbonOptimizer"
            new_import = "from ai_models.optimizer_hotfix import PatchedCarbonOptimizer as CarbonOptimizer"
            
            if original_import in content:
                # Replace the import statement
                modified_content = content.replace(original_import, new_import)
                
                # Backup the app file
                app_backup_path = f"{app_path}.backup_{backup_time}"
                shutil.copy2(app_path, app_backup_path)
                print(f"✅ App file backed up to {app_backup_path}")
                
                # Write the modified content
                with open(app_path, 'w') as file:
                    file.write(modified_content)
                
                print("✅ Hotfix applied successfully! Application now uses the patched optimizer.")
            else:
                print(f"❌ Could not find the import statement in {app_path}")
                print("⚠️ Please manually modify your application to use the patched optimizer.")
                print(f"Add this import: from ai_models.optimizer_hotfix import PatchedCarbonOptimizer as CarbonOptimizer")
        except Exception as e:
            print(f"❌ Failed to apply hotfix to app.py: {str(e)}")
            return False
    else:
        print(f"❌ Application file not found at {app_path}")
        print("⚠️ Please manually modify your application to use the patched optimizer.")
        print(f"Add this import: from ai_models.optimizer_hotfix import PatchedCarbonOptimizer as CarbonOptimizer")
    
    print("\n🔍 Next Steps:")
    print("1. Restart your application to apply the hotfix")
    print("2. Monitor the application logs to ensure it's working correctly")
    print("3. Check that the savings calculations are now correct")
    print("4. If any issues occur, you can restore from the backup files")
    
    return True

if __name__ == "__main__":
    print("🔧 CarbonSense AI Hotfix Integration Script 🔧")
    apply_hotfix()
