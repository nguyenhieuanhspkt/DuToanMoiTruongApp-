import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  Save, 
  RotateCcw, 
  FileText, 
  Scale, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  Users
} from 'lucide-react';
import type { PaktItem, PricingConfigData, LaborRankPricing } from '../types';

interface Tab06DonGiaNhanCongProps {
  items: PaktItem[];
  pricingConfig: PricingConfigData | null;
  onUpdatePricing: (newConfig: PricingConfigData) => Promise<boolean>;
}

export const DEFAULT_LABOR_RANKS: LaborRankPricing[] = [
  {
    id: 'rank_2',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng II',
    code_ngach: 'V.06.05.13',
    salary_coefficient_ref: '4,40 - 6,78 (Viên chức A2.1)',
    daily_rate: 850000,
    legal_basis: 'TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Chủ trì lấy mẫu hiện trường phức tạp, giám sát trưởng'
  },
  {
    id: 'rank_3_1',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.1',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '3,33 - 4,98 (Viên chức A1 - bậc cao)',
    daily_rate: 650000,
    legal_basis: 'TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Kỹ thuật viên chính lấy mẫu hiện trường và phân tích mẫu chính'
  },
  {
    id: 'rank_3_2',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.2',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '2,67 - 3,99 (Viên chức A1 - bậc trung)',
    daily_rate: 550000,
    legal_basis: 'TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Phân tích các chỉ tiêu hóa lý thông thường trong phòng thí nghiệm'
  },
  {
    id: 'rank_3_3',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.3',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '2,34 - 3,33 (Viên chức A1 - bậc khởi điểm)',
    daily_rate: 450000,
    legal_basis: 'TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Phân tích nhanh hiện trường, hỗ trợ đo thông số vật lý'
  },
  {
    id: 'rank_4',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng IV',
    code_ngach: 'V.06.05.15',
    salary_coefficient_ref: '1,86 - 4,06 (Viên chức loại B)',
    daily_rate: 450000,
    legal_basis: 'TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Vận hành máy đo tự động, chuẩn bị dụng cụ hiện trường'
  },
  {
    id: 'rank_ldpt',
    rank_name: 'Kỹ thuật viên / Lao động phổ thông',
    code_ngach: 'Lao động hợp đồng',
    salary_coefficient_ref: 'Lương tối thiểu vùng (Vùng 3/4)',
    daily_rate: 350000,
    legal_basis: 'Nghị định 74/2024/NĐ-CP & VB 5691/EVN',
    note: 'Hỗ trợ bốc xếp, vận chuyển mẫu bảo quản lạnh, hoa tiêu tàu'
  }
];

