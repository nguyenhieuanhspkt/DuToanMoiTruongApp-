import React from 'react';
import { RefreshCw, Maximize2, ShieldCheck, FileSpreadsheet } from 'lucide-react';

interface HeaderNavProps {
  onRefresh: () => void;
  isLoading: boolean;
}

export const HeaderNav: React.FC<HeaderNavProps> = ({ onRefresh, isLoading }) => {
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  return (
    <header className="h-14 bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 border-b border-blue-800/40 px-4 flex items-center justify-between select-none shadow-md z-30">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 text-white font-black text-sm tracking-wider">
          EVN
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-sm font-bold text-white tracking-tight">
              DuToanMoiTruongApp
            </h1>
            <span className="text-[10px] uppercase font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30 px-1.5 py-0.5 rounded">
              v1.0 Final
            </span>
          </div>
          <p className="text-[11px] text-blue-200/70 truncate max-w-md">
            Thẩm định Dự toán Quan trắc Môi trường 2026 • NMNĐ Vĩnh Tân 4 & VT4 Mở Rộng
          </p>
        </div>
      </div>

      {/* Center: Legal Bases */}
      <div className="hidden lg:flex items-center space-x-2 text-[11px] text-blue-200/80 bg-blue-900/30 border border-blue-700/40 px-3 py-1 rounded-full">
        <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
        <span>Căn cứ: <strong>TT 20/2017/TT-BTNMT</strong>, <strong>QĐ 80/2026/QĐ-UBND</strong> & <strong>VB 5691/EVN</strong></span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2.5">
        {/* OneDrive Sync Badge */}
        <div className="flex items-center space-x-1.5 bg-emerald-950/40 border border-emerald-600/30 text-emerald-300 px-2.5 py-1 rounded-md text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="hidden sm:inline font-medium">OneDrive Synced</span>
        </div>

        {/* Export Excel F1 Full Replica 100% Button */}
        <a
          href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
          download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
          title="Tải tệp Excel Dự toán Chuẩn 100% F1: Times New Roman, Công trình, Hao phí VT, Vật liệu, Nhân công, CCDC, Máy thi công, THDT"
          className="px-2.5 py-1 rounded-md bg-amber-600 hover:bg-amber-500 text-white border border-amber-500 text-xs font-bold transition active:scale-95 flex items-center space-x-1.5 shadow-md shadow-amber-600/30"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-amber-200" />
          <span className="hidden sm:inline">Excel Chuẩn F1 (100%)</span>
        </a>

        {/* Export Excel 6-Sheet F1 Replacement Button */}
        <a
          href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
          download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"
          title="Tải tệp Excel 6 Sheet chuẩn thay thế phần mềm F1 (XLOOKUP, khử trùng lặp M>=1)"
          className="px-2.5 py-1 rounded-md bg-blue-600 hover:bg-blue-500 text-white border border-blue-500 text-xs font-bold transition active:scale-95 flex items-center space-x-1.5 shadow-md shadow-blue-600/30"
        >
          <FileSpreadsheet className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Excel 6 Sheet</span>
        </a>

        {/* Export Excel 10-Sheet Button */}
        <a
          href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
          download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx"
          title="Tải tệp Excel 10 Sheet động khép kín công thức"
          className="px-2.5 py-1 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-500 text-xs font-bold transition active:scale-95 flex items-center space-x-1.5 shadow-md shadow-emerald-600/30"
        >
          <FileSpreadsheet className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Excel 10 Sheet</span>
        </a>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          title="Tải lại dữ liệu từ CSDL OneDrive"
          className="p-1.5 rounded-md text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-700/60 transition active:scale-95"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
        </button>

        {/* Fullscreen button */}
        <button
          onClick={toggleFullscreen}
          title="Toàn màn hình"
          className="p-1.5 rounded-md text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-700/60 transition active:scale-95"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
