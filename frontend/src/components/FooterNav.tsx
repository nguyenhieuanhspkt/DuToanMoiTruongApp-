import React from 'react';
import { ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight, Keyboard } from 'lucide-react';

interface FooterNavProps {
  totalItems: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

export const FooterNav: React.FC<FooterNavProps> = ({
  totalItems,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange
}) => {
  const totalPages = pageSize === -1 ? 1 : Math.max(1, Math.ceil(totalItems / pageSize));
  const startItem = totalItems === 0 ? 0 : pageSize === -1 ? 1 : (currentPage - 1) * pageSize + 1;
  const endItem = pageSize === -1 ? totalItems : Math.min(currentPage * pageSize, totalItems);

  return (
    <footer className="h-12 bg-slate-900 border-t border-slate-800 px-4 flex items-center justify-between select-none text-xs text-slate-400 z-20">
      {/* Left: Summary Count & Shortcuts */}
      <div className="flex items-center space-x-4">
        <div>
          Đang xem: <strong className="text-slate-200">{startItem} - {endItem}</strong> / <strong className="text-white">{totalItems}</strong> mục
        </div>
        <div className="hidden xl:flex items-center space-x-1.5 text-[11px] text-slate-500 bg-slate-800/60 px-2.5 py-0.5 rounded border border-slate-700/50">
          <Keyboard className="w-3.5 h-3.5 text-slate-400" />
          <span>Alt+1..0: Chuyển Tab • Ctrl+F: Tìm kiếm • Esc: Đóng</span>
        </div>
      </div>

      {/* Center: Smart Pagination Controls */}
      <div className="flex items-center space-x-1.5">
        <button
          onClick={() => onPageChange(1)}
          disabled={currentPage <= 1 || pageSize === -1}
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:pointer-events-none transition"
          title="Trang đầu"
        >
          <ChevronsLeft className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1 || pageSize === -1}
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:pointer-events-none transition"
          title="Trang trước"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="px-2 py-0.5 bg-slate-800/90 text-white font-mono text-xs rounded border border-slate-700">
          Trang <strong>{currentPage}</strong> / {totalPages}
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages || pageSize === -1}
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:pointer-events-none transition"
          title="Trang sau"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage >= totalPages || pageSize === -1}
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:pointer-events-none transition"
          title="Trang cuối"
        >
          <ChevronsRight className="w-4 h-4" />
        </button>
      </div>

      {/* Right: Page Size Selector */}
      <div className="flex items-center space-x-2">
        <span>Số dòng/trang:</span>
        <select
          value={pageSize}
          onChange={(e) => {
            onPageSizeChange(Number(e.target.value));
            onPageChange(1);
          }}
          className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1 outline-none focus:border-blue-500 font-medium"
        >
          <option value={15}>15 dòng</option>
          <option value={25}>25 dòng</option>
          <option value={50}>50 dòng</option>
          <option value={100}>100 dòng</option>
          <option value={-1}>Toàn bộ (253)</option>
        </select>
      </div>
    </footer>
  );
};
