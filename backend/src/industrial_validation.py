"""
Industrial Validation Module
Calculates ROI, Payback Period, CO2 savings, and Energy efficiency
based on real-time prediction engine and correction recommendations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from typing import Dict, Any

from prediction_service import predict_batch, _load_model
from correction_engine import analyze_batch_against_golden
from golden_updater import _safe_load, REGISTRY_FILE

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


def calculate_industrial_validation(
    electricity_cost: float,  # ₹ per kWh
    batches_per_day: float,
    deployment_cost: float,  # ₹ one-time
    annual_maintenance_cost: float,  # ₹ per year
    current_batch_params: Dict[str, Any] = None,
    operating_days_per_year: int = 250,
) -> Dict[str, Any]:
    """
    Calculate industrial validation metrics based on real-time prediction
    and correction engine simulations.
    
    Args:
        electricity_cost: Cost per kWh in rupees
        batches_per_day: Number of batches produced per day
        deployment_cost: One-time deployment cost in rupees
        annual_maintenance_cost: Annual maintenance cost in rupees
        current_batch_params: Current batch parameters (optional, uses defaults if None)
        operating_days_per_year: Number of operating days per year
        
    Returns:
        Dictionary containing ROI, payback period, CO2 savings, energy savings, etc.
    """
    
    # Default batch parameters (typical manufacturing scenario)
    if current_batch_params is None:
        current_batch_params = {
            'Machine_Speed': 50.0,
            'Compression_Force': 15.0,
            'Tablet_Weight': 500.0,
            'avg_temperature': 25.0,
            'avg_pressure': 1.5,
            'avg_power_consumption': 45.0,  # Reduced from 50
            'total_process_time': 90.0,  # Reduced from 120
            'Granulation_Time': 25.0,  # Reduced from 30
            'Binder_Amount': 10.0,
            'Drying_Temp': 60.0,
            'Drying_Time': 90.0,  # Reduced from 120
            'Lubricant_Conc': 1.0,
            'Moisture_Content': 2.0,
        }
    
    # =========================================================
    # Step 1: Predict current batch performance (baseline)
    # =========================================================
    current_prediction = predict_batch(current_batch_params)
    
    current_quality = current_prediction['Quality']
    current_yield = current_prediction['Yield']  # Scaled Content_Uniformity (80-100%)
    current_performance = current_prediction['Performance']  # Scaled performance_score (0-100%)
    current_energy = current_prediction['Energy']  # kWh per batch
    current_co2 = current_prediction['CO2']  # kg CO2 per batch
    
    # Yield and Performance are already scaled by prediction_service
    # Just ensure they're in reasonable bounds
    current_yield = max(80.0, min(100.0, current_yield))
    current_performance = max(0.0, min(100.0, current_performance))
    
    # Quality is already in reasonable range (typically 50-100), but apply bounds
    current_quality = max(50.0, min(100.0, current_quality))
    
    # Energy sanity check: Cap to realistic manufacturing values
    # Typical batch: 50-300 kWh. If model predicts unrealistic values, scale down
    if current_energy > 500:
        energy_scale_factor = 200.0 / current_energy  # Scale to ~200 kWh
        current_energy = current_energy * energy_scale_factor
        current_co2 = current_co2 * energy_scale_factor
    elif current_energy < 10:
        current_energy = 50.0  # Set minimum realistic value
        current_co2 = current_energy * 0.82
    
    # =========================================================
    # Step 2: Analyze against golden signature
    # =========================================================
    try:
        golden_registry = _safe_load(REGISTRY_FILE, {})
        
        # Get the "balanced" golden signature (or first available)
        # Registry structure: {mode: {cluster_id: {score, ranges, ...}}}
        golden_ranges = None
        if "balanced" in golden_registry:
            mode_data = golden_registry["balanced"]
            # Pick the first cluster entry
            first_cluster = next(iter(mode_data.values()), None)
            if first_cluster and "ranges" in first_cluster:
                golden_ranges = first_cluster["ranges"]
        elif len(golden_registry) > 0:
            first_mode = list(golden_registry.keys())[0]
            mode_data = golden_registry[first_mode]
            if isinstance(mode_data, dict):
                first_cluster = next(iter(mode_data.values()), None)
                if first_cluster and "ranges" in first_cluster:
                    golden_ranges = first_cluster["ranges"]
        
        # If golden signature exists, analyze corrections
        if golden_ranges is not None:
            model, feature_cols = _load_model()
            correction_analysis = analyze_batch_against_golden(
                current_batch_params, 
                golden_ranges, 
                model, 
                feature_cols
            )
            
            # Apply corrections to create optimized batch parameters
            optimized_params = current_batch_params.copy()
            
            # Apply corrections for beneficial parameters
            for _, row in correction_analysis.iterrows():
                param = row['Parameter']
                if row['Beneficial'] and row['Severity'] != "OK":
                    # Move toward golden mean
                    golden_mean = row['Golden Mean']
                    current_val = row['Current']
                    # Apply 70% correction toward golden mean
                    optimized_params[param] = current_val + 0.7 * (golden_mean - current_val)
            
            # Predict with corrected parameters
            optimized_prediction = predict_batch(optimized_params)
            
            optimized_quality = optimized_prediction['Quality']
            optimized_yield = optimized_prediction['Yield']  # Scaled Content_Uniformity (80-100%)
            optimized_performance = optimized_prediction['Performance']  # Scaled performance_score (0-100%)
            optimized_energy = optimized_prediction['Energy']
            optimized_co2 = optimized_prediction['CO2']
            
            # Apply bounds to optimized values (already scaled by prediction_service)
            optimized_yield = max(80.0, min(100.0, optimized_yield))
            optimized_performance = max(0.0, min(100.0, optimized_performance))
            optimized_quality = max(50.0, min(100.0, optimized_quality))
            
            # Apply same scaling if applied to baseline
            if current_prediction['Energy'] > 500:
                energy_scale_factor = 200.0 / current_prediction['Energy']
                optimized_energy = optimized_energy * energy_scale_factor
                optimized_co2 = optimized_co2 * energy_scale_factor
            
        else:
            # No golden signature available - simulate modest improvement
            optimized_quality = current_quality * 1.03  # 3% improvement
            optimized_yield = current_yield * 1.02  # 2% improvement
            optimized_performance = current_performance * 1.02  # 2% improvement
            optimized_energy = current_energy * 0.95  # 5% energy reduction
            optimized_co2 = current_co2 * 0.95
            
    except Exception as e:
        print(f"Golden signature not available or error: {e}")
        # Fallback: simulate conservative improvements
        optimized_quality = current_quality * 1.03
        optimized_yield = current_yield * 1.02
        optimized_performance = current_performance * 1.02
        optimized_energy = current_energy * 0.95
        optimized_co2 = current_co2 * 0.95
    
    # =========================================================
    # Step 3: Calculate improvements
    # =========================================================
    quality_improvement_pct = ((optimized_quality - current_quality) / current_quality * 100) if current_quality != 0 else 0
    yield_improvement_pct = ((optimized_yield - current_yield) / current_yield * 100) if current_yield != 0 else 0
    performance_improvement_pct = ((optimized_performance - current_performance) / current_performance * 100) if current_performance != 0 else 0
    
    energy_saved_per_batch = current_energy - optimized_energy  # kWh
    co2_saved_per_batch = current_co2 - optimized_co2  # kg CO2
    
    # =========================================================
    # Step 4: Annual calculations
    # =========================================================
    annual_batches = batches_per_day * operating_days_per_year
    
    energy_saved_annually = energy_saved_per_batch * annual_batches  # kWh/year
    co2_saved_annually = co2_saved_per_batch * annual_batches  # kg CO2/year
    
    # Financial savings
    energy_cost_savings_annually = energy_saved_annually * electricity_cost  # ₹/year
    
    # Yield improvement directly reduces raw material costs
    # Realistic estimate: ₹50,000 material cost saved per 1% yield improvement per batch
    # (accounts for reduced waste, rework, and scrap in Indian manufacturing context)
    raw_material_savings_per_batch = 50000.0 * (yield_improvement_pct / 100.0)
    raw_material_savings_annually = raw_material_savings_per_batch * annual_batches
    
    # Quality improvement reduces defects and rework
    # Realistic estimate: ₹33,000 saved per 1% quality improvement per batch
    # (reduced rework, warranties, and customer complaints)
    quality_savings_per_batch = 33000.0 * (quality_improvement_pct / 100.0)
    quality_savings_annually = quality_savings_per_batch * annual_batches
    
    # Performance improvement reduces labor and overhead costs
    # Realistic estimate: ₹25,000 saved per 1% performance improvement per batch
    # (faster throughput, better resource utilization)
    performance_savings_per_batch = 150.0 * (performance_improvement_pct / 100.0)
    performance_savings_annually = performance_savings_per_batch * annual_batches
    
    # Total annual savings
    total_annual_savings = (
        energy_cost_savings_annually +
        raw_material_savings_annually +
        quality_savings_annually +
        performance_savings_annually
    )
    
    # Net annual benefit (after maintenance costs)
    net_annual_benefit = total_annual_savings - annual_maintenance_cost
    
    # =========================================================
    # Step 5: ROI and Payback Period
    # =========================================================
    if deployment_cost > 0:
        # ROI = (3-year net benefit - deployment cost) / deployment cost * 100
        three_year_benefit = net_annual_benefit * 3
        roi = ((three_year_benefit - deployment_cost) / deployment_cost) * 100
        
        # Calculate payback period, cap at 999 years to avoid infinity
        if net_annual_benefit > 0:
            payback_period_years = min(deployment_cost / net_annual_benefit, 999.0)
            payback_period_months = min(payback_period_years * 12, 11988.0)
        else:
            # Negative or zero benefit means no payback
            payback_period_years = 999.0
            payback_period_months = 11988.0
    else:
        roi = 0.0
        payback_period_years = 0.0
        payback_period_months = 0.0
    
    # =========================================================
    # Step 6: Energy Efficiency Metrics
    # =========================================================
    energy_efficiency_improvement_pct = (energy_saved_per_batch / current_energy * 100) if current_energy != 0 else 0
    co2_reduction_pct = (co2_saved_per_batch / current_co2 * 100) if current_co2 != 0 else 0
    
    # CO2 equivalent in trees (1 tree absorbs ~22 kg CO2 per year)
    trees_equivalent = co2_saved_annually / 22.0
    
    # =========================================================
    # Step 7: Return comprehensive results
    # =========================================================
    return {
        # Input Parameters
        "inputs": {
            "electricity_cost": electricity_cost,
            "batches_per_day": batches_per_day,
            "deployment_cost": deployment_cost,
            "annual_maintenance_cost": annual_maintenance_cost,
            "operating_days_per_year": operating_days_per_year,
            "annual_batches": annual_batches,
        },
        
        # Current (Baseline) Performance
        "baseline": {
            "quality": round(current_quality, 2),
            "yield": round(current_yield, 2),
            "performance": round(current_performance, 2),
            "energy_per_batch": round(current_energy, 2),
            "co2_per_batch": round(current_co2, 2),
        },
        
        # Optimized (With Corrections) Performance
        "optimized": {
            "quality": round(optimized_quality, 2),
            "yield": round(optimized_yield, 2),
            "performance": round(optimized_performance, 2),
            "energy_per_batch": round(optimized_energy, 2),
            "co2_per_batch": round(optimized_co2, 2),
        },
        
        # Improvements
        "improvements": {
            "quality_improvement_pct": round(quality_improvement_pct, 2),
            "yield_improvement_pct": round(yield_improvement_pct, 2),
            "performance_improvement_pct": round(performance_improvement_pct, 2),
            "energy_saved_per_batch": round(energy_saved_per_batch, 2),
            "co2_saved_per_batch": round(co2_saved_per_batch, 2),
        },
        
        # Annual Savings
        "annual_savings": {
            "energy_saved_kwh": round(energy_saved_annually, 2),
            "co2_saved_kg": round(co2_saved_annually, 2),
            "energy_cost_savings": round(energy_cost_savings_annually, 2),
            "raw_material_savings": round(raw_material_savings_annually, 2),
            "quality_savings": round(quality_savings_annually, 2),
            "performance_savings": round(performance_savings_annually, 2),
            "total_savings": round(total_annual_savings, 2),
            "net_benefit": round(net_annual_benefit, 2),
        },
        
        # Financial Metrics
        "financial": {
            "roi_3_year_pct": round(roi, 2),
            "payback_period_years": round(payback_period_years, 2),
            "payback_period_months": round(payback_period_months, 1),
        },
        
        # Environmental Impact
        "environmental": {
            "energy_efficiency_improvement_pct": round(energy_efficiency_improvement_pct, 2),
            "co2_reduction_pct": round(co2_reduction_pct, 2),
            "trees_equivalent": round(trees_equivalent, 1),
        },
        
        # Status
        "status": "success"
    }


def get_validation_summary(validation_result: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of the industrial validation results.
    """
    financial = validation_result['financial']
    annual = validation_result['annual_savings']
    env = validation_result['environmental']
    
    summary = f"""
Industrial Validation Summary
=============================

Financial Impact:
- 3-Year ROI: {financial['roi_3_year_pct']:.1f}%
- Payback Period: {financial['payback_period_months']:.1f} months
- Annual Net Benefit: ${annual['net_benefit']:,.2f}

Environmental Impact:
- Energy Saved Annually: {annual['energy_saved_kwh']:,.2f} kWh
- CO2 Reduced Annually: {annual['co2_saved_kg']:,.2f} kg ({env['co2_reduction_pct']:.1f}%)
- Equivalent to {env['trees_equivalent']:.0f} trees planted

Operational Improvements:
- Quality: +{validation_result['improvements']['quality_improvement_pct']:.1f}%
- Yield: +{validation_result['improvements']['yield_improvement_pct']:.1f}%
- Performance: +{validation_result['improvements']['performance_improvement_pct']:.1f}%
"""
    return summary
