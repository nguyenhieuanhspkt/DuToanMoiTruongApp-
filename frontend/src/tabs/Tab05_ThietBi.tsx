import React, { useState, useMemo } from 'react';
import { Eye, Cpu, Layers, Search, AlertCircle, Zap } from 'lucide-react';
import type { PaktItem, EquipmentNormDetail } from '../types';

interface Tab05ThietBiProps {
  items: PaktItem[];
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab05_ThietBi: React.FC<Tab05ThietBiProps> = ({ items, onSelectDrawerItem }) => {
  const [viewMode, setViewMode] = useState<'by_item' | 'summary'>('by_item');
  const [eqSearch, setEqSearch] = useState<string>('');

  // 1. Trích xuất chi tiết thiết bị theo từng dòng công việc
  const itemsWithEquipment = useMemo(() => {
    return items.map((row) => {
      const N = row.so_luong_mau || 1;
      const tt = row.tt20_data;
      const secId = row.sec_id || '';
      const eqs: EquipmentNormDetail[] = [];

      if (tt) {
        for (const [stageKey, stageLabel] of [
          ['field', 'Ngoại nghiệp'],
          ['lab', 'Nội nghiệp'],
          ['single', 'Toàn phần'],
        ] as const) {
          const sub = tt[stageKey];
          if (sub && sub.equipment) {
            const annualShifts = stageLabel === 'Ngoại nghiệp' ? (secId.includes('II.6') ? 200.0 : 250.0) : 500.0;

            for (const e of sub.equipment) {
              const normShift = Number(e.norm || 0);
              const specStr = String(e.spec || '').trim().replace(',', '.');
              let powerKw = 0;
              try {
                if (specStr && /\d/.test(specStr)) {
                  const cleaned = specStr.replace(/[^\d.]/g, '');
                  powerKw = Number(cleaned) || 0;
                }
              } catch {
                powerKw = 0;
              }

              const totalShifts = Number((normShift * N).toFixed(4));
              const totalKwh = Number((powerKw * 8.0 * totalShifts).toFixed(2));

              eqs.push({
                stage: stageLabel,
                name: String(e.name || '').trim(),
                unit: String(e.unit || 'bộ').trim(),
                spec: String(e.spec || '').trim(),
                power_kw: powerKw,
                annual_standard_shifts: annualShifts,
                norm_shift_per_sample: normShift,
                total_shifts: totalShifts,
                total_kwh: totalKwh,
                is_inherited: normShift === 0,
              });
            }
          }
        }
      }

      return {
        ...row,
        equipment: eqs,
        totalEquipmentCount: eqs.length,
      };
    });
  }, [items]);

  // 2. Tổng hợp danh mục ca máy & điện năng toàn gói thầu
  const equipmentSummary = useMemo(() => {
    const summaryMap: Record<string, { name: string; unit: string; total_shifts: number; total_kwh: number; count: number; annual_shifts: number }> = {};

    for (const row of itemsWithEquipment) {
      for (const eq of row.equipment) {
        if (!eq.name) continue;
        const key = `${eq.name}___${eq.annual_standard_shifts}`;
        if (!summaryMap[key]) {
          summaryMap[key] = {
            name: eq.name,
            unit: eq.unit,
            total_shifts: 0,
            total_kwh: 0,
            count: 0,
            annual_shifts: eq.annual_standard_shifts,
          };
        }
        summaryMap[key].total_shifts += eq.total_shifts;
        summaryMap[key].total_kwh += eq.total_kwh;
        summaryMap[key].count += 1;
      }
    }

    const list = Object.values(summaryMap).map((eq) => ({
      ...eq,
      total_shifts: Number(eq.total_shifts.toFixed(4)),
      total_kwh: Number(eq.total_kwh.toFixed(2)),
    }));

    return list.sort((a, b) => b.total_shifts - a.total_shifts);
  }, [itemsWithEquipment]);

  const filteredEquipmentSummary = useMemo(() => {
    if (!eqSearch.trim()) return equipmentSummary;
    const q = eqSearch.toLowerCase();
    return equipmentSummary.filter((e) => e.name.toLowerCase().includes(q));
  }, [equipmentSummary, eqSearch]);

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
            <Cpu className="w-3.5 h-3.5" />
            <span>Tổng hợp ca máy & điện năng ({equipmentSummary.length} thiết bị)</span>
          </button>
        </div>

        <div className="flex items-center space-x-3 text-slate-400">
          <div className="flex items-center space-x-1 text-[11px] bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <AlertCircle className="w-3.5 h-3.5 text-blue-400" />
            <span>Khoản 4.3 TT20: Chuẩn <strong>250 ca</strong> (đất liền) / <strong>200 ca</strong> (biển II.6) / <strong>500 ca</strong> (lab)</span>
          </div>
          {viewMode === 'summary' && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Tìm tên máy móc..."
                value={eqSearch}
                onChange={(e) => setEqSearch(e.target.value)}
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
                <th className="py-2 px-3 min-w-[320px] bg-purple-950/20 text-purple-300">
                  Thiết bị đo, ca máy & Suất tiêu hao điện năng (kWh)
                </th>
                <th className="py-2 px-2.5 w-24 text-center">Số thiết bị</th>
                <th className="py-2 px-2 w-12 text-center">Soi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {itemsWithEquipment.map((row) => (
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
                  <td className="py-2 px-3 bg-purple-950/5">
                    {row.equipment.length === 0 ? (
                      <span className="text-slate-600 italic">Không sử dụng máy đo chuyên dụng</span>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {row.equipment.slice(0, 3).map((eq, idx) => (
                          <span
                            key={idx}
                            className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] border ${
                              eq.is_inherited
                                ? 'bg-slate-900/40 text-slate-500 border-dashed border-slate-700'
                                : 'bg-slate-900 text-slate-200 border-slate-800'
                            }`}
                            title={`${eq.name}: ${eq.norm_shift_per_sample} ca/mẫu x ${row.so_luong_mau} = ${eq.total_shifts} ca (${eq.annual_standard_shifts} ca/năm)`}
                          >
                            <span className="text-purple-300 font-medium truncate max-w-[140px]">{eq.name}</span>
                            <span className="text-slate-400 font-mono">({eq.total_shifts} ca)</span>
                            {eq.total_kwh > 0 && (
                              <span className="text-amber-400 font-mono flex items-center text-[10px]">
                                <Zap className="w-2.5 h-2.5 mr-0.5" />{eq.total_kwh}kwh
                              </span>
                            )}
                          </span>
                        ))}
                        {row.equipment.length > 3 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{row.equipment.length - 3} thiết bị khác...
                          </span>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="py-2 px-2.5 text-center font-mono font-bold text-slate-300">
                    {row.totalEquipmentCount > 0 ? (
                      <span className="text-purple-400">{row.totalEquipmentCount}</span>
                    ) : (
                      <span className="text-slate-600">0</span>
                    )}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <button
                      onClick={() => onSelectDrawerItem(row)}
                      className="p-1 rounded text-xs bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-blue-300 transition"
                      title="Soi sâu định mức thiết bị"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          /* CHẾ ĐỘ 2: TỔNG HỢP DANH MỤC THIẾT BỊ GÓI THẦU */
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-700 text-slate-300 font-bold z-10 shadow-sm">
              <tr>
                <th className="py-2.5 px-3 w-12 text-center">STT</th>
                <th className="py-2.5 px-4 min-w-[280px]">Tên thiết bị, máy móc quan trắc & phân tích</th>
                <th className="py-2.5 px-3 w-28 text-center">Chuẩn ca năm (TT20)</th>
                <th className="py-2.5 px-4 w-36 text-right tabular-nums bg-purple-950/20 text-purple-300 font-black">
                  Tổng ca máy sử dụng
                </th>
                <th className="py-2.5 px-4 w-36 text-right tabular-nums bg-amber-950/20 text-amber-300 font-black">
                  Điện năng tiêu thụ (kWh)
                </th>
                <th className="py-2.5 px-4 w-32 text-center">Số thông số đo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
              {filteredEquipmentSummary.map((eq, idx) => (
                <tr key={idx} className="hover:bg-slate-900/60 transition">
                  <td className="py-2 px-3 text-center text-slate-500">{idx + 1}</td>
                  <td className="py-2 px-4 font-sans font-semibold text-white">{eq.name}</td>
                  <td className="py-2 px-3 text-center font-sans text-slate-400">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 border border-slate-700">
                      {eq.annual_shifts} ca/năm
                    </span>
                  </td>
                  <td className="py-2 px-4 text-right font-black text-purple-300 bg-purple-950/10">
                    {eq.total_shifts.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 4 })} ca
                  </td>
                  <td className="py-2 px-4 text-right font-black text-amber-400 bg-amber-950/10">
                    {eq.total_kwh > 0 ? `${eq.total_kwh.toLocaleString('vi-VN')} kWh` : '—'}
                  </td>
                  <td className="py-2 px-4 text-center font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-blue-300 border border-slate-700 font-semibold">
                      {eq.count} thông số
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
