/* CarbonSense AI - Live Metrics Update Fix */

// Function to update the top metric cards with real API data
function updateLiveMetrics() {
    console.log('🔄 Updating live metrics from API...');
    
    fetch('/api/model-performance')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Live metrics data:', data);
            
            // Update Model Accuracy
            const accuracyElement = document.getElementById('modelAccuracy');
            if (accuracyElement && data.model_status) {
                accuracyElement.textContent = data.model_status.accuracy.toFixed(1) + '%';
            }
            
            // Update Training Samples
            const samplesElement = document.getElementById('trainingSamples');
            if (samplesElement && data.model_status) {
                samplesElement.textContent = data.model_status.training_samples.toLocaleString();
            }
            
            // Update Avg Fuel Savings
            const savingsElement = document.getElementById('avgFuelSavings');
            if (savingsElement && data.model_status) {
                savingsElement.textContent = data.model_status.avg_fuel_savings.toFixed(1) + '%';
            }
            
            // Update Prediction Time (fix: ms not s)
            const timeElement = document.getElementById('predictionTime');
            if (timeElement && data.model_status) {
                timeElement.textContent = data.model_status.prediction_time_ms.toFixed(1) + 'ms';
            }
            
            console.log('✅ All metric cards updated with live data');
        })
        .catch(error => {
            console.error('❌ Error fetching live metrics:', error);
        });
}

// Update immediately when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Loading live metrics...');
    updateLiveMetrics();
    
    // Update every 10 seconds
    setInterval(updateLiveMetrics, 10000);
});

// Manual update function for testing
function refreshMetrics() {
    updateLiveMetrics();
}