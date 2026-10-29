import sys

sys.stdout.reconfigure(encoding='utf-8')

tab10_path = r"D:\TaskApp_kiet\DuToanMoiTruongApp\frontend\src\tabs\Tab10_TongHopKinhPhi.tsx"
with open(tab10_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Top actions replacement
target1 = """          <a
            href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
            download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow-md shadow-emerald-600/30 transition active:scale-95 flex items-center space-x-1.5"
            title="Xuất trọn vẹn tệp Excel 10 Sheet động khép kín công thức"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
            <span>Xuất Excel 10 Sheet (Công Thức Sống)</span>
          </a>"""

replacement1 = """          <a
            href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
            download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
            className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-bold shadow-md shadow-amber-600/30 transition active:scale-95 flex items-center space-x-1.5"
            title="Tải tệp Excel Chuẩn F1 100% (Times New Roman, Công trình, Hao phí VT, Vật liệu, Nhân công, CCDC, Máy thi công, THDT)"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-amber-200" />
            <span>Xuất Excel Chuẩn F1 (100%)</span>
          </a>

          <a
            href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
            download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold shadow-md shadow-blue-600/30 transition active:scale-95 flex items-center space-x-1.5"
            title="Tải tệp Excel 6 Sheet chuẩn thay thế phần mềm F1 (XLOOKUP, khử trùng lặp M>=1)"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
            <span>Excel 6 Sheet</span>
          </a>

          <a
            href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
            download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow-md shadow-emerald-600/30 transition active:scale-95 flex items-center space-x-1.5"
            title="Xuất trọn vẹn tệp Excel 10 Sheet động khép kín công thức"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
            <span>Excel 10 Sheet</span>
          </a>"""

content = content.replace(target1.replace("\n", "\r\n"), replacement1.replace("\n", "\r\n"))
content = content.replace(target1, replacement1)

# 2. Bottom card replacement
target2 = """            <div className="pt-2">
              <a
                href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
                download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-600/30 flex items-center justify-center space-x-1.5 transition active:scale-95"
              >
                <FileSpreadsheet className="w-4 h-4" />
                <span>Tải Ngay Tệp Excel 10 Sheet (.XLSX)</span>
              </a>
            </div>"""

replacement2 = """            <div className="pt-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
              <a
                href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
                download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
                className="py-2 px-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-[11px] font-bold shadow-md shadow-amber-600/30 flex items-center justify-center space-x-1 transition active:scale-95 text-center"
                title="Chuẩn F1 100%: Times New Roman, Công trình, Hao phí VT, CCDC, Máy, THDT"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-amber-200" />
                <span>Tải Excel Chuẩn F1 (100%)</span>
              </a>
              <a
                href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
                download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
                className="py-2 px-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-[11px] font-bold shadow-md shadow-blue-600/30 flex items-center justify-center space-x-1 transition active:scale-95 text-center"
                title="Bản 6 Sheet (XLOOKUP & Khử trùng lặp M)"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
                <span>Tải Excel 6 Sheet</span>
              </a>
              <a
                href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
                download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
                className="py-2 px-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-[11px] font-bold shadow-md shadow-emerald-600/30 flex items-center justify-center space-x-1 transition active:scale-95 text-center"
                title="Bản 10 Sheet chi tiết 10 Tab"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
                <span>Tải Excel 10 Sheet</span>
              </a>
            </div>"""

content = content.replace(target2.replace("\n", "\r\n"), replacement2.replace("\n", "\r\n"))
content = content.replace(target2, replacement2)

with open(tab10_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Tab10_TongHopKinhPhi.tsx with 3 Excel buttons successfully!")
