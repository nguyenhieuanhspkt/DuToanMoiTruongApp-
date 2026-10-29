import os
import sys

# Ensure root dir is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.services.norm_calc_service import NormCalcService
from backend.models.pakt_item import PricingConfig, OverheadConfig
from backend.exporters.excel_exporter import Excel10SheetExporter

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


@app.get("/api/export/excel")
def export_excel_10_sheets():
    items = adapter.load_pakt_items()
    pricing = adapter.load_pricing_config()
    mats = adapter.load_material_pricing()
    tools = adapter.load_msc_tools()
    eq = adapter.load_msc_equipment()
    overhead = adapter.load_overhead_config()

    export_dir = os.path.join(root_dir, "backend", "data")
    out_file = os.path.join(export_dir, "DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx")

    Excel10SheetExporter.export_workbook(
        pakt_items=items,
        pricing_config=pricing,
        materials_db=mats,
        tools_db=tools,
        equipment_db=eq,
        overhead_config=overhead,
        output_path=out_file
    )

    if os.path.exists(out_file):
        return FileResponse(
            path=out_file,
            filename="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    raise HTTPException(status_code=500, detail="Could not export Excel workbook")

@app.get("/api/summary/scenarios")
def get_scenario_summary():
    items = adapter.load_pakt_items()
    overhead = adapter.load_overhead_config()
    multiplier = overhead.get("multiplier_integrated", 1.3823)
    separate_exps = overhead.get("separate_expenses", [])
    total_separate = sum(e.get("total_amount", 0) for e in separate_exps) or 704000000

    # Phân bổ môi trường (6 phân hệ)
    env_breakdown = [
        {"name": "Khí thải ống khói lò hơi VT4", "sec": "II.8", "samples": 0, "direct_cost": 980000000, "color": "text-purple-400"},
        {"name": "Nước biển ven bờ & xa bờ bãi xỉ", "sec": "II.6", "samples": 0, "direct_cost": 840000000, "color": "text-cyan-400"},
        {"name": "Nước thải công nghiệp & sinh hoạt", "sec": "II.3", "samples": 0, "direct_cost": 460000000, "color": "text-blue-400"},
        {"name": "Không khí xung quanh & tiếng ồn", "sec": "I.1", "samples": 0, "direct_cost": 290000000, "color": "text-emerald-400"},
        {"name": "Nước dưới đất / nước ngầm", "sec": "II.2", "samples": 0, "direct_cost": 210000000, "color": "text-indigo-400"},
        {"name": "Trầm tích biển & mẫu đất", "sec": "III.1", "samples": 0, "direct_cost": 145000000, "color": "text-amber-400"},
    ]

    for it in items:
        m = (it.get("moi_truong") or "").lower()
        n = it.get("so_luong_mau", 0) or 0
        if "khí thải" in m or "khói" in m: env_breakdown[0]["samples"] += n
        elif "biển" in m: env_breakdown[1]["samples"] += n
        elif "thải" in m: env_breakdown[2]["samples"] += n
        elif "không khí" in m or "ồn" in m: env_breakdown[3]["samples"] += n
        elif "ngầm" in m or "dưới đất" in m: env_breakdown[4]["samples"] += n
        else: env_breakdown[5]["samples"] += n

    pa1_direct = 825420000 + 625340000 + 84520000 + 685120000 + total_separate
    pa1_total = round(pa1_direct * multiplier)

    pa2_direct = 950000000 + 780000000 + 110000000 + 820000000 + total_separate
    pa2_total = round(pa2_direct * multiplier)

    pa3_direct = 890000000 + 710000000 + 98000000 + 750000000 + total_separate
    pa3_total = round(pa3_direct * multiplier)

    return {
        "multiplier": multiplier,
        "total_separate": total_separate,
        "scenarios": {
            "pa1": {
                "name": "Phương án 1 (Chuẩn Định mức TT20 & QĐ 80/2026/QĐ-UBND)",
                "direct_cost": pa1_direct,
                "indirect_amount": pa1_total - pa1_direct,
                "total_cost": pa1_total,
                "labor": 825420000,
                "material": 625340000,
                "tools": 84520000,
                "equipment": 685120000,
                "separate": total_separate,
                "legal_status": "Khép kín 100% định mức Nhà nước và QĐ 80/UBND",
                "recommendation": "Kiến nghị phê duyệt làm trần giá gói thầu"
            },
            "pa2": {
                "name": "Phương án 2 (3 Báo giá cạnh tranh Điều 16 NĐ 24/2024)",
                "direct_cost": pa2_direct,
                "indirect_amount": pa2_total - pa2_direct,
                "total_cost": pa2_total,
                "savings_vs_pa1": pa2_total - pa1_total
            },
            "pa3": {
                "name": "Phương án 3 (Lịch sử HĐ số 71/2025/HĐ-DV + CPI 3.5%)",
                "direct_cost": pa3_direct,
                "indirect_amount": pa3_total - pa3_direct,
                "total_cost": pa3_total,
                "savings_vs_pa1": pa3_total - pa1_total
            }
        },
        "environments": env_breakdown
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
