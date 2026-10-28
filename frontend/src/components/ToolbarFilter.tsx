import { forwardRef } from 'react';
import { Search, X } from 'lucide-react';
import type { FilterState } from '../types';

interface ToolbarFilterProps {
  filters: FilterState;
  onFilterChange: (newFilters: FilterState) => void;
  onClearFilters: () => void;
}

export const ToolbarFilter = forwardRef<HTMLInputElement, ToolbarFilterProps>(({
  filters,
  onFilterChange,
  onClearFilters
}, ref) => {
  const hasActiveFilters = Boolean(
    filters.search ||
    filters.program !== 'all' ||
    filters.plant !== 'all' ||
    filters.environment !== 'all'
  );

  return (
    <div className="p-3 bg-slate-900 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2.5">
      {/* Search Input with Shortcut Icon */}
      <div className="relative flex-1 min-w-[260px] max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          ref={ref}
          type="text"
          value={filters.search}
          onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
          placeholder="Tìm theo tên thông số, mã gộp, vị trí... (Ctrl+F)"
          className="w-full bg-slate-800 border border-slate-700/80 rounded-lg pl-9 pr-8 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition shadow-inner"
        />
        {filters.search && (
          <button
            onClick={() => onFilterChange({ ...filters, search: '' })}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Multi-level Dropdowns */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {/* Program Filter */}
        <select
          value={filters.program}
          onChange={(e) => onFilterChange({ ...filters, program: e.target.value })}
          className="bg-slate-800 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 font-medium"
        >
          <option value="all">Tất cả Chương trình</option>
          <option value="Định kỳ">1. Định kỳ theo Giấy phép MT</option>
          <option value="đối chứng">2. Đối chứng Tổ giám sát</option>
        </select>

        {/* Plant Filter */}
        <select
          value={filters.plant}
          onChange={(e) => onFilterChange({ ...filters, plant: e.target.value })}
          className="bg-slate-800 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 font-medium"
        >
          <option value="all">Tất cả Nhà máy</option>
          <option value="Vĩnh Tân 4 mở rộng">NMNĐ Vĩnh Tân 4 Mở rộng</option>
          <option value="Vĩnh Tân 4">NMNĐ Vĩnh Tân 4 (Gốc)</option>
        </select>

        {/* Environment Filter */}
        <select
          value={filters.environment}
          onChange={(e) => onFilterChange({ ...filters, environment: e.target.value })}
          className="bg-slate-800 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 font-medium"
        >
          <option value="all">Tất cả Môi trường</option>
          <option value="không khí">Không khí xung quanh</option>
          <option value="khí thải">Khí thải ống khói</option>
          <option value="nước thải">Nước thải công nghiệp</option>
          <option value="nước biển">Nước biển ven bờ</option>
          <option value="bùn">Bùn thải</option>
          <option value="sinh thái">Hệ sinh thái thủy sinh</option>
        </select>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="flex items-center space-x-1 px-2.5 py-1.5 bg-red-950/40 text-red-300 border border-red-700/50 rounded-lg hover:bg-red-900/60 transition active:scale-95 font-medium"
            title="Xóa toàn bộ bộ lọc"
          >
            <X className="w-3.5 h-3.5" />
            <span>Xóa lọc</span>
          </button>
        )}
      </div>
    </div>
  );
});
