import React from 'react';
import { RefreshCw, Maximize2, ShieldCheck } from 'lucide-react';

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
              v0.1.0 Baseline
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
        <span>Căn cứ: <strong>Thông tư 20/2017/TT-BTNMT</strong> & <strong>Văn bản 3072/EVN-MTPTBV</strong></span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2.5">
        {/* OneDrive Sync Badge */}
        <div className="flex items-center space-x-1.5 bg-emerald-950/40 border border-emerald-600/30 text-emerald-300 px-2.5 py-1 rounded-md text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="hidden sm:inline font-medium">OneDrive Synced</span>
        </div>

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
