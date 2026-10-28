import React, { useState, useMemo } from 'react';
import { Eye, CloudRain, DollarSign, Calculator } from 'lucide-react';
import type { PaktItem, PricingConfigData } from '../types';

interface Tab02NhanCongProps {
  items: PaktItem[];
  pricingConfig?: PricingConfigData | null;
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab02_NhanCong: React.FC<Tab02NhanCongProps> = ({ 
  items, 
  pricingConfig,
  onSelectDrawerItem 
}) => {
  const [viewMode, setViewMode] = useState<'norm' | 'money'>('norm');

  const resolveRate = useMemo(() => {
    return (rankStr: string): number => {
      const rates = pricingConfig?.labor_rates || {};
      if (!rankStr) return rates['Quan trắc viên tài nguyên môi trường hạng III.2'] || 550000;
      const lower = rankStr.toLowerCase();
      if (lower.includes('hạng ii')) return rates['Quan trắc viên tài nguyên môi trường hạng II'] || 850000;
      if (lower.includes('iii.1')) return rates['Quan trắc viên tài nguyên môi trường hạng III.1'] || 650000;
      if (lower.includes('iii.2')) return rates['Quan trắc viên tài nguyên môi trường hạng III.2'] || 550000;
      if (lower.includes('iii.3')) return rates['Quan trắc viên tài nguyên môi trường hạng III.3'] || 450000;
      if (lower.includes('hạng iv') || lower.includes('iv')) return rates['Quan trắc viên tài nguyên môi trường hạng IV'] || 450000;
      if (lower.includes('lao động') || lower.includes('phổ thông')) return rates['Kỹ thuật viên / Lao động phổ thông'] || 350000;
      return rates['Quan trắc viên tài nguyên môi trường hạng III.2'] || 550000;
    };
  }, [pricingConfig]);

  // Tính tổng cộng footer
  const totals = useMemo(() => {
    let fieldDays = 0;
    let labDays = 0;
    let fieldMoney = 0;
    let labMoney = 0;

    items.forEach(row => {
      if (row.is_header) return;
      const N = row.so_luong_mau || 0;
      const tt = row.tt20_data;
      if (!tt || N <= 0) return;

      if (tt.field) {
        const d = Number(tt.field.dinh_muc_cong || 0) * 1.2 * N;
        const rate = resolveRate(tt.field.dinh_bien || '');
        fieldDays += d;
        fieldMoney += d * rate;
      }
      if (tt.lab) {
        const d = Number(tt.lab.dinh_muc_cong || 0) * N;
        const rate = resolveRate(tt.lab.dinh_bien || '');
        labDays += d;
        labMoney += d * rate;
      }
      if (tt.single) {
        const d = Number(tt.single.dinh_muc_cong || 0) * 1.2 * N;
        const rate = resolveRate(tt.single.dinh_bien || '');
        fieldDays += d;
        fieldMoney += d * rate;
      }
    });

    return {
      fieldDays,
      labDays,
      totalDays: fieldDays + labDays,
      fieldMoney,
      labMoney,
      totalMoney: fieldMoney + labMoney
    };
  }, [items, resolveRate]);

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950">
      {/* 1. Sub-toolbar for Switching View Mode */}
      <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between z-20 shrink-0">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-300">Chế độ hiển thị:</span>
          <div className="bg-slate-950 p-0.5 rounded-lg border border-slate-800 flex items-center space-x-1">
            <button
              onClick={() => setViewMode('norm')}
              className={`px-3 py-1 rounded-md text-xs font-medium transition flex items-center space-x-1.5 ${
                viewMode === 'norm'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Calculator className="w-3.5 h-3.5" />
              <span>📊 Số công định mức (TT20)</span>
            </button>
            <button
              onClick={() => setViewMode('money')}
              className={`px-3 py-1 rounded-md text-xs font-medium transition flex items-center space-x-1.5 ${
                viewMode === 'money'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <DollarSign className="w-3.5 h-3.5" />
              <span>💰 Thành tiền chi tiết (VNĐ)</span>
            </button>
          </div>
          {viewMode === 'money' && (
            <span className="text-[11px] text-emerald-400 font-mono bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/40">
              Áp theo TTLT 56/2015 & VB 5691/EVN
            </span>
          )}
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono">
          {viewMode === 'norm' ? (
            <div className="flex items-center space-x-3 text-slate-300">
              <span>Ngoại: <strong className="text-amber-400">{totals.fieldDays.toFixed(2)}</strong> công</span>
              <span>•</span>
              <span>Lab: <strong className="text-purple-400">{totals.labDays.toFixed(2)}</strong> công</span>
              <span>•</span>
              <span>Tổng: <strong className="text-blue-400">{totals.totalDays.toFixed(2)}</strong> công</span>
            </div>
          ) : (
            <div className="flex items-center space-x-3 text-slate-300">
              <span>Ngoại: <strong className="text-amber-400">{totals.fieldMoney.toLocaleString('vi-VN')}</strong> đ</span>
              <span>•</span>
              <span>Lab: <strong className="text-purple-400">{totals.labMoney.toLocaleString('vi-VN')}</strong> đ</span>
              <span>•</span>
              <span>Tổng quỹ lương: <strong className="text-emerald-400 font-bold">{totals.totalMoney.toLocaleString('vi-VN')}</strong> VNĐ</span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Main Data Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="sticky top-0 bg-slate-900 border-b border-slate-700/80 text-slate-300 font-bold z-10 shadow-sm">
            {/* Multi-tier header */}
            <tr className="border-b border-slate-800 text-[11px]">
              <th colSpan={7} className="py-2 px-3 text-center bg-slate-900 border-r border-slate-800 text-slate-400 uppercase tracking-wider">
                Khối lượng công việc Phụ lục 1 (PAKT Đề xuất)
              </th>
              {viewMode === 'norm' ? (
                <>
                  <th colSpan={4} className="py-2 px-3 text-center bg-amber-950/30 text-amber-300 border-r border-slate-800 uppercase tracking-wider">
                    1. Ngoại nghiệp (Khoản 4.1.3 TT20: Hệ số thời tiết +20%)
                  </th>
                  <th colSpan={3} className="py-2 px-3 text-center bg-purple-950/30 text-purple-300 border-r border-slate-800 uppercase tracking-wider">
                    2. Nội nghiệp (Phòng thí nghiệm)
                  </th>
                  <th colSpan={2} className="py-2 px-3 text-center bg-blue-950/30 text-blue-300 uppercase tracking-wider">
                    Tổng số công TT20
                  </th>
                </>
              ) : (
                <>
                  <th colSpan={3} className="py-2 px-3 text-center bg-amber-950/40 text-amber-300 border-r border-slate-800 uppercase tracking-wider">
                    1. Chi phí Lương Ngoại nghiệp (VNĐ)
                  </th>
                  <th colSpan={3} className="py-2 px-3 text-center bg-purple-950/40 text-purple-300 border-r border-slate-800 uppercase tracking-wider">
                    2. Chi phí Lương Nội nghiệp (VNĐ)
                  </th>
                  <th colSpan={2} className="py-2 px-3 text-center bg-emerald-950/40 text-emerald-300 uppercase tracking-wider">
                    Tổng tiền lương nhân công
                  </th>
                </>
              )}
            </tr>

            {/* Column subheaders */}
            <tr>
              <th className="py-2 px-2.5 w-10 text-center">STT</th>
              <th className="py-2 px-2.5 w-24">Nhóm</th>
              <th className="py-2 px-2.5 min-w-[120px]">Nhà máy</th>
              <th className="py-2 px-2.5 min-w-[130px]">Môi trường</th>
              <th className="py-2 px-2.5 min-w-[180px]">Thông số quan trắc</th>
              <th className="py-2 px-2 w-14 text-center">ĐVT</th>
              <th className="py-2 px-2.5 w-16 text-right tabular-nums border-r border-slate-800">Mẫu (N)</th>

              {viewMode === 'norm' ? (
                <>
                  {/* Ngoại nghiệp - Hao phí */}
                  <th className="py-2 px-2.5 w-28 bg-amber-950/20 text-amber-300">Bậc thợ</th>
                  <th className="py-2 px-2 w-16 text-right bg-amber-950/20 text-amber-400/80 tabular-nums" title="Định mức công gốc theo TT20">ĐM gốc</th>
                  <th className="py-2 px-2 w-20 text-right bg-amber-950/20 text-amber-300 tabular-nums font-semibold" title="Định mức đã nhân hệ số thời tiết 1,2 theo Khoản 4.1.3 TT20">
                    <span className="flex items-center justify-end space-x-1">
                      <CloudRain className="w-3 h-3 text-amber-400" />
                      <span>+20% TT</span>
                    </span>
                  </th>
                  <th className="py-2 px-2.5 w-24 text-right bg-amber-950/20 text-amber-300 tabular-nums font-bold border-r border-slate-800">
                    Tổng ngoại
                  </th>

                  {/* Nội nghiệp - Hao phí */}
                  <th className="py-2 px-2.5 w-28 bg-purple-950/20 text-purple-300">Bậc thợ</th>
                  <th className="py-2 px-2 w-16 text-right bg-purple-950/20 text-purple-300 tabular-nums">ĐM/mẫu</th>
                  <th className="py-2 px-2.5 w-24 text-right bg-purple-950/20 text-purple-300 tabular-nums font-bold border-r border-slate-800">
                    Tổng nội
                  </th>

                  {/* Tổng công */}
                  <th className="py-2 px-3 w-28 text-right bg-blue-950/20 text-blue-300 tabular-nums font-black">
                    Tổng cộng
                  </th>
                  <th className="py-2 px-2 w-12 text-center bg-blue-950/20">Soi</th>
                </>
              ) : (
                <>
                  {/* Ngoại nghiệp - Thành tiền */}
                  <th className="py-2 px-2.5 w-28 bg-amber-950/20 text-amber-300">Bậc thợ</th>
                  <th className="py-2 px-2.5 w-24 text-right bg-amber-950/20 text-amber-300 tabular-nums font-mono" title="Đơn giá lương theo bậc ngạch">Đơn giá/ngày</th>
                  <th className="py-2 px-3 w-28 text-right bg-amber-950/20 text-amber-300 tabular-nums font-bold border-r border-slate-800">
                    Tiền ngoại (đ)
                  </th>

                  {/* Nội nghiệp - Thành tiền */}
                  <th className="py-2 px-2.5 w-28 bg-purple-950/20 text-purple-300">Bậc thợ</th>
                  <th className="py-2 px-2.5 w-24 text-right bg-purple-950/20 text-purple-300 tabular-nums font-mono" title="Đơn giá lương theo bậc ngạch">Đơn giá/ngày</th>
                  <th className="py-2 px-3 w-28 text-right bg-purple-950/20 text-purple-300 tabular-nums font-bold border-r border-slate-800">
                    Tiền lab (đ)
                  </th>

                  {/* Tổng tiền */}
                  <th className="py-2 px-3 w-32 text-right bg-emerald-950/20 text-emerald-300 tabular-nums font-black">
                    Tổng lương (đ)
                  </th>
                  <th className="py-2 px-2 w-12 text-center bg-emerald-950/20">Soi</th>
                </>
              )}
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800 text-slate-300">
            {items.map((row) => {
              if (row.is_header) {
                return (
                  <tr key={row.id} className="bg-slate-900/90 border-y border-blue-900/60 text-blue-300">
                    <td className="py-2 px-2.5 text-center text-slate-500 font-mono">{row.id}</td>
                    <td colSpan={6} className="py-2 px-3 font-semibold text-xs text-blue-300">
                      📂 {row.thong_so}
                    </td>
                    <td colSpan={viewMode === 'norm' ? 9 : 8} className="py-2 px-3 text-slate-500 italic text-[11px]">
                      Dòng tiêu đề phân loại PAKT (không phát sinh chi phí nhân công)
                    </td>
                  </tr>
                );
              }

              const N = row.so_luong_mau || 0;
              const tt = row.tt20_data;

              let fieldRank = '—';
              let fieldNormRaw = 0;
              let fieldNormWeather = 0;
              let fieldTotal = 0;

              let labRank = '—';
              let labNorm = 0;
              let labTotal = 0;

              if (tt) {
                if (tt.field) {
                  fieldRank = tt.field.dinh_bien || 'QTVTNMT';
                  fieldNormRaw = Number(tt.field.dinh_muc_cong || 0);
                  fieldNormWeather = fieldNormRaw * 1.2;
                  fieldTotal = fieldNormWeather * N;
                }
                if (tt.lab) {
                  labRank = tt.lab.dinh_bien || 'QTVTNMT';
                  labNorm = Number(tt.lab.dinh_muc_cong || 0);
                  labTotal = labNorm * N;
                }
                if (tt.single) {
                  fieldRank = tt.single.dinh_bien || 'QTVTNMT';
                  fieldNormRaw = Number(tt.single.dinh_muc_cong || 0);
                  fieldNormWeather = fieldNormRaw * 1.2;
                  fieldTotal = fieldNormWeather * N;
                }
              }

              const grandTotalDays = fieldTotal + labTotal;

              // Tính giá trị tiền
              const fieldDailyRate = fieldTotal > 0 ? resolveRate(fieldRank) : 0;
              const labDailyRate = labTotal > 0 ? resolveRate(labRank) : 0;
              const fieldMoney = fieldTotal * fieldDailyRate;
              const labMoney = labTotal * labDailyRate;
              const grandTotalMoney = fieldMoney + labMoney;

              return (
                <tr key={row.id} className="hover:bg-slate-900/60 transition group">
                  <td className="py-2 px-2.5 text-center text-slate-500 font-mono">{row.id}</td>
                  <td className="py-2 px-2.5">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      row.nhom.includes('Định kỳ')
                        ? 'bg-blue-950 text-blue-300 border border-blue-800/40'
                        : 'bg-purple-950 text-purple-300 border border-purple-800/40'
                    }`}>
                      {row.nhom.includes('Định kỳ') ? 'Định kỳ' : 'Đối chứng'}
                    </span>
                  </td>
                  <td className="py-2 px-2.5 text-slate-300 truncate max-w-[130px]" title={row.khu_vuc}>
                    {row.khu_vuc.replace('Nhà máy Nhiệt điện ', 'NMNĐ ')}
                  </td>
                  <td className="py-2 px-2.5 text-slate-400 truncate max-w-[140px]" title={row.moi_truong}>
                    {row.moi_truong}
                  </td>
                  <td className="py-2 px-2.5 font-semibold text-white truncate max-w-[200px]" title={row.thong_so}>
                    {row.thong_so}
                  </td>
                  <td className="py-2 px-2 text-center text-slate-400">{row.dvt}</td>
                  <td className="py-2 px-2.5 text-right font-bold text-slate-200 tabular-nums font-mono border-r border-slate-800">
                    {N}
                  </td>

                  {viewMode === 'norm' ? (
                    <>
                      {/* Ngoại nghiệp - Hao phí */}
                      <td className="py-2 px-2.5 text-amber-300/90 truncate max-w-[130px] bg-amber-950/10" title={fieldRank}>
                        {fieldRank}
                      </td>
                      <td className="py-2 px-2 text-right text-slate-500 tabular-nums font-mono bg-amber-950/10" title="Định mức gốc chưa nhân hệ số thời tiết">
                        {fieldNormRaw > 0 ? fieldNormRaw.toFixed(3) : '—'}
                      </td>
                      <td className="py-2 px-2 text-right text-amber-400 tabular-nums font-mono font-medium bg-amber-950/10" title="Đã nhân 1,2 theo Khoản 4.1.3 TT20">
                        {fieldNormWeather > 0 ? fieldNormWeather.toFixed(3) : '—'}
                      </td>
                      <td className="py-2 px-2.5 text-right font-bold text-amber-300 tabular-nums font-mono bg-amber-950/10 border-r border-slate-800">
                        {fieldTotal > 0 ? fieldTotal.toFixed(2) : '—'}
                      </td>

                      {/* Nội nghiệp - Hao phí */}
                      <td className="py-2 px-2.5 text-purple-300/90 truncate max-w-[130px] bg-purple-950/10" title={labRank}>
                        {labRank}
                      </td>
                      <td className="py-2 px-2 text-right text-slate-400 tabular-nums font-mono bg-purple-950/10">
                        {labNorm > 0 ? labNorm.toFixed(3) : '—'}
                      </td>
                      <td className="py-2 px-2.5 text-right font-bold text-purple-300 tabular-nums font-mono bg-purple-950/10 border-r border-slate-800">
                        {labTotal > 0 ? labTotal.toFixed(2) : '—'}
                      </td>

                      {/* Tổng công */}
                      <td className="py-2 px-3 text-right font-black text-white tabular-nums font-mono bg-blue-950/10">
                        {grandTotalDays > 0 ? (
                          <span className="text-blue-300 font-bold">{grandTotalDays.toFixed(2)} công</span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                    </>
                  ) : (
                    <>
                      {/* Ngoại nghiệp - Thành tiền */}
                      <td className="py-2 px-2.5 text-amber-300/90 truncate max-w-[130px] bg-amber-950/10" title={fieldRank}>
                        {fieldRank}
                      </td>
                      <td className="py-2 px-2.5 text-right text-slate-400 tabular-nums font-mono bg-amber-950/10">
                        {fieldDailyRate > 0 ? fieldDailyRate.toLocaleString('vi-VN') : '—'}
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-amber-300 tabular-nums font-mono bg-amber-950/10 border-r border-slate-800">
                        {fieldMoney > 0 ? Math.round(fieldMoney).toLocaleString('vi-VN') : '—'}
                      </td>

                      {/* Nội nghiệp - Thành tiền */}
                      <td className="py-2 px-2.5 text-purple-300/90 truncate max-w-[130px] bg-purple-950/10" title={labRank}>
                        {labRank}
                      </td>
                      <td className="py-2 px-2.5 text-right text-slate-400 tabular-nums font-mono bg-purple-950/10">
                        {labDailyRate > 0 ? labDailyRate.toLocaleString('vi-VN') : '—'}
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-purple-300 tabular-nums font-mono bg-purple-950/10 border-r border-slate-800">
                        {labMoney > 0 ? Math.round(labMoney).toLocaleString('vi-VN') : '—'}
                      </td>

                      {/* Tổng tiền */}
                      <td className="py-2 px-3 text-right font-black text-emerald-300 tabular-nums font-mono bg-emerald-950/10">
                        {grandTotalMoney > 0 ? (
                          <span className="font-bold">{Math.round(grandTotalMoney).toLocaleString('vi-VN')} đ</span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                    </>
                  )}

                  <td className="py-2 px-2 text-center bg-slate-900/40">
                    <button
                      onClick={() => onSelectDrawerItem(row)}
                      className="p-1 rounded text-xs bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-blue-300 transition"
                      title="Mở Drawer soi sâu 4 bậc"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>

          {/* Footer Total Row */}
          <tfoot className="sticky bottom-0 bg-slate-900 border-t-2 border-slate-700 text-white font-bold z-10 shadow-lg">
            <tr>
              <td colSpan={7} className="py-2.5 px-3 text-right text-xs uppercase tracking-wider text-slate-400 border-r border-slate-800">
                Tổng cộng toàn dự án (253 công việc - 1.683 mẫu):
              </td>
              {viewMode === 'norm' ? (
                <>
                  <td colSpan={3} className="py-2.5 px-3 text-right text-amber-400 font-mono text-xs">
                    Ngoại nghiệp (+20% TT):
                  </td>
                  <td className="py-2.5 px-2.5 text-right font-mono font-black text-amber-300 border-r border-slate-800 text-sm">
                    {totals.fieldDays.toFixed(2)} công
                  </td>
                  <td colSpan={2} className="py-2.5 px-3 text-right text-purple-400 font-mono text-xs">
                    Nội nghiệp:
                  </td>
                  <td className="py-2.5 px-2.5 text-right font-mono font-black text-purple-300 border-r border-slate-800 text-sm">
                    {totals.labDays.toFixed(2)} công
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-black text-blue-400 text-sm bg-blue-950/40">
                    {totals.totalDays.toFixed(2)} công
                  </td>
                  <td className="bg-blue-950/40"></td>
                </>
              ) : (
                <>
                  <td colSpan={2} className="py-2.5 px-3 text-right text-amber-400 font-mono text-xs">
                    Quỹ lương ngoại:
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-black text-amber-300 border-r border-slate-800 text-sm">
                    {Math.round(totals.fieldMoney).toLocaleString('vi-VN')} đ
                  </td>
                  <td colSpan={2} className="py-2.5 px-3 text-right text-purple-400 font-mono text-xs">
                    Quỹ lương lab:
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-black text-purple-300 border-r border-slate-800 text-sm">
                    {Math.round(totals.labMoney).toLocaleString('vi-VN')} đ
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-black text-emerald-400 text-base bg-emerald-950/40">
                    {Math.round(totals.totalMoney).toLocaleString('vi-VN')} đ
                  </td>
                  <td className="bg-emerald-950/40"></td>
                </>
              )}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};
