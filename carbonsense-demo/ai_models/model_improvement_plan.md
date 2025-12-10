# CarbonSense AI Model Improvement Plan

Based on the diagnostic analysis performed on our optimization model, we've identified several issues and recommendations for improvement.

## Current Issues

1. **Zero Savings Issue:**
   - Model generates varying speed recommendations but **always predicts 0.0% fuel savings**
   - None of the test cases (0/20) produced meaningful savings (>0.5%)
   - The model produces the same savings value regardless of input variation

2. **Data Observations:**
   - Data quality is generally good with no missing values
   - Good distribution of key numeric features
   - Some class imbalance in categorical features (soil_type is 81.7% loam)

## Recommended Improvements

### 1. Fix Savings Calculation

The most urgent issue appears to be in how savings are calculated. The model produces different speed recommendations but no meaningful savings.

**Action Items:**
- Verify the savings calculation formula in `carbon_optimizer.py`
- Check if the baseline comparison is working correctly
- Ensure the savings percentage is calculated using `abs(current_speed - optimal_speed) / current_speed * 100`
- Add a diagnostic print statement to see intermediate calculation values

### 2. Improve Model Architecture

**Action Items:**
- Implement a multi-output model that predicts both optimal speed and expected savings
- Add a regularization term that penalizes solutions with near-zero savings
- Consider using a different architecture (e.g., gradient boosting instead of neural network)
- Experiment with ensemble methods that combine multiple optimization strategies

### 3. Enhance Training Process

**Action Items:**
- Use a custom loss function that explicitly penalizes zero-savings predictions
- Implement cross-validation to prevent overfitting
- Apply more aggressive hyperparameter tuning
- Use learning rate schedules to avoid local minima

### 4. Improve Feature Engineering

**Action Items:**
- Create more interaction features (e.g., engine_load × terrain_type)
- Add domain-specific features based on agricultural science principles
- Normalize all input features consistently
- Test feature importance and remove less important features

### 5. Expand Training Data

**Action Items:**
- Balance the soil_type distribution (currently 81.7% loam)
- Add synthetic data points for extreme cases
- Generate more examples with diverse optimization potential
- Validate model on holdout data that wasn't used during training

## Implementation Plan

1. **Short-term (Demo Support):** Continue using the fallback implementation for the demo
2. **Medium-term:** Fix the savings calculation and retrain the model with current data
3. **Long-term:** Implement all improvements and develop a new version of the optimization model

## Tracking Progress

Create a benchmarking system to track model improvement:
- Average savings percentage across test cases
- Number of test cases with meaningful savings
- Diversity of recommended speeds and savings percentages
- Correlation between input variation and output recommendations
