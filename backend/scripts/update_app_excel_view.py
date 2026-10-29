import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

app_path = r'D:\TaskApp_kiet\DuToanMoiTruongApp\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add import for ExcelSpreadsheetView
if 'ExcelSpreadsheetView' not in text:
    target_import = "import { Tab10_TongHopKinhPhi } from './tabs/Tab10_TongHopKinhPhi';"
    replace_import = "import { Tab10_TongHopKinhPhi } from './tabs/Tab10_TongHopKinhPhi';\nimport { ExcelSpreadsheetView } from './components/ExcelSpreadsheetView';"
    text = text.replace(target_import, replace_import)

# 2. Add viewMode state
if 'viewMode' not in text:
    target_state = "const [activeTab, setActiveTab] = useState<number>(1);"
    replace_state = "const [activeTab, setActiveTab] = useState<number>(1);\n  const [viewMode, setViewMode] = useState<'excel' | 'dashboard'>('excel');"
    text = text.replace(target_state, replace_state)

# 3. Update HeaderNav props
target_header = '<HeaderNav onRefresh={loadData} isLoading={isLoading} />'
replace_header = '<HeaderNav onRefresh={loadData} isLoading={isLoading} viewMode={viewMode} onToggleViewMode={setViewMode} />'
text = text.replace(target_header, replace_header)

# 4. Wrap body with viewMode check
target_body_start = """      {/* 2. Middle Body: Sidebar + Main Content */}
      <div className="flex-1 flex overflow-hidden">"""

replace_body_start = """      {/* 2. Middle Body: Excel View vs Dashboard */}
      {viewMode === 'excel' ? (
        <div className="flex-1 overflow-hidden p-2 bg-[#2B579A]/15 flex flex-col">
          <ExcelSpreadsheetView items={items} />
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">"""

text = text.replace(target_body_start, replace_body_start)

# 5. Close the conditional before FooterNav or at end of body
target_body_end = """      {/* 3. Bottom Status Bar */}
      <FooterNav"""

replace_body_end = """        </div>
      )}

      {/* 3. Bottom Status Bar */}
      <FooterNav"""

text = text.replace(target_body_end, replace_body_end)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated App.tsx with ExcelSpreadsheetView and viewMode toggle successfully!")
