import React, { useState, useMemo } from 'react';
import { Eye, Beaker, Layers, Search, AlertCircle } from 'lucide-react';
import type { PaktItem, MaterialNormDetail, MaterialSummaryItem } from '../types';

interface Tab03VatLieuProps {
  items: PaktItem[];
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab03_VatLieu: React.FC<Tab03VatLieuProps> = ({ items, onSelectDrawerItem }) => {
  const [viewMode, setViewMode] = useState<'by_item' | 'summary'>('by_item');
  const [chemSearch, setChemSearch] = useState<string>('');

  // 1. Trích xuất chi tiết vật liệu cho từng dòng công việc
  const itemsWithMaterials = useMemo(() => {
    return items.map((row) => {
      const N = row.so_luong_mau || 1;
      const tt = row.tt20_data;
      const mats: MaterialNormDetail[] = [];

      if (tt) {
        for (const [stageKey, stageLabel] of [
          ['field', 'Ngoại nghiệp'],
          ['lab', 'Nội nghiệp'],
          ['single', 'Toàn phần'],
        ] as const) {
          const sub = tt[stageKey];
          if (sub && sub.materials) {
            for (const m of sub.materials) {
              const normRaw = Number(m.norm || 0);
              const normWithWaste = Number((normRaw * 1.08).toFixed(6));
              mats.push({
                stage: stageLabel,
                name: String(m.name || '').trim(),
                unit: String(m.unit || '').trim(),
                norm_raw: normRaw,
                waste_factor: 1.08,
                norm_per_sample: normWithWaste,
                total_qty: Number((normWithWaste * N).toFixed(4)),
              });
            }
          }
        }
      }

      return {
        ...row,
        materials: mats,
        totalMaterialsCount: mats.length,
      };
    });
  }, [items]);

  // 2. Tổng hợp nhu cầu hóa chất toàn gói thầu
  const chemicalSummary = useMemo(() => {
    const summaryMap: Record<string, MaterialSummaryItem> = {};

    for (const row of itemsWithMaterials) {
      for (const m of row.materials) {
        if (!m.name) continue;
        const key = `${m.name}___${m.unit}`;
        if (!summaryMap[key]) {
          summaryMap[key] = {
            name: m.name,
            unit: m.unit,
            total_quantity: 0,
            used_by_parameters_count: 0,
          };
        }
        summaryMap[key].total_quantity += m.total_qty;
        summaryMap[key].used_by_parameters_count += 1;
      }
    }

    const list = Object.values(summaryMap).map((item) => ({
      ...item,
      total_quantity: Number(item.total_quantity.toFixed(4)),
    }));

    return list.sort((a, b) => a.name.localeCompare(b.name));
  }, [itemsWithMaterials]);

  // Bộ lọc hóa chất theo từ khóa
  const filteredSummary = useMemo(() => {
    if (!chemSearch.trim()) return chemicalSummary;
    const q = chemSearch.toLowerCase();
    return chemicalSummary.filter((c) => c.name.toLowerCase().includes(q) || c.unit.toLowerCase().includes(q));
  }, [chemicalSummary, chemSearch]);

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
            <Beaker className="w-3.5 h-3.5" />
            <span>Tổng hợp nhu cầu hóa chất gói thầu ({chemicalSummary.length} loại)</span>
          </button>
        </div>

        <div className="flex items-center space-x-3 text-slate-400">
          <div className="flex items-center space-x-1 text-[11px] bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <AlertCircle className="w-3.5 h-3.5 text-blue-400" />
            <span>Khoản 4.4 TT20: Đã tính thêm <strong>+8%</strong> hao hụt vụn vặt</span>
          </div>
          {viewMode === 'summary' && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Tìm tên hóa chất..."
                value={chemSearch}
                onChange={(e) => setChemSearch(e.target.value)}
                className="pl-8 pr-2.5 py-1 rounded bg-slate-950 border border-slate-700 text-slate-200 text-xs w-48 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>
      </div>

      {/* Main View Area */}
      <div className="flex-1 overflow-auto">
        {viewMode === 'by_item' ? (
          /* CHẾ ĐỘ 1: XEM THEO DÒNG CÔNG VIỆC */
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-700 text-slate-300 font-bold z-10 shadow-sm">
              <tr>
                <th className="py-2 px-2.5 w-10 text-center">STT</th>
                <th className="py-2 px-2.5 w-24">Nhóm</th>
                <th className="py-2 px-2.5 min-w-[130px]">Nhà máy</th>
                <th className="py-2 px-2.5 min-w-[140px]">Thông số quan trắc</th>
                <th className="py-2 px-2 w-16 text-right tabular-nums">Mẫu (N)</th>
                <th className="py-2 px-3 min-w-[320px] bg-emerald-950/20 text-emerald-300">
                  Danh mục hóa chất, giấy lọc & Định mức tiêu hao (+8% hao hụt)
                </th>
                <th className="py-2 px-2.5 w-24 text-center">Số loại hóa chất</th>
                <th className="py-2 px-2 w-12 text-center">Soi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {itemsWithMaterials.map((row) => (
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
                  <td className="py-2 px-3 bg-emerald-950/5">
                    {row.materials.length === 0 ? (
                      <span className="text-slate-600 italic">Không sử dụng hóa chất tiêu hao (Đo sensor trực tiếp)</span>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {row.materials.slice(0, 3).map((m, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] bg-slate-900 text-slate-200 border border-slate-800"
                            title={`${m.name}: ${m.norm_per_sample} ${m.unit}/mẫu x ${row.so_luong_mau} mẫu = ${m.total_qty} ${m.unit}`}
                          >
                            <span className="text-emerald-400 font-medium truncate max-w-[140px]">{m.name}</span>
                            <span className="text-slate-400 font-mono">({m.total_qty} {m.unit})</span>
                          </span>
                        ))}
                        {row.materials.length > 3 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{row.materials.length - 3} chất khác...
                          </span>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="py-2 px-2.5 text-center font-mono font-bold text-slate-300">
                    {row.totalMaterialsCount > 0 ? (
                      <span className="text-emerald-400">{row.totalMaterialsCount}</span>
                    ) : (
                      <span className="text-slate-600">0</span>
                    )}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <button
                      onClick={() => onSelectDrawerItem(row)}
                      className="p-1 rounded text-xs bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-blue-300 transition"
                      title="Soi sâu định mức hóa chất"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          /* CHẾ ĐỘ 2: BẢNG TỔNG HỢP NHU CẦU HÓA CHẤT GÓI THẦU */
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-700 text-slate-300 font-bold z-10 shadow-sm">
              <tr>
                <th className="py-2.5 px-3 w-12 text-center">STT</th>
                <th className="py-2.5 px-4 min-w-[280px]">Tên hóa chất, thuốc thử, giấy lọc</th>
                <th className="py-2.5 px-3 w-28 text-center">Đơn vị tính</th>
                <th className="py-2.5 px-4 w-40 text-right tabular-nums bg-emerald-950/20 text-emerald-300 font-black">
                  Tổng nhu cầu trần (+8%)
                </th>
                <th className="py-2.5 px-4 w-40 text-center">Số thông số sử dụng</th>
                <th className="py-2.5 px-4 text-slate-400">Ghi chú quản lý kho hóa chất</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
              {filteredSummary.map((chem, idx) => (
                <tr key={idx} className="hover:bg-slate-900/60 transition">
                  <td className="py-2 px-3 text-center text-slate-500">{idx + 1}</td>
                  <td className="py-2 px-4 font-sans font-semibold text-white">{chem.name}</td>
                  <td className="py-2 px-3 text-center text-slate-400 font-sans">{chem.unit}</td>
                  <td className="py-2 px-4 text-right font-black text-emerald-300 bg-emerald-950/10">
                    {chem.total_quantity.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                  </td>
                  <td className="py-2 px-4 text-center font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-blue-300 border border-slate-700 font-semibold">
                      {chem.used_by_parameters_count} thông số
                    </span>
                  </td>
                  <td className="py-2 px-4 text-slate-500 font-sans text-[11px]">
                    Hóa chất tinh khiết đạt chuẩn phân tích Vilas/Vimcerts
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
