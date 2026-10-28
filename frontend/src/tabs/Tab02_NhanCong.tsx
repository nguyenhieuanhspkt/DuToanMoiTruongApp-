import React from 'react';
import { Eye } from 'lucide-react';
import type { PaktItem } from '../types';

interface Tab02NhanCongProps {
  items: PaktItem[];
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab02_NhanCong: React.FC<Tab02NhanCongProps> = ({ items, onSelectDrawerItem }) => {
  return (
    <div className="flex-1 overflow-auto bg-slate-950">
      <table className="w-full text-left border-collapse text-xs">
        <thead className="sticky top-0 bg-slate-900 border-b border-slate-700/80 text-slate-300 font-bold z-10 shadow-sm">
          {/* Multi-tier header */}
          <tr className="border-b border-slate-800 text-[11px]">
            <th colSpan={7} className="py-2 px-3 text-center bg-slate-900 border-r border-slate-800 text-slate-400 uppercase tracking-wider">
              Khối lượng công việc Phụ lục 1 (PAKT Đề xuất)
            </th>
            <th colSpan={3} className="py-2 px-3 text-center bg-amber-950/30 text-amber-300 border-r border-slate-800 uppercase tracking-wider">
              1. Ngoại nghiệp (Hiện trường)
            </th>
            <th colSpan={3} className="py-2 px-3 text-center bg-purple-950/30 text-purple-300 border-r border-slate-800 uppercase tracking-wider">
              2. Nội nghiệp (Phòng thí nghiệm)
            </th>
            <th colSpan={2} className="py-2 px-3 text-center bg-blue-950/30 text-blue-300 uppercase tracking-wider">
              Tổng số công TT20
            </th>
          </tr>
          <tr>
            <th className="py-2 px-2.5 w-10 text-center">STT</th>
            <th className="py-2 px-2.5 w-24">Nhóm</th>
            <th className="py-2 px-2.5 min-w-[120px]">Nhà máy</th>
            <th className="py-2 px-2.5 min-w-[130px]">Môi trường</th>
            <th className="py-2 px-2.5 min-w-[180px]">Thông số quan trắc</th>
            <th className="py-2 px-2 w-14 text-center">ĐVT</th>
            <th className="py-2 px-2.5 w-16 text-right tabular-nums border-r border-slate-800">Mẫu (N)</th>

            {/* Ngoại nghiệp */}
            <th className="py-2 px-2.5 w-32 bg-amber-950/20 text-amber-300">Bậc thợ</th>
            <th className="py-2 px-2 w-20 text-right bg-amber-950/20 text-amber-300 tabular-nums">ĐM/mẫu</th>
            <th className="py-2 px-2.5 w-24 text-right bg-amber-950/20 text-amber-300 tabular-nums font-bold border-r border-slate-800">
              Tổng công
            </th>

            {/* Nội nghiệp */}
            <th className="py-2 px-2.5 w-32 bg-purple-950/20 text-purple-300">Bậc thợ</th>
            <th className="py-2 px-2 w-20 text-right bg-purple-950/20 text-purple-300 tabular-nums">ĐM/mẫu</th>
            <th className="py-2 px-2.5 w-24 text-right bg-purple-950/20 text-purple-300 tabular-nums font-bold border-r border-slate-800">
              Tổng công
            </th>

            {/* Tổng công */}
            <th className="py-2 px-3 w-28 text-right bg-blue-950/20 text-blue-300 tabular-nums font-black">
              Tổng (×N)
            </th>
            <th className="py-2 px-2 w-12 text-center bg-blue-950/20">Soi</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 text-slate-300">
          {items.map((row) => {
            const N = row.so_luong_mau || 1;
            const tt = row.tt20_data;

            let fieldRank = '—';
            let fieldNorm = 0;
            let fieldTotal = 0;

            let labRank = '—';
            let labNorm = 0;
            let labTotal = 0;

            if (tt) {
              if (tt.field) {
                fieldRank = tt.field.dinh_bien || 'QTVTNMT';
                fieldNorm = Number(tt.field.dinh_muc_cong || 0);
                fieldTotal = fieldNorm * N;
              }
              if (tt.lab) {
                labRank = tt.lab.dinh_bien || 'QTVTNMT';
                labNorm = Number(tt.lab.dinh_muc_cong || 0);
                labTotal = labNorm * N;
              }
              if (tt.single) {
                fieldRank = tt.single.dinh_bien || 'QTVTNMT';
                fieldNorm = Number(tt.single.dinh_muc_cong || 0);
                fieldTotal = fieldNorm * N;
              }
            }

            const grandTotal = fieldTotal + labTotal;

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

                {/* Ngoại nghiệp */}
                <td className="py-2 px-2.5 text-amber-300/90 truncate max-w-[130px] bg-amber-950/10" title={fieldRank}>
                  {fieldRank}
                </td>
                <td className="py-2 px-2 text-right text-slate-400 tabular-nums font-mono bg-amber-950/10">
                  {fieldNorm > 0 ? fieldNorm.toFixed(3) : '—'}
                </td>
                <td className="py-2 px-2.5 text-right font-bold text-amber-300 tabular-nums font-mono bg-amber-950/10 border-r border-slate-800">
                  {fieldTotal > 0 ? fieldTotal.toFixed(2) : '—'}
                </td>

                {/* Nội nghiệp */}
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
                  {grandTotal > 0 ? (
                    <span className="text-blue-300 font-bold">{grandTotal.toFixed(2)} công</span>
                  ) : (
                    <span className="text-slate-600">—</span>
                  )}
                </td>
                <td className="py-2 px-2 text-center bg-blue-950/10">
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
      </table>
    </div>
  );
};
