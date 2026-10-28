import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.services.norm_calc_service import NormCalcService

def test_data_integrity():
    adapter = OneDriveAdapter()
    items = adapter.load_pakt_items()
    assert len(items) == 253, f"Expected 253 items, got {len(items)}"
    print(f"PASS: Loaded exactly 253 items from OneDrive storage.")

    totals = NormCalcService.calculate_totals(items)
    assert totals["total_items"] == 253
    assert totals["total_samples"] > 0
    assert totals["total_days"] > 0
    print(f"PASS: Totals calculated -> Samples: {totals['total_samples']:,}, Total days: {totals['total_days']:,}")

    pricing = adapter.load_pricing_config()
    assert "labor_rates_3072" in pricing
    print("PASS: Pricing configuration for VB 3072 loaded successfully.")

if __name__ == "__main__":
    test_data_integrity()
    print("ALL INTEGRITY TESTS PASSED 100%!")
