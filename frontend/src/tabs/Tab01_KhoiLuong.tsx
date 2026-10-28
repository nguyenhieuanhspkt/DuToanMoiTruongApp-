import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Eye, Layers } from 'lucide-react';
import type { PaktItem } from '../types';

interface Tab01KhoiLuongProps {
  items: PaktItem[];
  onSelectDrawerItem: (item: PaktItem) => void;
}

export const Tab01_KhoiLuong: React.FC<Tab01KhoiLuongProps> = ({ items, onSelectDrawerItem }) => {
  const [expandedRows, setExpandedRows] = useState<Record<number, boolean>>({});

  const toggleRow = (id: number) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex-1 overflow-auto bg-slate-950">
      <table className="w-full text-left border-collapse text-xs">
        <thead className="sticky top-0 bg-slate-900 border-b border-slate-700/80 text-slate-300 font-bold z-10 shadow-sm">
          <tr>
            <th className="py-2.5 px-3 w-12 text-center">STT</th>
            <th className="py-2.5 px-3 w-28">Nhóm</th>
            <th className="py-2.5 px-3 min-w-[140px]">Khu vực / Nhà máy</th>
            <th className="py-2.5 px-3 min-w-[150px]">Môi trường</th>
            <th className="py-2.5 px-3 min-w-[200px]">Tên thông số quan trắc</th>
            <th className="py-2.5 px-3 w-16 text-center">ĐVT</th>
            <th className="py-2.5 px-3 w-24 text-right tabular-nums">Số lượng (N)</th>
            <th className="py-2.5 px-3 w-28 text-center bg-blue-950/40 border-l border-blue-900/40">Mã TT20</th>
            <th className="py-2.5 px-3 min-w-[160px] bg-blue-950/40">Thông số đối chiếu</th>
            <th className="py-2.5 px-3 w-24 text-center bg-blue-950/40">Bóc tách</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 text-slate-300">
          {items.map((row) => {
            const isExpanded = Boolean(expandedRows[row.id]);
            const tt = row.tt20_data;
            const N = row.so_luong_mau || 1;

            return (
              <React.Fragment key={row.id}>
                <tr className="hover:bg-slate-900/60 transition group">
                  <td className="py-2 px-3 text-center text-slate-500 font-mono">{row.id}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      row.nhom.includes('Định kỳ')
                        ? 'bg-blue-950 text-blue-300 border border-blue-800/40'
                        : 'bg-purple-950 text-purple-300 border border-purple-800/40'
                    }`}>
                      {row.nhom.includes('Định kỳ') ? 'Định kỳ' : 'Đối chứng'}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-300 font-medium truncate max-w-[150px]" title={row.khu_vuc}>
                    {row.khu_vuc.replace('Nhà máy Nhiệt điện ', 'NMNĐ ')}
                  </td>
                  <td className="py-2 px-3 text-slate-400 truncate max-w-[160px]" title={row.moi_truong}>
                    {row.moi_truong}
                  </td>
                  <td className="py-2 px-3 font-semibold text-white">
                    {row.thong_so}
                    {row.vi_tri && (
                      <span className="block text-[10px] text-slate-400 font-normal truncate max-w-xs" title={row.vi_tri}>
                        📍 {row.vi_tri}
                      </span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-center text-slate-400">{row.dvt}</td>
                  <td className="py-2 px-3 text-right font-bold text-white tabular-nums font-mono">
                    {N} <span className="text-[10px] font-normal text-slate-400">({row.so_vi_tri}x{row.so_lan})</span>
                  </td>
                  <td className="py-2 px-3 text-center border-l border-slate-800 bg-slate-900/30">
                    <span className="font-mono font-bold text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/40">
                      {row.ma_gop || '—'}
                    </span>
                  </td>
                  <td className="py-2 px-3 bg-slate-900/30 text-slate-300">
                    {tt ? (
                      <div>
                        <div className="font-medium text-blue-200">{tt.name}</div>
                        {tt.standard && <div className="text-[10px] text-slate-500 font-mono">{tt.standard}</div>}
                      </div>
                    ) : (
                      <span className="text-amber-500/70 italic text-[11px]">Chưa ánh xạ</span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-center bg-slate-900/30">
                    <div className="flex items-center justify-center space-x-1">
                      <button
                        onClick={() => toggleRow(row.id)}
                        className={`p-1 rounded text-xs transition ${
                          isExpanded
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
                        }`}
                        title="Bung 4 bảng hao phí chi tiết tại chỗ"
                      >
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </button>
                      <button
                        onClick={() => onSelectDrawerItem(row)}
                        className="p-1 rounded text-xs bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-blue-300 transition"
                        title="Mở Drawer soi sâu 4 bậc"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>

                {/* Accordion Inline Row */}
                {isExpanded && (
                  <tr className="bg-slate-900/90 border-b border-slate-700/60">
                    <td colSpan={10} className="p-4">
                      {!tt ? (
                        <div className="text-amber-400 text-xs italic">Không tìm thấy định mức chi tiết trong CSDL TT20.</div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 text-xs font-bold text-blue-300">
                            <Layers className="w-4 h-4" />
                            <span>BÓC TÁCH CHI TIẾT 4 BẢNG HAO PHÍ CHO {N} {row.dvt.toUpperCase()} (HỌC PHẦN {row.sec_id}):</span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                            {/* Bảng 1: Nhân công */}
                            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                              <div className="text-[11px] font-bold text-amber-400 mb-1">1. Nhân công</div>
                              <div className="space-y-1 font-mono text-[11px]">
                                {tt.field && (
                                  <div className="flex justify-between text-slate-300">
                                    <span>Ngoại ({tt.field.dinh_bien}):</span>
                                    <strong className="text-amber-300">{(Number(tt.field.dinh_muc_cong || 0) * N).toFixed(2)} công</strong>
                                  </div>
                                )}
                                {tt.lab && (
                                  <div className="flex justify-between text-slate-300">
                                    <span>Nội ({tt.lab.dinh_bien}):</span>
                                    <strong className="text-purple-300">{(Number(tt.lab.dinh_muc_cong || 0) * N).toFixed(2)} công</strong>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Bảng 2: Dụng cụ */}
                            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                              <div className="text-[11px] font-bold text-blue-400 mb-1">2. Dụng cụ ({((tt.field?.tools?.length || 0) + (tt.lab?.tools?.length || 0))} mục)</div>
                              <div className="text-slate-400 text-[11px]">
                                {((tt.field?.tools?.length || 0) + (tt.lab?.tools?.length || 0)) > 0 ? (
                                  <span>BHLĐ, dụng cụ đo, bình chứa mẫu theo định mức TT20.</span>
                                ) : (
                                  <span className="italic text-slate-600">Không có</span>
                                )}
                              </div>
                            </div>

                            {/* Bảng 3: Thiết bị */}
                            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                              <div className="text-[11px] font-bold text-indigo-400 mb-1">3. Thiết bị ({((tt.field?.equipment?.length || 0) + (tt.lab?.equipment?.length || 0))} mục)</div>
                              <div className="text-slate-400 text-[11px]">
                                {((tt.field?.equipment?.length || 0) + (tt.lab?.equipment?.length || 0)) > 0 ? (
                                  <span>Máy đo hiện trường, tủ sấy, cân phân tích, điện năng.</span>
                                ) : (
                                  <span className="italic text-slate-600">Không có</span>
                                )}
                              </div>
                            </div>

                            {/* Bảng 4: Vật liệu */}
                            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                              <div className="text-[11px] font-bold text-emerald-400 mb-1">4. Vật liệu ({((tt.field?.materials?.length || 0) + (tt.lab?.materials?.length || 0))} mục)</div>
                              <div className="text-slate-400 text-[11px]">
                                {((tt.field?.materials?.length || 0) + (tt.lab?.materials?.length || 0)) > 0 ? (
                                  <span>Hóa chất, thuốc thử, giấy lọc, chất bảo quản.</span>
                                ) : (
                                  <span className="italic text-slate-600">Không có</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
