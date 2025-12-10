"""
CarbonSense AI - API Smoke Tests
Tests to verify the optimization endpoint is working correctly
"""

import os
import sys
import pytest
import requests
import json

# Add the backend directory to the path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

# Add the ai_models directory to the path
ai_models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_models'))
sys.path.insert(0, ai_models_dir)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_optimization_endpoint(client):
    """Test the optimization endpoint with a known payload"""
    # Test payload that matches model features
    payload = {
        'speed_mph': 7.5,
        'engine_load_pct': 75,
        'implement_width_ft': 24,
        'field_acres': 160,
        'weather_factor': 1.0,
        'operation_type': 'tillage',
        'soil_type': 'loam',
        'terrain_type': 'rolling',
        'fuel_rate_gph': 15,
        'fuel_cost_per_hour': 58.52
    }

    response = client.post('/api/optimize', json=payload)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'optimized_parameters' in data
    assert 'savings' in data
    
    # Verify optimization produces meaningful results
    assert data['optimized_parameters']['speed_mph'] > 0
    assert data['savings']['fuel_reduction_pct'] > 0
    assert data['savings']['co2_reduction_pct'] > 0
    assert data['savings']['cost_savings_per_hour'] > 0
    
    # Verify implementation details
    assert 'implementation' in data
    assert 'action' in data['implementation']
    assert 'expected_result' in data['implementation']
    assert 'confidence' in data['implementation']

def test_optimization_with_edge_cases(client):
    """Test optimization with edge cases"""
    edge_cases = [
        {
            # High speed, high load
            'speed_mph': 12.0,
            'engine_load_pct': 95,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.0,
            'operation_type': 'tillage',
            'soil_type': 'clay',
            'terrain_type': 'hilly',
            'fuel_rate_gph': 18,
            'fuel_cost_per_hour': 70.0
        },
        {
            # Low speed, low load
            'speed_mph': 4.0,
            'engine_load_pct': 45,
            'implement_width_ft': 24,
            'field_acres': 160,
            'weather_factor': 1.0,
            'operation_type': 'planter',
            'soil_type': 'sandy',
            'terrain_type': 'flat',
            'fuel_rate_gph': 12,
            'fuel_cost_per_hour': 45.0
        }
    ]

    for case in edge_cases:
        response = client.post('/api/optimize', json=case)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Verify each edge case gets meaningful recommendations
        assert data['optimized_parameters']['speed_mph'] > 0
        assert data['savings']['fuel_reduction_pct'] > 0
        
        # High load case should recommend speed reduction
        if case['engine_load_pct'] > 90:
            assert data['optimized_parameters']['speed_mph'] < case['speed_mph']
            
        # Low speed case should potentially recommend speed increase
        if case['speed_mph'] < 5.0:
            assert data['optimized_parameters']['speed_mph'] > case['speed_mph']

def test_recommendations_consistency(client):
    """Test that recommendations are consistent for similar inputs"""
    base_payload = {
        'speed_mph': 7.5,
        'engine_load_pct': 75,
        'implement_width_ft': 24,
        'field_acres': 160,
        'weather_factor': 1.0,
        'operation_type': 'tillage',
        'soil_type': 'loam',
        'terrain_type': 'rolling',
        'fuel_rate_gph': 15,
        'fuel_cost_per_hour': 58.52
    }

    # Make two similar requests with slight variations
    payload1 = base_payload.copy()
    payload2 = base_payload.copy()
    payload2['speed_mph'] = 7.6  # Slightly different speed

    response1 = client.post('/api/optimize', json=payload1)
    response2 = client.post('/api/optimize', json=payload2)

    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)

    # Recommendations should be similar but not identical for similar inputs
    assert abs(data1['optimized_parameters']['speed_mph'] - data2['optimized_parameters']['speed_mph']) < 1.0
    assert abs(data1['savings']['fuel_reduction_pct'] - data2['savings']['fuel_reduction_pct']) < 5.0

if __name__ == '__main__':
    # Run tests with more detailed output
    pytest.main([__file__, '-v'])
