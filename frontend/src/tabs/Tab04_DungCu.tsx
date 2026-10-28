import React, { useState, useMemo } from 'react';
import { Eye, Wrench, Layers, Search, AlertCircle } from 'lucide-react';
import type { PaktItem, ToolNormDetail } from '../types';

interface Tab04DungCuProps {
  items: PaktItem[];
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab04_DungCu: React.FC<Tab04DungCuProps> = ({ items, onSelectDrawerItem }) => {
  const [viewMode, setViewMode] = useState<'by_item' | 'summary'>('by_item');
  const [toolSearch, setToolSearch] = useState<string>('');

  // 1. Trích xuất chi tiết dụng cụ theo từng dòng công việc
  const itemsWithTools = useMemo(() => {
    return items.map((row) => {
      const N = row.so_luong_mau || 1;
      const tt = row.tt20_data;
      const tools: ToolNormDetail[] = [];

      if (tt) {
        for (const [stageKey, stageLabel] of [
          ['field', 'Ngoại nghiệp'],
          ['lab', 'Nội nghiệp'],
          ['single', 'Toàn phần'],
        ] as const) {
          const sub = tt[stageKey];
          if (sub && sub.tools) {
            for (const t of sub.tools) {
              const rawName = String(t.name || '').trim();
              const rawUnit = String(t.unit || '').trim();
              const rawLifespan = t.lifespan_months;
              const rawNorm = t.norm;

              let toolName = rawName;
              let toolUnit = rawUnit;
              let lifespanMonths = 12.0;

              if (/^\d+$/.test(rawName)) {
                toolName = rawUnit;
                toolUnit = String(rawLifespan).trim();
                lifespanMonths = Number(rawNorm || 12) || 12;
              } else {
                lifespanMonths = Number(rawLifespan || 12) || 12;
              }

              if (lifespanMonths <= 0) lifespanMonths = 12.0;

              const standardShifts = lifespanMonths * 22.0;
              const normShiftPerSample = Number(((1.0 / standardShifts) * 1.10).toFixed(6));

              tools.push({
                stage: stageLabel,
                name: toolName,
                unit: toolUnit,
                lifespan_months: lifespanMonths,
                standard_shifts: standardShifts,
                minor_tool_factor: 1.10,
                norm_shift_per_sample: normShiftPerSample,
                total_shifts: Number((normShiftPerSample * N).toFixed(4)),
              });
            }
          }
        }
      }

      return {
        ...row,
        tools,
        totalToolsCount: tools.length,
      };
    });
  }, [items]);

  // 2. Tổng hợp danh mục dụng cụ toàn gói thầu
  const toolSummary = useMemo(() => {
    const summaryMap: Record<string, { name: string; unit: string; total_shifts: number; count: number; avg_lifespan: number }> = {};

    for (const row of itemsWithTools) {
      for (const t of row.tools) {
        if (!t.name) continue;
        const key = `${t.name}___${t.unit}`;
        if (!summaryMap[key]) {
          summaryMap[key] = {
            name: t.name,
            unit: t.unit,
            total_shifts: 0,
            count: 0,
            avg_lifespan: t.lifespan_months,
          };
        }
        summaryMap[key].total_shifts += t.total_shifts;
        summaryMap[key].count += 1;
      }
    }

    const list = Object.values(summaryMap).map((t) => ({
      ...t,
      total_shifts: Number(t.total_shifts.toFixed(4)),
    }));

    return list.sort((a, b) => a.name.localeCompare(b.name));
  }, [itemsWithTools]);

  const filteredToolSummary = useMemo(() => {
    if (!toolSearch.trim()) return toolSummary;
    const q = toolSearch.toLowerCase();
    return toolSummary.filter((t) => t.name.toLowerCase().includes(q) || t.unit.toLowerCase().includes(q));
  }, [toolSummary, toolSearch]);

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950">
      {/* Sub-header Controls */}
      <div className="h-10 px-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('by_item')}
            className={`px-3 py-1.5 rounded font-medium flex items-center space-x-1.5 transition ${
              viewMode === 'by_item'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Theo dòng công việc (253 dòng)</span>
          </button>
          <button
            onClick={() => setViewMode('summary')}
            className={`px-3 py-1.5 rounded font-medium flex items-center space-x-1.5 transition ${
              viewMode === 'summary'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Wrench className="w-3.5 h-3.5" />
            <span>Tổng hợp danh mục dụng cụ ({toolSummary.length} dụng cụ)</span>
          </button>
        </div>

        <div className="flex items-center space-x-3 text-slate-400">
          <div className="flex items-center space-x-1 text-[11px] bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <AlertCircle className="w-3.5 h-3.5 text-blue-400" />
            <span>Khoản 4.2 TT20: Chuẩn <strong>22 ca/tháng</strong>, cộng <strong>+10%</strong> dụng cụ phụ</span>
          </div>
          {viewMode === 'summary' && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Tìm tên dụng cụ..."
                value={toolSearch}
                onChange={(e) => setToolSearch(e.target.value)}
                className="pl-8 pr-2.5 py-1 rounded bg-slate-950 border border-slate-700 text-slate-200 text-xs w-48 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>
      </div>

      {/* Main Table Area */}
      <div className="flex-1 overflow-auto">
        {viewMode === 'by_item' ? (
          /* CHẾ ĐỘ 1: THEO DÒNG CÔNG VIỆC */
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-700 text-slate-300 font-bold z-10 shadow-sm">
              <tr>
                <th className="py-2 px-2.5 w-10 text-center">STT</th>
                <th className="py-2 px-2.5 w-24">Nhóm</th>
                <th className="py-2 px-2.5 min-w-[130px]">Nhà máy</th>
                <th className="py-2 px-2.5 min-w-[140px]">Thông số quan trắc</th>
                <th className="py-2 px-2 w-16 text-right tabular-nums">Mẫu (N)</th>
                <th className="py-2 px-3 min-w-[320px] bg-amber-950/20 text-amber-300">
                  Dụng cụ lấy mẫu, bình chứa & Đồ bảo hộ lao động (+10% phụ)
                </th>
                <th className="py-2 px-2.5 w-24 text-center">Số loại dụng cụ</th>
                <th className="py-2 px-2 w-12 text-center">Soi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {itemsWithTools.map((row) => (
                <tr key={row.id} className="hover:bg-slate-900/60 transition group">
                  <td className="py-2 px-2.5 text-center text-slate-500 font-mono">{row.id}</td>
                  <td className="py-2 px-2.5">
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {row.nhom.includes('Định kỳ') ? 'Định kỳ' : 'Đối chứng'}
                    </span>
                  </td>
                  <td className="py-2 px-2.5 text-slate-300 truncate max-w-[130px]" title={row.khu_vuc}>
                    {row.khu_vuc.replace('Nhà máy Nhiệt điện ', 'NMNĐ ')}
                  </td>
                  <td className="py-2 px-2.5 font-semibold text-white truncate max-w-[160px]" title={row.thong_so}>
                    {row.thong_so}
                  </td>
                  <td className="py-2 px-2 text-right font-bold text-slate-200 tabular-nums font-mono">
                    {row.so_luong_mau}
                  </td>
                  <td className="py-2 px-3 bg-amber-950/5">
                    {row.tools.length === 0 ? (
                      <span className="text-slate-600 italic">Không có dụng cụ hao phí riêng</span>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {row.tools.slice(0, 3).map((t, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] bg-slate-900 text-slate-200 border border-slate-800"
                            title={`${t.name} (${t.lifespan_months} tháng = ${t.standard_shifts} ca) -> Khấu hao ${t.total_shifts} ca`}
                          >
                            <span className="text-amber-400 font-medium truncate max-w-[130px]">{t.name}</span>
                            <span className="text-slate-500 font-mono">({t.lifespan_months}th)</span>
                          </span>
                        ))}
                        {row.tools.length > 3 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{row.tools.length - 3} dụng cụ khác...
                          </span>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="py-2 px-2.5 text-center font-mono font-bold text-slate-300">
                    {row.totalToolsCount > 0 ? (
                      <span className="text-amber-400">{row.totalToolsCount}</span>
                    ) : (
                      <span className="text-slate-600">0</span>
                    )}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <button
                      onClick={() => onSelectDrawerItem(row)}
                      className="p-1 rounded text-xs bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-blue-300 transition"
                      title="Soi sâu định mức dụng cụ"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          /* CHẾ ĐỘ 2: TỔNG HỢP DANH MỤC DỤNG CỤ GÓI THẦU */
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-700 text-slate-300 font-bold z-10 shadow-sm">
              <tr>
                <th className="py-2.5 px-3 w-12 text-center">STT</th>
                <th className="py-2.5 px-4 min-w-[280px]">Tên công cụ, dụng cụ & đồ BHLĐ</th>
                <th className="py-2.5 px-3 w-28 text-center">Đơn vị tính</th>
                <th className="py-2.5 px-4 w-32 text-center">Niên hạn trung bình</th>
                <th className="py-2.5 px-4 w-40 text-right tabular-nums bg-amber-950/20 text-amber-300 font-black">
                  Tổng ca khấu hao (+10%)
                </th>
                <th className="py-2.5 px-4 w-40 text-center">Số thông số sử dụng</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
              {filteredToolSummary.map((tool, idx) => (
                <tr key={idx} className="hover:bg-slate-900/60 transition">
                  <td className="py-2 px-3 text-center text-slate-500">{idx + 1}</td>
                  <td className="py-2 px-4 font-sans font-semibold text-white">{tool.name}</td>
                  <td className="py-2 px-3 text-center text-slate-400 font-sans">{tool.unit}</td>
                  <td className="py-2 px-4 text-center font-sans text-slate-300">
                    {tool.avg_lifespan} tháng ({tool.avg_lifespan * 22} ca)
                  </td>
                  <td className="py-2 px-4 text-right font-black text-amber-300 bg-amber-950/10">
                    {tool.total_shifts.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 4 })} ca
                  </td>
                  <td className="py-2 px-4 text-center font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-blue-300 border border-slate-700 font-semibold">
                      {tool.count} thông số
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
