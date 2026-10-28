import React from 'react';
import { X, Users, Wrench, Cpu, Layers, ShieldAlert } from 'lucide-react';
import type { PaktItem } from '../types';

interface MultiLevelDrawerProps {
  item: PaktItem | null;
  onClose: () => void;
}

export const MultiLevelDrawer: React.FC<MultiLevelDrawerProps> = ({ item, onClose }) => {
  if (!item) return null;

  const tt = item.tt20_data;
  const N = item.so_luong_mau || 1;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-black/40 backdrop-blur-xs transition-opacity animate-in fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-700 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-800 flex items-start justify-between bg-slate-950/60">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30 font-mono">
                Mục #{item.stt} • ID {item.id}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                Mã TT20: {item.ma_gop || '—'}
              </span>
            </div>
            <h2 className="text-base font-bold text-white leading-snug">
              {item.thong_so}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {item.khu_vuc} • {item.moi_truong}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title="Đóng (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-2 p-3 bg-slate-800/60 rounded-lg border border-slate-700/60 font-mono">
            <div>
              <div className="text-[10px] text-slate-400 font-sans uppercase font-bold">Số vị trí x Đợt</div>
              <div className="text-sm font-bold text-slate-200">{item.so_vi_tri} vị trí × {item.so_lan} đợt</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-400 font-sans uppercase font-bold">Tổng Mẫu (N)</div>
              <div className="text-sm font-bold text-blue-400">{N} {item.dvt}</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-400 font-sans uppercase font-bold">Học phần TT20</div>
              <div className="text-sm font-bold text-indigo-400">{item.sec_id || 'Chưa định danh'}</div>
            </div>
          </div>

          {/* If No TT20 data matched */}
          {!tt ? (
            <div className="p-4 bg-amber-950/30 border border-amber-700/40 rounded-lg text-amber-300 flex items-center space-x-2.5">
              <ShieldAlert className="w-5 h-5 shrink-0 text-amber-400" />
              <span>Chưa đối chiếu được thông số chuẩn trong 13 học phần TT20. Cần rà soát bổ sung.</span>
            </div>
          ) : (
            <>
              {/* Bảng 1: Nhân công (Bậc 4 chi tiết) */}
              <div className="bg-slate-800/40 border border-slate-700/70 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2 font-bold text-slate-200 text-xs">
                  <Users className="w-4 h-4 text-amber-400" />
                  <span>BẢNG 1: ĐỊNH MỨC NHÂN CÔNG (BẬC THỢ & NGÀY CÔNG)</span>
                </div>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-[11px]">
                      <th className="py-1.5 font-semibold">Phân loại</th>
                      <th className="py-1.5 font-semibold">Chức danh / Bậc thợ</th>
                      <th className="py-1.5 font-semibold text-right">Định mức/mẫu</th>
                      <th className="py-1.5 font-semibold text-right">Tổng ngày công (×{N})</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    {tt.field && (
                      <tr>
                        <td className="py-1.5 font-sans font-medium text-amber-300">Ngoại nghiệp</td>
                        <td className="py-1.5 font-sans text-slate-300">{tt.field.dinh_bien || 'QTVTNMT'}</td>
                        <td className="py-1.5 text-right text-slate-300">{Number(tt.field.dinh_muc_cong || 0).toFixed(3)}</td>
                        <td className="py-1.5 text-right font-bold text-amber-300">
                          {(Number(tt.field.dinh_muc_cong || 0) * N).toFixed(2)} công
                        </td>
                      </tr>
                    )}
                    {tt.lab && (
                      <tr>
                        <td className="py-1.5 font-sans font-medium text-purple-300">Nội nghiệp (PTN)</td>
                        <td className="py-1.5 font-sans text-slate-300">{tt.lab.dinh_bien || 'QTVTNMT'}</td>
                        <td className="py-1.5 text-right text-slate-300">{Number(tt.lab.dinh_muc_cong || 0).toFixed(3)}</td>
                        <td className="py-1.5 text-right font-bold text-purple-300">
                          {(Number(tt.lab.dinh_muc_cong || 0) * N).toFixed(2)} công
                        </td>
                      </tr>
                    )}
                    {tt.single && (
                      <tr>
                        <td className="py-1.5 font-sans font-medium text-blue-300">Toàn phần</td>
                        <td className="py-1.5 font-sans text-slate-300">{tt.single.dinh_bien || 'QTVTNMT'}</td>
                        <td className="py-1.5 text-right text-slate-300">{Number(tt.single.dinh_muc_cong || 0).toFixed(3)}</td>
                        <td className="py-1.5 text-right font-bold text-blue-300">
                          {(Number(tt.single.dinh_muc_cong || 0) * N).toFixed(2)} công
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Bảng 2: Dụng cụ */}
              <div className="bg-slate-800/40 border border-slate-700/70 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2 font-bold text-slate-200 text-xs">
                  <Wrench className="w-4 h-4 text-blue-400" />
                  <span>BẢNG 2: DỤNG CỤ & BẢO HỘ LAO ĐỘNG</span>
                </div>
                {((tt.field?.tools?.length || 0) + (tt.lab?.tools?.length || 0) + (tt.single?.tools?.length || 0)) === 0 ? (
                  <div className="text-slate-500 italic py-1">Không quy định dụng cụ riêng cho thông số này.</div>
                ) : (
                  <div className="max-h-40 overflow-y-auto pr-1">
                    <table className="w-full text-left border-collapse text-[11px]">
                      <thead>
                        <tr className="border-b border-slate-700 text-slate-400">
                          <th className="py-1">Tên Dụng cụ</th>
                          <th className="py-1">ĐVT</th>
                          <th className="py-1 text-right">Định mức/mẫu</th>
                          <th className="py-1 text-right">Tổng (×{N})</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 font-mono">
                        {[...(tt.field?.tools || []), ...(tt.lab?.tools || []), ...(tt.single?.tools || [])].map((tc, idx) => (
                          <tr key={idx}>
                            <td className="py-1 font-sans text-slate-300">{tc.name}</td>
                            <td className="py-1 font-sans text-slate-400">{tc.unit}</td>
                            <td className="py-1 text-right text-slate-300">{tc.norm}</td>
                            <td className="py-1 text-right text-blue-300 font-bold">{(tc.norm * N).toFixed(4)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Bảng 3: Thiết bị máy móc */}
              <div className="bg-slate-800/40 border border-slate-700/70 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2 font-bold text-slate-200 text-xs">
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <span>BẢNG 3: MÁY MÓC, THIẾT BỊ & ĐIỆN NĂNG</span>
                </div>
                {((tt.field?.equipment?.length || 0) + (tt.lab?.equipment?.length || 0) + (tt.single?.equipment?.length || 0)) === 0 ? (
                  <div className="text-slate-500 italic py-1">Không quy định máy móc thiết bị riêng cho thông số này.</div>
                ) : (
                  <div className="max-h-40 overflow-y-auto pr-1">
                    <table className="w-full text-left border-collapse text-[11px]">
                      <thead>
                        <tr className="border-b border-slate-700 text-slate-400">
                          <th className="py-1">Tên Thiết bị</th>
                          <th className="py-1">ĐVT</th>
                          <th className="py-1 text-right">Định mức/mẫu</th>
                          <th className="py-1 text-right">Tổng ca máy (×{N})</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 font-mono">
                        {[...(tt.field?.equipment || []), ...(tt.lab?.equipment || []), ...(tt.single?.equipment || [])].map((eq, idx) => (
                          <tr key={idx}>
                            <td className="py-1 font-sans text-slate-300">{eq.name}</td>
                            <td className="py-1 font-sans text-slate-400">{eq.unit}</td>
                            <td className="py-1 text-right text-slate-300">{eq.norm}</td>
                            <td className="py-1 text-right text-indigo-300 font-bold">{(eq.norm * N).toFixed(4)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Bảng 4: Vật liệu hóa chất */}
              <div className="bg-slate-800/40 border border-slate-700/70 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2 font-bold text-slate-200 text-xs">
                  <Layers className="w-4 h-4 text-emerald-400" />
                  <span>BẢNG 4: VẬT LIỆU, HÓA CHẤT & THUỐC THỬ</span>
                </div>
                {((tt.field?.materials?.length || 0) + (tt.lab?.materials?.length || 0) + (tt.single?.materials?.length || 0)) === 0 ? (
                  <div className="text-slate-500 italic py-1">Không quy định hóa chất vật liệu riêng cho thông số này.</div>
                ) : (
                  <div className="max-h-40 overflow-y-auto pr-1">
                    <table className="w-full text-left border-collapse text-[11px]">
                      <thead>
                        <tr className="border-b border-slate-700 text-slate-400">
                          <th className="py-1">Tên Vật liệu / Hóa chất</th>
                          <th className="py-1">ĐVT</th>
                          <th className="py-1 text-right">Định mức/mẫu</th>
                          <th className="py-1 text-right">Tổng vật liệu (×{N})</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 font-mono">
                        {[...(tt.field?.materials || []), ...(tt.lab?.materials || []), ...(tt.single?.materials || [])].map((mat, idx) => (
                          <tr key={idx}>
                            <td className="py-1 font-sans text-slate-300">{mat.name}</td>
                            <td className="py-1 font-sans text-slate-400">{mat.unit}</td>
                            <td className="py-1 text-right text-slate-300">{mat.norm}</td>
                            <td className="py-1 text-right text-emerald-300 font-bold">{(mat.norm * N).toFixed(4)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};
