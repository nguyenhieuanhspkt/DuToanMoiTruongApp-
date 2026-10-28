import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


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
    assert "labor_rates" in pricing or "labor_rates_3072" in pricing
    print("PASS: Pricing configuration for labor rates loaded successfully.")

    # TT20 Norm Database checks
    tt20_db = adapter.load_tt20_norm_database()
    assert len(tt20_db.get("sections", {})) == 13, f"Expected 13 sections, got {len(tt20_db.get('sections', {}))}"
    assert len(tt20_db.get("parameter_index", {})) >= 700, f"Expected >= 700 parameters, got {len(tt20_db.get('parameter_index', {}))}"
    print(f"PASS: TT20 Database loaded with {len(tt20_db['sections'])} sections and {len(tt20_db['parameter_index'])} parameters.")

    sec_summary = adapter.get_tt20_sections_summary()
    assert len(sec_summary) == 13
    print(f"PASS: TT20 Sections summary retrieved successfully (13 sections).")

    lookup = adapter.lookup_tt20_parameter("1KK1a")
    assert lookup is not None and lookup["section_id"] == "II.1"
    print(f"PASS: Parameter lookup for '1KK1a' succeeded -> {lookup['parameter']['ten_thong_so']}.")


if __name__ == "__main__":
    test_data_integrity()
    print("ALL INTEGRITY TESTS PASSED 100%!")
