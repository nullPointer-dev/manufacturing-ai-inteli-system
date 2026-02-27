"""
Quick test to verify optimizer is working
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integration_api import api_optimize_auto

print("Testing optimizer...")
print("=" * 60)

try:
    result = api_optimize_auto(mode="balanced")
    print("✅ Success!")
    print(f"Status: {result.get('status')}")
    print(f"Has top_result: {'top_result' in result}")
    
    if result.get('status') == 'success':
        top = result.get('top_result')
        if top:
            print(f"\nOptimal Solution:")
            print(f"  Quality: {top.get('Quality', 'N/A')}")
            print(f"  Yield: {top.get('Yield', 'N/A')}")
            print(f"  Performance: {top.get('Performance', 'N/A')}")
            print(f"  Energy: {top.get('Energy', 'N/A')}")
            print(f"  CO2: {top.get('CO2', 'N/A')}")
            print(f"  Proposal: {result.get('proposal')}")
            print(f"  Cluster ID: {result.get('cluster_id')}")
    else:
        print(f"❌ No solution found: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
