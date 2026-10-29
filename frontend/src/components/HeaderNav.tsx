import React from 'react';
import { RefreshCw, Maximize2, FileSpreadsheet, LayoutDashboard } from 'lucide-react';

interface HeaderNavProps {
  onRefresh: () => void;
  isLoading: boolean;
  viewMode: 'excel' | 'dashboard';
  onToggleViewMode: (mode: 'excel' | 'dashboard') => void;
}

export const HeaderNav: React.FC<HeaderNavProps> = ({ 
  onRefresh, 
  isLoading,
  viewMode,
  onToggleViewMode 
}) => {
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
        <div className="w-8 h-8 rounded-lg bg-[#107c41] flex items-center justify-center shadow-lg shadow-green-500/30 text-white font-black text-sm tracking-wider">
          XLS
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-sm font-bold text-white tracking-tight">
              DuToanMoiTruongApp • Chế độ Bảng tính Excel F1
            </h1>
            <span className="text-[10px] uppercase font-semibold bg-green-500/20 text-green-300 border border-green-400/30 px-1.5 py-0.5 rounded">
              Excel View
            </span>
          </div>
          <p className="text-[11px] text-blue-200/70 truncate max-w-md">
            Thẩm định Dự toán TT20 • NMNĐ Vĩnh Tân 4 • Chuẩn 100% F1 & Khoản 4.5 TT20
          </p>
        </div>
      </div>

      {/* Center: VIEW MODE TOGGLE (Chuyển chế độ Bảng tính Excel vs Dashboard) */}
      <div className="flex items-center bg-slate-950/80 p-1 rounded-lg border border-slate-700/80 shadow-inner">
        <button
          onClick={() => onToggleViewMode('excel')}
          className={`px-3 py-1 rounded text-xs font-bold flex items-center space-x-1.5 transition-all ${
            viewMode === 'excel'
              ? 'bg-[#107c41] text-white shadow-md shadow-green-900/40'
              : 'text-slate-300 hover:text-white hover:bg-slate-800'
          }`}
          title="Chế độ xem giao diện Bảng tính Excel 100% với fx, dòng, cột và sheet tabs"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
          <span>Giao diện Excel F1</span>
        </button>

        <button
          onClick={() => onToggleViewMode('dashboard')}
          className={`px-3 py-1 rounded text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            viewMode === 'dashboard'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-900/40'
              : 'text-slate-300 hover:text-white hover:bg-slate-800'
          }`}
          title="Chế độ Dashboard thẩm định phân tích chi tiết"
        >
          <LayoutDashboard className="w-3.5 h-3.5" />
          <span>Dashboard Thẩm định</span>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2.5">
        {/* Export Excel F1 Full Replica 100% Button */}
        <a
          href="/DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
          download="DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
          className="flex items-center space-x-1.5 bg-[#107c41] hover:bg-[#0b5c30] text-white px-3 py-1.5 rounded-md text-xs font-bold transition-all shadow-md shadow-green-900/40 border border-green-400/40"
          title="Tải về file Excel dự toán đầy đủ 100% định dạng phần mềm F1 (11 Sheet, Times New Roman, SUMIF động)"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-green-200" />
          <span>Tải Excel F1 chuẩn</span>
        </a>

        {/* Refresh Data Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-1.5 text-blue-200 hover:text-white bg-blue-900/40 hover:bg-blue-800/60 border border-blue-700/40 rounded-md transition-colors"
          title="Đồng bộ lại dữ liệu từ CSDL OneDrive"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>

        {/* Fullscreen Button */}
        <button
          onClick={toggleFullscreen}
          className="p-1.5 text-blue-200 hover:text-white bg-blue-900/40 hover:bg-blue-800/60 border border-blue-700/40 rounded-md transition-colors"
          title="Toàn màn hình"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
