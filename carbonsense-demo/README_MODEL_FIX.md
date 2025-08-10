# CarbonSense AI Model Fix Toolkit

This toolkit contains solutions to fix the issues with the CarbonSense AI model that is producing 0% fuel savings despite providing different speed recommendations.

## Files Included

1. **optimizer_hotfix.py**: A patched version of the CarbonOptimizer that fixes the savings calculation issue.
2. **apply_hotfix.py**: A script to easily apply the hotfix to your application.
3. **model_improvement_plan.md**: A comprehensive plan for fixing and improving the model.
4. **ai_models/diagnostics/debug_optimizer.py**: A diagnostic tool to analyze and debug model performance.

## Quick Start

### Option 1: Apply the Hotfix (Recommended for Immediate Fix)

The hotfix patches the savings calculation while preserving the model's speed recommendations:

```bash
# Navigate to your project directory
cd path/to/carbonsense-demo

# Run the hotfix application script
python apply_hotfix.py
```

The script will:
1. Test the patched optimizer
2. Ask for confirmation before applying
3. Back up your original files
4. Apply the patch to your application

### Option 2: Run Diagnostics for Detailed Analysis

For a deeper understanding of the model issues:

```bash
# Navigate to your project directory
cd path/to/carbonsense-demo

# Run the model diagnostics
python -m ai_models.diagnostics.debug_optimizer
```

This will:
1. Generate test cases to evaluate the model
2. Analyze model performance and issues
3. Save diagnostic results and visualizations
4. Provide recommendations for fixes

## Understanding the Issues

The main issue with the CarbonOptimizer model is that it's calculating 0% fuel savings despite producing different speed recommendations. The diagnostics show:

1. The model correctly varies its speed recommendations based on input conditions
2. The savings calculation logic is broken, consistently producing 0% savings
3. The correlation between speed differences and savings is poor or non-existent

## How the Hotfix Works

The patched optimizer:

1. Preserves the original model's speed recommendations
2. Overrides the savings calculation with a physics-based approach
3. Accounts for terrain type, soil conditions, and engine load
4. Ensures realistic savings estimates (5-25%)
5. Adds additional contextual recommendations

## Long-term Model Improvement

For a comprehensive fix, refer to `model_improvement_plan.md` which includes:

1. Short-term fixes (implemented in the hotfix)
2. Mid-term improvements (1-3 months)
3. Long-term enhancements (3-6 months)
4. Implementation plan with timeline and resources

## Requirements

- Python 3.7+
- NumPy, Pandas for the diagnostic tool
- Matplotlib, Tabulate for visualization and reporting (only for diagnostics)

## Backup and Safety

Before applying any changes:
- The hotfix script automatically backs up original files
- Original model behavior can be restored from backups if needed
- Test thoroughly in a development environment first

## Support

If you encounter any issues with these tools, please check the following:

1. Ensure the correct file paths are used in the scripts
2. Verify that the original model structure matches the expected interface
3. Check that all required dependencies are installed
