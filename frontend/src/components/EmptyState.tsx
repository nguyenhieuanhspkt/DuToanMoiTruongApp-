import React from 'react';
import { SearchX, RotateCcw } from 'lucide-react';

interface EmptyStateProps {
  searchQuery?: string;
  onClearFilters: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ searchQuery, onClearFilters }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center h-full min-h-[350px]">
      <div className="w-14 h-14 rounded-full bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 mb-4 shadow-inner">
        <SearchX className="w-7 h-7 text-slate-500" />
      </div>
      <h3 className="text-sm font-bold text-slate-200 mb-1">
        Không tìm thấy thông số phù hợp
      </h3>
      <p className="text-xs text-slate-400 max-w-md mb-5 leading-relaxed">
        {searchQuery ? (
          <>
            Không có kết quả nào khớp với từ khóa <strong className="text-blue-300 font-mono">"{searchQuery}"</strong> trong bộ lọc hiện tại.
          </>
        ) : (
          'Không có mục công việc nào thỏa mãn tiêu chí lọc đã chọn.'
        )}
      </p>
      <button
        onClick={onClearFilters}
        className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-blue-600/30 transition active:scale-95"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        <span>Xóa bộ lọc & Xem toàn bộ</span>
      </button>
    </div>
  );
};
