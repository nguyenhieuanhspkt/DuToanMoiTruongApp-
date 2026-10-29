import sys

sys.stdout.reconfigure(encoding='utf-8')

app_path = r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\app.py"
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add import
target_import = "from backend.exporters.excel_exporter import Excel10SheetExporter"
repl_import = "from backend.exporters.excel_exporter import Excel10SheetExporter\nfrom backend.exporters.excel_6sheet_f1_exporter import Excel6SheetF1Exporter"

content = content.replace(target_import, repl_import)

# 2. Add endpoint
target_endpoint = """@app.get("/api/summary/scenarios")"""
new_endpoint = """@app.get("/api/export/excel-6sheet")
def export_excel_6_sheets_f1():
    items = adapter.load_pakt_items()
    pricing = adapter.load_pricing_config()
    mats = adapter.load_material_pricing()
    tools = adapter.load_msc_tools()
    eq = adapter.load_msc_equipment()
    overhead = adapter.load_overhead_config()

    export_dir = os.path.join(root_dir, "backend", "data")
    out_file = os.path.join(export_dir, "DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx")

    Excel6SheetF1Exporter.export_workbook(
        pakt_items=items,
        pricing_config=pricing,
        materials_db=mats,
        tools_db=tools,
        equipment_db=eq,
        overhead_config=overhead,
        output_path=out_file
    )

    if os.path.exists(out_file):
        try:
            pub_dest = os.path.join(root_dir, 'frontend', 'public', 'DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx')
            shutil.copy2(out_file, pub_dest)
        except Exception:
            pass
        return FileResponse(
            path=out_file,
            filename="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    raise HTTPException(status_code=500, detail="Could not export 6-sheet F1 Excel workbook")

@app.get("/api/summary/scenarios")"""

content = content.replace(target_endpoint, new_endpoint)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated backend/app.py with excel-6sheet endpoint!")
