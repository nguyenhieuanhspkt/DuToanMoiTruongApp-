import React from 'react';
import { Layers, FileSpreadsheet, Compass, FlaskConical, Clock } from 'lucide-react';

interface KPICardsProps {
  totalItems: number;
  totalSamples: number;
  totalFieldDays: number;
  totalLabDays: number;
}

export const KPICards: React.FC<KPICardsProps> = ({
  totalItems,
  totalSamples,
  totalFieldDays,
  totalLabDays
}) => {
  const grandTotalDays = totalFieldDays + totalLabDays;

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-2.5 p-3 bg-slate-900/60 border-b border-slate-800">
      {/* 1. Tổng công việc */}
      <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
        <div className="w-8 h-8 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
          <FileSpreadsheet className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-slate-400">Tổng Mục PAKT</div>
          <div className="text-base font-bold text-white tabular-nums">{totalItems} <span className="text-xs font-normal text-slate-400">mục</span></div>
        </div>
      </div>

      {/* 2. Tổng mẫu */}
      <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
        <div className="w-8 h-8 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
          <Layers className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-slate-400">Khối Lượng Mẫu</div>
          <div className="text-base font-bold text-white tabular-nums">{totalSamples.toLocaleString('vi-VN')} <span className="text-xs font-normal text-slate-400">mẫu</span></div>
        </div>
      </div>

      {/* 3. Công Ngoại nghiệp */}
      <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
        <div className="w-8 h-8 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
          <Compass className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-amber-400">Công Ngoại Nghiệp</div>
          <div className="text-base font-bold text-amber-300 tabular-nums">
            {totalFieldDays.toLocaleString('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-amber-200/60">công</span>
          </div>
        </div>
      </div>

      {/* 4. Công Nội nghiệp */}
      <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
        <div className="w-8 h-8 rounded-md bg-purple-500/20 text-purple-400 flex items-center justify-center shrink-0">
          <FlaskConical className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-purple-400">Công Nội Nghiệp (PTN)</div>
          <div className="text-base font-bold text-purple-300 tabular-nums">
            {totalLabDays.toLocaleString('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-purple-200/60">công</span>
          </div>
        </div>
      </div>

      {/* 5. Tổng Công Toàn Bộ */}
      <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/40 rounded-lg p-2.5 flex items-center space-x-2.5 col-span-2 md:col-span-1 shadow-sm">
        <div className="w-8 h-8 rounded-md bg-blue-500 text-white flex items-center justify-center shrink-0 shadow-md">
          <Clock className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-blue-200">Tổng Ngày Công TT20</div>
          <div className="text-base font-black text-white tabular-nums">
            {grandTotalDays.toLocaleString('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-blue-300">công</span>
          </div>
        </div>
      </div>
    </div>
  );
};
