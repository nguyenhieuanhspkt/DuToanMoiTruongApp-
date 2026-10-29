import React, { useState, useEffect, useMemo, useCallback } from 'react';
import * as XLSX from 'xlsx';
import { 
  Download, Search, RefreshCw, ChevronLeft, ChevronRight, 
  ChevronsLeft, ChevronsRight, FileSpreadsheet, Loader2, Info
} from 'lucide-react';

interface ExcelSpreadsheetViewProps {
  items?: any[];
  onRefresh?: () => void;
}

interface CellData {
  coord: string;
  r: number;
  c: number;
  rawVal: any;
  dispVal: string;
  formula?: string;
  isNumeric: boolean;
  isBold?: boolean;
  colSpan?: number;
  rowSpan?: number;
  isHidden?: boolean;
}

export const ExcelSpreadsheetView: React.FC<ExcelSpreadsheetViewProps> = () => {
  const [workbook, setWorkbook] = useState<XLSX.WorkBook | null>(null);
  const [activeSheetName, setActiveSheetName] = useState<string>('Công trình');
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Selected cell for Formula Bar
  const [selectedCell, setSelectedCell] = useState<{ coord: string; value: string; formula: string }>({
    coord: 'A1',
    value: '',
    formula: ''
  });

  // Search & Pagination
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(100);

  // Load workbook from public folder
  const loadWorkbook = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const response = await fetch('/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx?t=' + Date.now());
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Không thể tải file Excel từ server`);
      }
      const arrayBuffer = await response.arrayBuffer();
      const wb = XLSX.read(arrayBuffer, { 
        type: 'array', 
        cellFormula: true, 
        cellStyles: true,
        sheetStubs: true 
      });
      setWorkbook(wb);
      if (wb.SheetNames && wb.SheetNames.length > 0) {
        if (!wb.SheetNames.includes(activeSheetName)) {
          setActiveSheetName(wb.SheetNames.includes('Công trình') ? 'Công trình' : wb.SheetNames[0]);
        }
      }
    } catch (err: any) {
      console.error('Error reading excel workbook:', err);
      setLoadError(err?.message || 'Lỗi khi đọc file Excel');
    } finally {
      setLoading(false);
    }
  }, [activeSheetName]);

  useEffect(() => {
    loadWorkbook();
  }, [loadWorkbook]);

  // Reset page when sheet or search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [activeSheetName, searchTerm, pageSize]);

  // Parse active worksheet into grid matrix
  const { gridRows, maxCol, colLetters, totalRows } = useMemo(() => {
    if (!workbook || !activeSheetName || !workbook.Sheets[activeSheetName]) {
      return { gridRows: [], maxCol: 0, colLetters: [], totalRows: 0 };
    }

    const ws = workbook.Sheets[activeSheetName];
    if (!ws['!ref']) {
      return { gridRows: [], maxCol: 0, colLetters: [], totalRows: 0 };
    }

    const range = XLSX.utils.decode_range(ws['!ref']);
    const numRows = range.e.r + 1;
    const numCols = Math.min(range.e.c + 1, 26); // Support up to Z columns comfortably

    // Build merges lookup map
    const mergesMap = new Map<string, { colSpan: number; rowSpan: number }>();
    const hiddenCells = new Set<string>();

    if (ws['!merges']) {
      ws['!merges'].forEach(m => {
        const startCoord = XLSX.utils.encode_cell({ r: m.s.r, c: m.s.c });
        const colSpan = m.e.c - m.s.c + 1;
        const rowSpan = m.e.r - m.s.r + 1;
        mergesMap.set(startCoord, { colSpan, rowSpan });

        for (let r = m.s.r; r <= m.e.r; r++) {
          for (let c = m.s.c; c <= m.e.c; c++) {
            if (r !== m.s.r || c !== m.s.c) {
              hiddenCells.add(XLSX.utils.encode_cell({ r, c }));
            }
          }
        }
      });
    }

    // Build column letters (A, B, C...)
    const colLetters: string[] = [];
    for (let c = 0; c < numCols; c++) {
      colLetters.push(XLSX.utils.encode_col(c));
    }

    // Extract all rows
    const allRows: CellData[][] = [];
    for (let r = 0; r < numRows; r++) {
      const rowCells: CellData[] = [];
      for (let c = 0; c < numCols; c++) {
        const coord = XLSX.utils.encode_cell({ r, c });
        const cell = ws[coord];
        
        const isHidden = hiddenCells.has(coord);
        const mergeInfo = mergesMap.get(coord);

        let dispVal = '';
        let formula = cell?.f ? `=${cell.f}` : '';
        let isNumeric = false;
        let rawVal = cell?.v;

        if (cell) {
          if (cell.w !== undefined && cell.w !== null && cell.w !== '') {
            dispVal = String(cell.w);
          } else if (cell.v !== undefined && cell.v !== null) {
            dispVal = String(cell.v);
          } else if (cell.f) {
            dispVal = `=${cell.f}`;
          }

          if (cell.t === 'n' || typeof cell.v === 'number') {
            isNumeric = true;
          }
        }

        rowCells.push({
          coord,
          r,
          c,
          rawVal,
          dispVal,
          formula,
          isNumeric,
          colSpan: mergeInfo?.colSpan,
          rowSpan: mergeInfo?.rowSpan,
          isHidden
        });
      }
      allRows.push(rowCells);
    }

    return { gridRows: allRows, maxCol: numCols, colLetters, totalRows: numRows };
  }, [workbook, activeSheetName]);

  // Set initial selected cell when sheet changes
  useEffect(() => {
    if (gridRows.length > 0 && gridRows[0].length > 0) {
      const firstCell = gridRows[0][0];
      setSelectedCell({
        coord: firstCell.coord,
        value: firstCell.dispVal,
        formula: firstCell.formula || (firstCell.dispVal ? `="${firstCell.dispVal}"` : '')
      });
    }
  }, [gridRows]);

  // Filter rows by searchTerm
  const filteredRows = useMemo(() => {
    if (!searchTerm.trim()) {
      return gridRows;
    }
    const term = searchTerm.toLowerCase();
    // Keep header rows (0 to 5) always visible for context, filter subsequent data rows
    return gridRows.filter((row, idx) => {
      if (idx < 5) return true;
      return row.some(cell => cell.dispVal.toLowerCase().includes(term));
    });
  }, [gridRows, searchTerm]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;
  const paginatedRows = useMemo(() => {
    if (pageSize >= 10000 || filteredRows.length <= pageSize) {
      return filteredRows;
    }
    // Always include top 5 header rows if not on page 1, or just slice directly
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  // Handle cell click
  const handleCellSelect = (cell: CellData) => {
    setSelectedCell({
      coord: cell.coord,
      value: cell.dispVal,
      formula: cell.formula || (cell.dispVal ? `="${cell.dispVal}"` : '')
    });
  };

  // Sheet Tabs styling helper
  const getSheetColor = (name: string) => {
    if (name.includes('Khoản 4.5')) return '#d97706'; // Amber for Khoan 4.5
    if (name.includes('THDT')) return '#dc2626'; // Red for Summary Macro
    if (name.includes('Đơn giá')) return '#2563eb'; // Blue for Unit Price
    return '#107c41'; // Standard Excel Green
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7.25rem)] bg-[#F3F3F3] border border-[#CBD5E1] rounded shadow-sm select-none font-['Times_New_Roman',serif]">
      {/* 1. TOP TOOLBAR: Search, Pagination, Download, Refresh */}
      <div className="h-10 bg-[#F8F9FA] border-b border-[#D4D4D8] px-3 flex items-center justify-between text-xs text-slate-700">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 font-sans font-semibold text-emerald-800">
            <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
            <span>Excel F1 Viewer (Read-only)</span>
          </div>

          <span className="text-slate-300">|</span>

          {/* Quick Search */}
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2" />
            <input
              type="text"
              placeholder={`Tìm kiếm trong [${activeSheetName}]...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-7 pr-3 py-1 bg-white border border-[#CBD5E1] rounded text-xs w-64 focus:outline-none focus:ring-1 focus:ring-emerald-600 focus:border-emerald-600 font-sans"
            />
            {searchTerm && (
              <button 
                onClick={() => setSearchTerm('')} 
                className="absolute right-2 text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            )}
          </div>

          {searchTerm && (
            <span className="text-[11px] font-sans text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Khớp: {filteredRows.length - 5} dòng
            </span>
          )}
        </div>

        {/* Right side: Page Navigation + Download */}
        <div className="flex items-center space-x-3 font-sans">
          {/* Pagination controls for large sheets */}
          {filteredRows.length > 100 && (
            <div className="flex items-center space-x-1 bg-white border border-[#CBD5E1] rounded px-1.5 py-0.5 text-xs">
              <span className="text-slate-500 mr-1">
                Dòng {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, filteredRows.length)} / {filteredRows.length.toLocaleString()}
              </span>

              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(1)}
                className="p-1 hover:bg-slate-100 disabled:opacity-30 rounded"
                title="Trang đầu"
              >
                <ChevronsLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                className="p-1 hover:bg-slate-100 disabled:opacity-30 rounded"
                title="Trang trước"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              
              <span className="px-1.5 font-bold text-slate-700">
                {currentPage} / {totalPages}
              </span>

              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                className="p-1 hover:bg-slate-100 disabled:opacity-30 rounded"
                title="Trang sau"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(totalPages)}
                className="p-1 hover:bg-slate-100 disabled:opacity-30 rounded"
                title="Trang cuối"
              >
                <ChevronsRight className="w-3.5 h-3.5" />
              </button>

              <select
                value={pageSize}
                onChange={(e) => setPageSize(Number(e.target.value))}
                className="ml-1 text-[11px] border-l border-slate-200 pl-1 py-0.5 bg-transparent focus:outline-none"
              >
                <option value={50}>50 dòng/trang</option>
                <option value={100}>100 dòng/trang</option>
                <option value={250}>250 dòng/trang</option>
                <option value={500}>500 dòng/trang</option>
                <option value={20000}>Tất cả ({filteredRows.length})</option>
              </select>
            </div>
          )}

          {/* Refresh Button */}
          <button
            onClick={loadWorkbook}
            disabled={loading}
            title="Tải lại file từ máy chủ"
            className="flex items-center space-x-1 px-2 py-1 bg-white hover:bg-slate-50 border border-[#CBD5E1] rounded text-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-600' : ''}`} />
            <span>Làm mới</span>
          </button>

          {/* Download Original XLSX */}
          <a
            href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
            download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
            className="flex items-center space-x-1 px-2.5 py-1 bg-emerald-700 hover:bg-emerald-800 text-white rounded font-medium shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Tải Excel gốc (.xlsx)</span>
          </a>
        </div>
      </div>

      {/* 2. EXCEL FORMULA BAR (Thanh công thức fx) */}
      <div className="h-8 bg-white border-b border-[#D4D4D8] flex items-center px-2 space-x-2 text-xs text-slate-800">
        {/* Name Box (Tọa độ ô: A1, B8, D7...) */}
        <div className="w-16 h-6 px-1.5 bg-[#F8F9FA] border border-[#CBD5E1] rounded flex items-center justify-center font-mono font-bold text-slate-700 shadow-inner">
          {selectedCell.coord}
        </div>

        {/* Function Button Icons */}
        <div className="flex items-center space-x-1 text-slate-400 border-r border-[#CBD5E1] pr-2">
          <span className="font-serif italic font-bold text-slate-600 px-1 select-none">fx</span>
        </div>

        {/* Formula Input Box (Chỉ đọc) */}
        <div className="flex-1 h-6 px-2 bg-[#FAFAFA] border border-[#E2E8F0] rounded flex items-center font-mono text-slate-800 text-[12px] overflow-x-auto whitespace-nowrap">
          {selectedCell.formula || selectedCell.value}
        </div>
      </div>

      {/* 3. MAIN SPREADSHEET GRID */}
      <div className="flex-1 overflow-auto bg-white relative">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 font-sans space-y-2">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
            <p className="text-sm font-medium">Đang đọc dữ liệu từ file Excel (13.399 dòng định mức)...</p>
          </div>
        ) : loadError ? (
          <div className="flex flex-col items-center justify-center h-full text-red-600 font-sans p-6">
            <Info className="w-10 h-10 mb-2" />
            <p className="font-bold text-base">Không thể tải file Excel</p>
            <p className="text-sm text-slate-600 mt-1">{loadError}</p>
            <button
              onClick={loadWorkbook}
              className="mt-4 px-4 py-1.5 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700"
            >
              Thử lại
            </button>
          </div>
        ) : (
          <table className="border-collapse text-[13px] text-slate-900 border border-[#D4D4D8] min-w-full">
            {/* Table Header: Column Letters (A, B, C...) with Freeze Panes */}
            <thead className="sticky top-0 z-20 bg-[#EFEFF2] shadow-sm">
              <tr className="border-b border-[#D4D4D8] text-slate-600 text-center text-[11px] font-sans font-semibold">
                {/* Row Header column top-left corner */}
                <th className="w-12 py-1 px-1 bg-[#E1E2E5] border-r border-[#CBD5E1] sticky left-0 z-30 font-mono text-slate-500">
                  #
                </th>
                {colLetters.map((letter) => (
                  <th
                    key={letter}
                    className="py-1 px-2 border-r border-[#CBD5E1] bg-[#EFEFF2] min-w-[70px] text-center"
                  >
                    {letter}
                  </th>
                ))}
              </tr>
            </thead>

            {/* Table Body: Rows and Cells */}
            <tbody>
              {paginatedRows.map((rowCells) => {
                const rowNum = (rowCells[0]?.r || 0) + 1;
                const isSelectedRow = rowCells.some(c => c.coord === selectedCell.coord);

                return (
                  <tr 
                    key={`row-${rowNum}`} 
                    className={`border-b border-[#E2E8F0] hover:bg-[#F4F9F4] transition-colors ${
                      isSelectedRow ? 'bg-[#EBF7EE]' : ''
                    }`}
                  >
                    {/* Row Index Column (1, 2, 3...) - Sticky on left */}
                    <td className="sticky left-0 z-10 bg-[#EFEFF2] border-r border-[#CBD5E1] text-center text-[11px] text-slate-500 font-mono py-1 px-1 select-none font-semibold">
                      {rowNum}
                    </td>

                    {/* Data Cells */}
                    {rowCells.map((cell) => {
                      if (cell.isHidden) return null;

                      const isSelected = selectedCell.coord === cell.coord;
                      const hasFormula = Boolean(cell.formula);

                      // Alignment heuristics
                      let alignClass = 'text-left';
                      if (cell.isNumeric) {
                        alignClass = 'text-right font-mono';
                      } else if (cell.dispVal.length <= 6 || /^[A-Z0-9_\-\.]+$/i.test(cell.dispVal)) {
                        alignClass = 'text-center font-mono';
                      }

                      // Header / Section Row Highlighting
                      const isBoldRow = rowNum <= 6 || cell.dispVal.startsWith('I.') || cell.dispVal.startsWith('II.') || cell.dispVal.startsWith('BẢNG');

                      return (
                        <td
                          key={cell.coord}
                          colSpan={cell.colSpan}
                          rowSpan={cell.rowSpan}
                          onClick={() => handleCellSelect(cell)}
                          title={`${cell.coord}: ${cell.formula ? cell.formula + ' => ' : ''}${cell.dispVal}`}
                          className={`px-2 py-1 border-r border-[#E2E8F0] cursor-pointer whitespace-nowrap overflow-hidden text-ellipsis max-w-md ${alignClass} ${
                            isSelected 
                              ? 'ring-2 ring-emerald-600 bg-emerald-50 z-10' 
                              : ''
                          } ${isBoldRow ? 'font-bold bg-[#FBFBFC]' : ''} ${
                            hasFormula ? 'relative' : ''
                          }`}
                        >
                          {cell.dispVal}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* 4. BOTTOM STATUS & SHEET TABS BAR */}
      <div className="h-9 bg-[#EFEFF2] border-t border-[#D4D4D8] flex items-center justify-between px-2 text-xs">
        {/* Left: Sheet Tabs Carousel */}
        <div className="flex items-center space-x-1 overflow-x-auto py-1 scrollbar-thin">
          {workbook?.SheetNames.map((sheetName) => {
            const isActive = sheetName === activeSheetName;
            const tabColor = getSheetColor(sheetName);

            return (
              <button
                key={sheetName}
                onClick={() => {
                  setActiveSheetName(sheetName);
                  setSearchTerm('');
                }}
                className={`px-3 py-1 text-xs font-sans font-medium rounded-t border transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                  isActive
                    ? 'bg-white text-slate-900 border-[#CBD5E1] border-b-white shadow-sm font-semibold'
                    : 'bg-[#E5E6E8] text-slate-600 border-transparent hover:bg-[#DADBDE]'
                }`}
                style={{
                  borderTop: isActive ? `3px solid ${tabColor}` : undefined
                }}
              >
                <span 
                  className="w-2 h-2 rounded-full inline-block"
                  style={{ backgroundColor: tabColor }}
                />
                <span>{sheetName}</span>
                {sheetName === 'Hao phí VT' && (
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1 py-0.2 rounded font-mono">
                    13.399 dòng
                  </span>
                )}
                {sheetName.includes('Khoản 4.5') && (
                  <span className="text-[10px] bg-amber-100 text-amber-800 px-1 py-0.2 rounded font-mono">
                    Mục 2.1.2
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Right: Info Status */}
        <div className="hidden md:flex items-center space-x-3 font-sans text-[11px] text-slate-500 pl-2">
          <span>Sheet: <strong className="text-slate-800">{activeSheetName}</strong></span>
          <span>•</span>
          <span>Dòng: <strong className="text-slate-800">{totalRows.toLocaleString()}</strong></span>
          <span>•</span>
          <span>Cột: <strong className="text-slate-800">{maxCol}</strong></span>
          <span>•</span>
          <span className="text-emerald-700 font-semibold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
            F1 Replica 100%
          </span>
        </div>
      </div>
    </div>
  );
};