export const Tab06_DonGiaNhanCong: React.FC<Tab06DonGiaNhanCongProps> = ({
  items,
  pricingConfig,
  onUpdatePricing
}) => {
  const [rates, setRates] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Khởi tạo đơn giá từ config hoặc default
  useEffect(() => {
    if (pricingConfig && pricingConfig.labor_rates) {
      setRates(pricingConfig.labor_rates);
    } else {
      const initial: Record<string, number> = {};
      DEFAULT_LABOR_RANKS.forEach(r => {
        initial[r.rank_name] = r.daily_rate;
      });
      setRates(initial);
    }
  }, [pricingConfig]);

  const handleRateChange = (rankName: string, value: string) => {
    const num = parseInt(value.replace(/\D/g, ''), 10) || 0;
    setRates(prev => ({ ...prev, [rankName]: num }));
    setSaveStatus('idle');
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const newConfig: PricingConfigData = {
        labor_rates: rates,
        currency: 'VND',
        source: 'Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 và Quyết định số 1155/QĐ-NĐVT4',
        legal_bases: [
          'Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV ngày 08/12/2015',
          'Nghị định số 73/2024/NĐ-CP ngày 30/6/2024 (Lương cơ sở 2.340.000 đồng/tháng)',
          'Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 của Tập đoàn Điện lực Việt Nam',
          'Quyết định số 1155/QĐ-NĐVT4 của NMNĐ Vĩnh Tân 4'
        ],
        last_updated: new Date().toISOString()
      };
      const ok = await onUpdatePricing(newConfig);
      setSaveStatus(ok ? 'success' : 'error');
    } catch {
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetDefaults = () => {
    const initial: Record<string, number> = {};
    DEFAULT_LABOR_RANKS.forEach(r => {
      initial[r.rank_name] = r.daily_rate;
    });
    setRates(initial);
    setSaveStatus('idle');
  };

  // Tính toán nhanh tổng chi phí nhân công toàn gói thầu
  const stats = React.useMemo(() => {
    let totalLaborCost = 0;
    let fieldCost = 0;
    let labCost = 0;
    let totalFieldDays = 0;
    let totalLabDays = 0;

    const resolveRate = (rankStr: string): number => {
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

    items.forEach(row => {
      if (row.is_header) return;
      const N = row.so_luong_mau || 0;
      const tt = row.tt20_data;
      if (!tt || N <= 0) return;

      if (tt.field) {
        const fieldDays = Number(tt.field.dinh_muc_cong || 0) * 1.2 * N;
        const rate = resolveRate(tt.field.dinh_bien || '');
        const cost = fieldDays * rate;
        totalFieldDays += fieldDays;
        fieldCost += cost;
        totalLaborCost += cost;
      }
      if (tt.lab) {
        const labDays = Number(tt.lab.dinh_muc_cong || 0) * N;
        const rate = resolveRate(tt.lab.dinh_bien || '');
        const cost = labDays * rate;
        totalLabDays += labDays;
        labCost += cost;
        totalLaborCost += cost;
      }
      if (tt.single) {
        const singleDays = Number(tt.single.dinh_muc_cong || 0) * 1.2 * N;
        const rate = resolveRate(tt.single.dinh_bien || '');
        const cost = singleDays * rate;
        totalFieldDays += singleDays;
        fieldCost += cost;
        totalLaborCost += cost;
      }
    });

    const totalDays = totalFieldDays + totalLabDays;
    const avgRate = totalDays > 0 ? totalLaborCost / totalDays : 0;

    return {
      totalLaborCost,
      fieldCost,
      labCost,
      totalFieldDays,
      totalLabDays,
      totalDays,
      avgRate
    };
  }, [items, rates]);

  return (
    <div className="flex-1 overflow-auto bg-slate-950 p-6 space-y-6">
      {/* 1. Legal Banner */}
      <div className="bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/50 border border-blue-800/40 rounded-xl p-4 shadow-lg">
        <div className="flex items-start space-x-3">
          <Scale className="w-6 h-6 text-blue-400 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <h2 className="text-sm font-bold text-white uppercase tracking-wide flex items-center space-x-2">
              <span>Căn cứ Pháp lý & Tiêu chuẩn Xác định Đơn giá Tiền lương Nhân công</span>
              <span className="bg-blue-900/80 text-blue-300 text-[10px] px-2 py-0.5 rounded-full font-mono border border-blue-700/50">
                TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN
              </span>
            </h2>
            <div className="text-xs text-slate-300 space-y-0.5 leading-relaxed">
              <p>• <strong>Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV</strong>: Quy định mã số và tiêu chuẩn chức danh nghề nghiệp viên chức chuyên ngành tài nguyên và môi trường (Hạng II mã V.06.05.13; Hạng III mã V.06.05.14; Hạng IV mã V.06.05.15).</p>
              <p>• <strong>Nghị định số 73/2024/NĐ-CP</strong>: Mức lương cơ sở áp dụng 2.340.000 đồng/tháng từ ngày 01/7/2024.</p>
              <p>• <strong>Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026</strong> & <strong>Quyết định số 1155/QĐ-NĐVT4</strong>: Hướng dẫn cơ cấu đơn giá ngày công thẩm định cho NMNĐ Vĩnh Tân 4.</p>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Tổng chi phí nhân công</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-black text-emerald-400 font-mono">
            {stats.totalLaborCost.toLocaleString('vi-VN')} <span className="text-xs font-normal text-slate-400">VNĐ</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Ngoại: {stats.fieldCost.toLocaleString('vi-VN')} đ • Nội: {stats.labCost.toLocaleString('vi-VN')} đ
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Tổng ngày công TT20</span>
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2 text-2xl font-black text-blue-400 font-mono">
            {stats.totalDays.toFixed(2)} <span className="text-xs font-normal text-slate-400">công</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Ngoại nghiệp: {stats.totalFieldDays.toFixed(2)} công (+20% TT) • Lab: {stats.totalLabDays.toFixed(2)} công
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Đơn giá bình quân</span>
            <Scale className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 text-2xl font-black text-amber-400 font-mono">
            {Math.round(stats.avgRate).toLocaleString('vi-VN')} <span className="text-xs font-normal text-slate-400">đ/công</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Mức lương ngày công thực tế bình quân
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Lưu trữ cấu hình</span>
            <FileText className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-2 text-sm font-semibold text-purple-300 font-mono truncate" title="OneDrive - EVN/pricing_config.json">
            pricing_config.json
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Đồng bộ 2 chiều với đám mây EVN
          </div>
        </div>
      </div>

      {/* 3. Pricing Table with Inline Editing */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-5 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-sm text-white">Bảng Đơn giá Ngày công Theo Ngạch Bậc Viên chức</span>
            <span className="text-xs text-slate-400 font-mono">(5 bậc ngạch chuẩn + lao động phụ)</span>
          </div>
          <div className="flex items-center space-x-2.5">
            {saveStatus === 'success' && (
              <span className="flex items-center space-x-1 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Đã lưu vào OneDrive!</span>
              </span>
            )}
            {saveStatus === 'error' && (
              <span className="flex items-center space-x-1 text-xs text-rose-400 font-medium">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Lỗi khi lưu cấu hình!</span>
              </span>
            )}
            <button
              onClick={handleResetDefaults}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition flex items-center space-x-1.5"
              title="Khôi phục đơn giá định chuẩn ban đầu"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Mặc định</span>
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-1.5 rounded-lg text-xs font-bold bg-blue-600 text-white hover:bg-blue-500 transition shadow-md flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{isSaving ? 'Đang lưu...' : 'Lưu vào OneDrive'}</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-950/80 text-slate-300 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-3 w-12 text-center">STT</th>
                <th className="py-3 px-4 min-w-[220px]">Chức danh nghề nghiệp (TTLT 56/2015)</th>
                <th className="py-3 px-3 w-28 text-center font-mono">Mã ngạch</th>
                <th className="py-3 px-4 min-w-[180px]">Hệ số lương tham chiếu</th>
                <th className="py-3 px-4 w-44 text-right">Đơn giá áp dụng (VNĐ/công)</th>
                <th className="py-3 px-4 min-w-[200px]">Căn cứ pháp lý & Ghi chú</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {DEFAULT_LABOR_RANKS.map((rank, index) => {
                const currentVal = rates[rank.rank_name] ?? rank.daily_rate;
                return (
                  <tr key={rank.id} className="hover:bg-slate-800/40 transition group">
                    <td className="py-3 px-3 text-center text-slate-500 font-mono">{index + 1}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-white">{rank.rank_name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{rank.note}</div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="font-mono text-[11px] font-semibold text-blue-300 bg-blue-950/70 px-2 py-0.5 rounded border border-blue-800/50">
                        {rank.code_ngach}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                      {rank.salary_coefficient_ref}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <input
                          type="text"
                          value={currentVal.toLocaleString('vi-VN')}
                          onChange={e => handleRateChange(rank.rank_name, e.target.value)}
                          className="w-32 bg-slate-950 border border-slate-700 rounded px-2.5 py-1 text-right font-mono font-bold text-emerald-400 focus:outline-none focus:border-blue-500 text-xs shadow-inner"
                        />
                        <span className="text-[10px] text-slate-500">đ</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] leading-relaxed">
                      <span className="inline-flex items-center space-x-1 text-blue-300/90 font-medium">
                        <Scale className="w-3 h-3 text-blue-400 inline" />
                        <span>{rank.legal_basis}</span>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer info note */}
        <div className="p-4 bg-slate-950/50 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-slate-500" />
            <span>
              Khi thay đổi đơn giá và bấm <strong>"Lưu vào OneDrive"</strong>, toàn bộ các bảng tính tại <strong>Tab 2 (Nhân công)</strong> và <strong>Tab 9 (Tổng hợp dự toán)</strong> sẽ tự động cập nhật ngay lập tức.
            </span>
          </div>
          <div className="text-right font-mono text-slate-500">
            {pricingConfig?.last_updated ? `Cập nhật lần cuối: ${new Date(pricingConfig.last_updated).toLocaleString('vi-VN')}` : 'Đang dùng cấu hình mặc định'}
          </div>
        </div>
      </div>
    </div>
  );
};
