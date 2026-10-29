import os
import sys

# Ensure root dir is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.services.norm_calc_service import NormCalcService
from backend.models.pakt_item import PricingConfig, OverheadConfig

app = FastAPI(
    title="DuToanMoiTruongApp API",
    description="Backend Service Thẩm Định Dự Toán Quan Trắc Môi Trường EVN Vĩnh Tân 4 theo Thông tư 20 & Văn bản 5691/EVN-MTPTBV",
    version="0.1.0"
)

# Enable CORS for local Vite / frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adapter = OneDriveAdapter()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DuToanMoiTruongApp",
        "version": "0.1.0-baseline",
        "storage_path": adapter.data_dir
    }

@app.get("/api/pakt-items")
def get_pakt_items() -> List[Dict[str, Any]]:
    items = adapter.load_pakt_items()
    if not items:
        raise HTTPException(status_code=404, detail="No PAKT items found in OneDrive storage")
    return items

@app.get("/api/summary-stats")
def get_summary_stats():
    items = adapter.load_pakt_items()
    totals = NormCalcService.calculate_totals(items)
    pricing = adapter.load_pricing_config()
    overhead = adapter.load_overhead_config()
    return {
        "totals": totals,
        "pricing": pricing,
        "overhead": overhead
    }

@app.get("/api/pricing-config")
def get_pricing_config():
    return adapter.load_pricing_config()

@app.post("/api/pricing-config")
def update_pricing_config(config: Dict[str, Any]):
    adapter.save_pricing_config(config)
    return {"status": "success", "message": "Updated pricing configuration"}

@app.get("/api/pricing/labor")
def get_labor_pricing():
    return adapter.load_pricing_config()

@app.post("/api/pricing/labor")
def update_labor_pricing(config: Dict[str, Any]):
    current = adapter.load_pricing_config()
    current.update(config)
    adapter.save_pricing_config(current)
    return {"status": "success", "message": "Updated labor pricing", "data": current}

@app.get("/api/overhead-config")
def get_overhead_config():
    return adapter.load_overhead_config()

@app.post("/api/overhead-config")
def update_overhead_config(config: Dict[str, Any]):
    adapter.save_overhead_config(config)
    return {"status": "success", "message": "Updated overhead configuration", "data": config}

@app.get("/api/tt20/sections")
def get_tt20_sections():
    return adapter.get_tt20_sections_summary()

@app.get("/api/tt20/database")
def get_tt20_database():
    db = adapter.load_tt20_norm_database()
    if not db:
        raise HTTPException(status_code=404, detail="TT20 Norm Database not found in OneDrive storage")
    return db

@app.get("/api/tt20/lookup/{code}")
def lookup_tt20_parameter(code: str):
    res = adapter.lookup_tt20_parameter(code)
    if not res:
        raise HTTPException(status_code=404, detail=f"Parameter code '{code}' not found in TT20 database")
    return res

@app.get("/api/norms/materials-summary")
def get_materials_summary():
    items = adapter.load_pakt_items()
    return NormCalcService.calculate_material_summary(items)

@app.get("/api/norms/breakdown/{item_id}")
def get_item_norm_breakdown(item_id: int):
    items = adapter.load_pakt_items()
    target = next((it for it in items if it.get("id") == item_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"PAKT Item with id {item_id} not found")
    return {
        "item": target,
        "labor": NormCalcService.extract_labor_details(target),
        "materials": NormCalcService.extract_materials_details(target),
        "tools": NormCalcService.extract_tools_details(target),
        "equipment": NormCalcService.extract_equipment_details(target)
    }

@app.get("/api/material-pricing")
def get_material_pricing():
    return adapter.load_material_pricing()

@app.post("/api/material-pricing")
def update_material_pricing(data: Dict[str, Any]):
    adapter.save_material_pricing(data)
    return {"status": "success", "message": "Updated material pricing successfully", "total_items": len(data.get("items", []))}


@app.get("/api/msc-lookup/tools")
def get_msc_tools():
    return adapter.load_msc_tools()

@app.post("/api/msc-lookup/tools")
def update_msc_tools(data: Dict[str, Any]):
    adapter.save_msc_tools(data)
    return {"status": "success", "message": "Updated MSC tools pricing", "total": len(data.get("items", []))}

@app.get("/api/msc-lookup/equipment")
def get_msc_equipment():
    return adapter.load_msc_equipment()

@app.post("/api/msc-lookup/equipment")
def update_msc_equipment(data: Dict[str, Any]):
    adapter.save_msc_equipment(data)
    return {"status": "success", "message": "Updated MSC equipment pricing", "total": len(data.get("items", []))}

@app.get("/api/msc-lookup/materials")
def get_msc_materials():
    return adapter.load_msc_materials()

@app.post("/api/msc-lookup/materials")
def update_msc_materials(data: Dict[str, Any]):
    adapter.save_msc_materials(data)
    return {"status": "success", "message": "Updated MSC materials pricing", "total": len(data.get("items", []))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
