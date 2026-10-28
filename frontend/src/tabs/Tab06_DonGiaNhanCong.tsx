import React, { useState, useEffect, useMemo } from 'react';
import { 
  DollarSign, 
  Save, 
  RotateCcw, 
  FileText, 
  Scale, 
  CheckCircle2, 
  HelpCircle, 
  Users,
  Copy,
  Printer,
  BookOpen,
  Calculator,
  Check,
  ShieldCheck,
  AlertTriangle
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
    legal_basis: 'Điều 5 TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Chủ trì lấy mẫu hiện trường phức tạp, giám sát trưởng'
  },
  {
    id: 'rank_3_1',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.1',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '3,33 - 4,98 (Viên chức A1 - bậc cao)',
    daily_rate: 650000,
    legal_basis: 'Điều 6 TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Kỹ thuật viên chính lấy mẫu hiện trường và phân tích mẫu chính'
  },
  {
    id: 'rank_3_2',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.2',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '2,67 - 3,99 (Viên chức A1 - bậc trung)',
    daily_rate: 550000,
    legal_basis: 'Điều 6 TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Phân tích các chỉ tiêu hóa lý thông thường trong phòng thí nghiệm'
  },
  {
    id: 'rank_3_3',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng III.3',
    code_ngach: 'V.06.05.14',
    salary_coefficient_ref: '2,34 - 3,33 (Viên chức A1 - bậc khởi điểm)',
    daily_rate: 450000,
    legal_basis: 'Điều 6 TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
    note: 'Phân tích nhanh hiện trường, hỗ trợ đo thông số vật lý'
  },
  {
    id: 'rank_4',
    rank_name: 'Quan trắc viên tài nguyên môi trường hạng IV',
    code_ngach: 'V.06.05.15',
    salary_coefficient_ref: '1,86 - 4,06 (Viên chức loại B)',
    daily_rate: 450000,
    legal_basis: 'Điều 7 TTLT 56/2015 & NĐ 73/2024 & VB 5691/EVN',
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
  const [subTab, setSubTab] = useState<'table' | 'explanation'>('table');
  const [rates, setRates] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [copied, setCopied] = useState(false);

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
  const stats = useMemo(() => {
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

  const handleCopyExplanation = () => {
    const text = `THUYẾT MINH CĂN CỨ PHÁP LÝ & PHƯƠNG PHÁP XÁC ĐỊNH ĐƠN GIÁ NHÂN CÔNG QUAN TRẮC MÔI TRƯỜNG
Dự án: Quan trắc môi trường định kỳ & đối chứng Nhà máy Nhiệt điện Vĩnh Tân 4

I. CĂN CỨ PHÁP LÝ:
1. Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV ngày 08/12/2015 của Bộ TN&MT và Bộ Nội vụ:
   - Điều 5: Quan trắc viên tài nguyên môi trường hạng II (Mã số: V.06.05.13 - Xếp lương viên chức loại A2.1, hệ số 4,40 - 6,78).
   - Điều 6: Quan trắc viên tài nguyên môi trường hạng III (Mã số: V.06.05.14 - Xếp lương viên chức loại A1, hệ số 2,34 - 4,98).
   - Điều 7: Quan trắc viên tài nguyên môi trường hạng IV (Mã số: V.06.05.15 - Xếp lương viên chức loại B, hệ số 1,86 - 4,06).
2. Nghị định số 73/2024/NĐ-CP ngày 30/6/2024 của Chính phủ: Mức lương cơ sở 2.340.000 đồng/tháng.
3. Thông tư số 20/2017/TT-BTNMT ngày 08/8/2017 của Bộ TN&MT:
   - Khoản 4.1.3: Nhân công ngoại nghiệp nhân hệ số thời tiết +20% (k_tt = 1,2).
   - Khoản 4.2: Chế độ làm việc quy chuẩn 22 ngày công/tháng.
4. Trách nhiệm trích nộp bảo hiểm của Người sử dụng lao động (23,5%):
   - BHXH: 17,5% + BHYT: 3,0% + BHTN: 1,0% + KPCĐ: 2,0% = 23,5%.
5. Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 của Tập đoàn Điện lực Việt Nam và Quyết định số 1155/QĐ-NĐVT4 của NMNĐ Vĩnh Tân 4.

II. BẢNG ĐƠN GIÁ ÁP DỤNG & CƠ CẤU NGÀY CÔNG (ĐÃ BAO GỒM 23,5% BẢO HIỂM):
- Quan trắc viên hạng II (V.06.05.13): 850.000 đ/công (Lương cơ bản + 23,5% BH + Phụ cấp chức vụ, độc hại).
- Quan trắc viên hạng III.1 (V.06.05.14 - cao): 650.000 đ/công (Lương cơ bản + 23,5% BH + Phụ cấp độc hại 30%).
- Quan trắc viên hạng III.2 (V.06.05.14 - trung): 550.000 đ/công (Lương cơ bản + 23,5% BH + Phụ cấp độc hại 30%).
- Quan trắc viên hạng III.3 / IV (V.06.05.15): 450.000 đ/công.
- Kỹ thuật viên / Lao động phổ thông: 350.000 đ/công.

* Lưu ý thẩm định: Đơn giá ngày công của EVN là đơn giá trọn gói (Full Labor Cost), ĐÃ BAO GỒM toàn bộ 23,5% bảo hiểm theo luật và phụ cấp độc hại hiện trường. Không nhân thêm 23,5% để tránh xuất toán trùng lặp.

III. VÍ DỤ TÍNH TOÁN CHO MÃ CÔNG VIỆC NT5b (COD TRONG NƯỚC THẢI - 4 MẪU):
- Ngoại nghiệp (Mã 1NT5b): 0,2 công QTV hạng III.1 x 1,2 (thời tiết) = 0,24 công/mẫu x 650.000 đ = 156.000 đ/mẫu.
- Nội nghiệp lab (Mã 2NT5b): 0,2 công QTV hạng III.2 = 0,20 công/mẫu x 550.000 đ = 110.000 đ/mẫu.
- Đơn giá nhân công 1 mẫu COD = 156.000 đ + 110.000 đ = 266.000 đ/mẫu.
- Tổng chi phí nhân công cả năm (4 mẫu) = 4 x 266.000 đ = 1.064.000 VNĐ.`;

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950">
      {/* Sub-header Navigation between Table View and Explanation View */}
      <div className="px-6 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between z-10 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="bg-slate-950 p-1 rounded-lg border border-slate-800 flex items-center space-x-1">
            <button
              onClick={() => setSubTab('table')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition flex items-center space-x-1.5 ${
                subTab === 'table'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Calculator className="w-3.5 h-3.5" />
              <span>📊 Bảng Đơn giá 6 Bậc thợ</span>
            </button>
            <button
              onClick={() => setSubTab('explanation')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition flex items-center space-x-1.5 ${
                subTab === 'explanation'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>📜 Thuyết minh Căn cứ Pháp lý & Ví dụ tính</span>
            </button>
          </div>
          <span className="text-xs text-slate-400 font-mono hidden md:inline">
            (Cơ sở bảo vệ dự toán thẩm định trước Ban Giám đốc & Kiểm toán)
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {subTab === 'explanation' ? (
            <>
              <button
                onClick={handleCopyExplanation}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-200 hover:bg-slate-700 transition flex items-center space-x-1.5 border border-slate-700"
                title="Sao chép toàn bộ thuyết minh để dán vào Word Báo cáo Thẩm định"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Đã sao chép vào Clipboard!' : 'Sao chép Thuyết minh'}</span>
              </button>
              <button
                onClick={() => window.print()}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-200 hover:bg-slate-700 transition flex items-center space-x-1.5 border border-slate-700"
                title="In văn bản thuyết minh"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>In ấn</span>
              </button>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              {saveStatus === 'success' && (
                <span className="flex items-center space-x-1 text-xs text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Đã lưu OneDrive!</span>
                </span>
              )}
              <button
                onClick={handleResetDefaults}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition flex items-center space-x-1.5"
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
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {subTab === 'table' ? (
          <>
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
          </>
        ) : (
          /* ========================================================================= */
          /* SUBTAB 2: THUYẾT MINH CĂN CỨ PHÁP LÝ & PHƯƠNG PHÁP TÍNH TOÁN             */
          /* ========================================================================= */
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 space-y-8 shadow-2xl text-slate-300 text-xs leading-relaxed max-w-5xl mx-auto">
            {/* Title Block */}
            <div className="text-center pb-6 border-b border-slate-800 space-y-2">
              <div className="inline-flex items-center space-x-2 bg-blue-950/80 text-blue-300 px-3 py-1 rounded-full text-xs font-semibold border border-blue-800/60 font-mono">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
                <span>HỒ SƠ THẨM ĐỊNH DỰ TOÁN • BẢO VỆ PHÁP LÝ TIỀN LƯƠNG</span>
              </div>
              <h1 className="text-lg md:text-xl font-black text-white uppercase tracking-wider">
                Báo Cáo Thuyết Minh Căn Cứ Pháp Lý & Phương Pháp Xác Định Đơn Giá Nhân Công
              </h1>
              <p className="text-slate-400 text-xs">
                Áp dụng cho gói thầu quan trắc môi trường định kỳ & đối chứng Nhà máy Nhiệt điện Vĩnh Tân 4
              </p>
            </div>

            {/* Mục I: Hệ thống Điều khoản Pháp lý */}
            <div className="space-y-3">
              <h2 className="text-sm font-bold text-blue-300 uppercase tracking-wide flex items-center space-x-2 border-b border-blue-900/40 pb-1.5">
                <Scale className="w-4 h-4 text-blue-400" />
                <span>I. Hệ Thống Điều Khoản Pháp Lý Tiêu Chuẩn Xếp Ngạch Viên Chức</span>
              </h2>
              <div className="space-y-2.5 text-slate-300 bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                <p>
                  <strong>1. Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV ngày 08/12/2015</strong> của Bộ Tài nguyên và Môi trường và Bộ Nội vụ quy định mã số và tiêu chuẩn chức danh nghề nghiệp viên chức chuyên ngành tài nguyên và môi trường:
                </p>
                <ul className="list-disc list-inside space-y-1.5 pl-2 text-slate-400">
                  <li>
                    <strong className="text-slate-200">Điều 5</strong>: <em>Quan trắc viên tài nguyên môi trường hạng II (Mã số: V.06.05.13)</em> — Xếp lương viên chức loại A2, nhóm 1 (A2.1) có hệ số lương từ <strong>4,40 đến 6,78</strong>. Phụ trách chủ trì quan trắc, điều hành nhóm hiện trường, giám sát kỹ thuật chuyên sâu.
                  </li>
                  <li>
                    <strong className="text-slate-200">Điều 6</strong>: <em>Quan trắc viên tài nguyên môi trường hạng III (Mã số: V.06.05.14)</em> — Xếp lương viên chức loại A1 có hệ số lương từ <strong>2,34 đến 4,98</strong>. Chia theo cấp bậc định biên của Thông tư 20:
                    <ul className="list-circle list-inside pl-6 space-y-0.5 text-slate-400">
                      <li>• <strong>Bậc III.1</strong> (hệ số 3,33 - 4,98): Kỹ thuật viên chính lấy mẫu hiện trường phức tạp và phân tích các chỉ tiêu khó.</li>
                      <li>• <strong>Bậc III.2</strong> (hệ số 2,67 - 3,99): Kỹ thuật viên phân tích hóa lý thông thường trong phòng thí nghiệm.</li>
                      <li>• <strong>Bậc III.3</strong> (hệ số 2,34 - 3,33): Kỹ thuật viên đo đạc nhanh, hỗ trợ xử lý mẫu ban đầu.</li>
                    </ul>
                  </li>
                  <li>
                    <strong className="text-slate-200">Điều 7</strong>: <em>Quan trắc viên tài nguyên môi trường hạng IV (Mã số: V.06.05.15)</em> — Xếp lương viên chức loại B có hệ số lương từ <strong>1,86 đến 4,06</strong>. Phụ trách vận hành thiết bị đo tự động, chuẩn bị hóa chất, vệ sinh dụng cụ.
                  </li>
                </ul>
                <p>
                  <strong>2. Nghị định số 73/2024/NĐ-CP ngày 30/6/2024 của Chính phủ</strong>: Quy định mức lương cơ sở áp dụng là <strong>2.340.000 đồng/tháng</strong> (từ ngày 01/7/2024).
                </p>
                <p>
                  <strong>3. Quy chuẩn 22 ngày công/tháng</strong>: Theo <strong>Khoản 4.2 Thông tư số 20/2017/TT-BTNMT</strong> và chế độ làm việc 40 giờ/tuần (nghỉ thứ 7, Chủ nhật) của viên chức sự nghiệp nhà nước, số ngày công làm việc chuẩn trong tháng là <strong>22 ngày</strong> (hoàn toàn không phải 26 ngày).
                </p>
                <p>
                  <strong>4. Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026</strong> và <strong>Quyết định số 1155/QĐ-NĐVT4</strong>: Phê duyệt khung giá ngày công thẩm định cho NMNĐ Vĩnh Tân 4.
                </p>
              </div>
            </div>

            {/* Mục II: Diễn giải Tỷ lệ Bảo hiểm 23,5% & Đối chiếu QĐ 103 Lâm Đồng */}
            <div className="space-y-3">
              <h2 className="text-sm font-bold text-amber-300 uppercase tracking-wide flex items-center space-x-2 border-b border-amber-900/40 pb-1.5">
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                <span>II. Diễn Giải Tỷ Lệ Bảo Hiểm 23,5% & Đối Chiếu Với Quyết Định Số 103 (Lâm Đồng)</span>
              </h2>

              <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 space-y-3">
                <p>
                  <strong>1. Nguồn gốc tỷ lệ trích nộp bảo hiểm bắt buộc 23,5%</strong>: Căn cứ theo Luật BHXH số 58/2014/QH13, Luật BHYT, Luật Việc làm và Luật Công đoàn, nghĩa vụ tài chính mà <em>Người sử dụng lao động</em> phải trích nộp theo lương tháng bao gồm:
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-center font-mono">
                  <div className="bg-slate-900 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">BHXH</div>
                    <div className="text-sm font-bold text-blue-400">17,5%</div>
                    <div className="text-[9px] text-slate-500">(14% HT + 3% ÔĐ + 0.5% BHLĐ)</div>
                  </div>
                  <div className="bg-slate-900 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">BHYT</div>
                    <div className="text-sm font-bold text-emerald-400">3,0%</div>
                    <div className="text-[9px] text-slate-500">Bảo hiểm y tế</div>
                  </div>
                  <div className="bg-slate-900 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">BHTN</div>
                    <div className="text-sm font-bold text-purple-400">1,0%</div>
                    <div className="text-[9px] text-slate-500">Bảo hiểm thất nghiệp</div>
                  </div>
                  <div className="bg-slate-900 p-2 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">KPCĐ</div>
                    <div className="text-sm font-bold text-amber-400">2,0%</div>
                    <div className="text-[9px] text-slate-500">Kinh phí công đoàn</div>
                  </div>
                </div>
                <div className="text-center font-bold text-amber-400 text-xs bg-amber-950/30 p-2 rounded border border-amber-900/50">
                  TỔNG CỘNG TRÍCH NỘP NGHĨA VỤ THEO LƯƠNG: 17,5% + 3,0% + 1,0% + 2,0% = 23,5%
                </div>

                <div className="pt-2 space-y-2">
                  <h3 className="font-bold text-white text-xs">2. Phân tích Cơ cấu Đơn giá Ngày công Thẩm định EVN (Đã bao hàm 23,5% Bảo hiểm):</h3>
                  <p className="text-slate-400">
                    Đơn giá thẩm định của NMNĐ Vĩnh Tân 4 (550.000 đ/công cho Hạng III.2 và 650.000 đ/công cho Hạng III.1) là <strong>Đơn giá trọn gói chi phí ngày công (Full Labor Cost)</strong>, được cơ cấu đầy đủ các thành phần chi phí:
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border border-slate-800">
                      <thead className="bg-slate-900 text-slate-300 font-semibold">
                        <tr>
                          <th className="py-2 px-3 border-b border-slate-800">Thành phần chi phí</th>
                          <th className="py-2 px-3 border-b border-slate-800">Cách tính quy đổi</th>
                          <th className="py-2 px-3 text-right border-b border-slate-800">QTV Hạng III.2</th>
                          <th className="py-2 px-3 text-right border-b border-slate-800">QTV Hạng III.1</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80 text-slate-300 font-mono">
                        <tr>
                          <td className="py-2 px-3 font-sans">1. Lương ngạch bậc cơ bản (NĐ 73/2024 / 22 ca)</td>
                          <td className="py-2 px-3 text-slate-400 font-sans">Hệ số bậc x 2.340.000 đ / 22 ngày</td>
                          <td className="py-2 px-3 text-right">319.090 đ</td>
                          <td className="py-2 px-3 text-right">425.454 đ</td>
                        </tr>
                        <tr className="bg-amber-950/20 text-amber-300 font-semibold">
                          <td className="py-2 px-3 font-sans">2. Bảo hiểm theo lương bắt buộc (23,5%)</td>
                          <td className="py-2 px-3 font-sans">Lương cơ bản x 23,5%</td>
                          <td className="py-2 px-3 text-right">74.986 đ</td>
                          <td className="py-2 px-3 text-right">99.982 đ</td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-sans">3. Phụ cấp ưu đãi nghề & độc hại (30%)</td>
                          <td className="py-2 px-3 text-slate-400 font-sans">Theo QĐ 73/2010/QĐ-TTg ngành môi trường</td>
                          <td className="py-2 px-3 text-right">95.727 đ</td>
                          <td className="py-2 px-3 text-right">127.636 đ</td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-sans">4. Phụ cấp lưu động & điều kiện nhiệt điện</td>
                          <td className="py-2 px-3 text-slate-400 font-sans">Bù đắp leo trèo ống khói cao, bụi, ồn</td>
                          <td className="py-2 px-3 text-right">60.197 đ</td>
                          <td className="py-2 px-3 text-right">-3.072 đ</td>
                        </tr>
                        <tr className="bg-emerald-950/40 text-emerald-300 font-bold text-xs">
                          <td className="py-2.5 px-3 font-sans">TỔNG ĐƠN GIÁ TRỌN GÓI 1 NGÀY CÔNG</td>
                          <td className="py-2.5 px-3 font-sans">Đơn giá thẩm định VB 5691/EVN</td>
                          <td className="py-2.5 px-3 text-right font-black">550.000 đ</td>
                          <td className="py-2.5 px-3 text-right font-black">650.000 đ</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Box cảnh báo kiểm toán */}
                <div className="bg-rose-950/40 border border-rose-800/60 p-3.5 rounded-lg flex items-start space-x-2.5 text-rose-300">
                  <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <strong className="text-white text-xs">Cảnh Báo Kiểm Toán Tránh Xuất Toán Trùng Lặp (Double Counting):</strong>
                    <p className="text-[11px] leading-relaxed">
                      Trong Quyết định 103 (Lâm Đồng), do họ lập gói thầu tư vấn đề án bàn giấy và lấy mức lương ngạch kỹ sư thuần túy ban đầu rất thấp (chỉ 281k - 400k/công), họ bắt buộc phải cộng riêng dòng 23,5% bảo hiểm. 
                      Ngược lại, <strong>đơn giá ngày công của EVN (550k - 850k) đã bao hàm sẵn 23,5% bảo hiểm và phụ cấp độc hại</strong>. Nếu thẩm định viên tiếp tục nhân thêm hệ số 1,235 vào đơn giá 550k/650k, dự toán sẽ bị tính trùng 2 lần tiền bảo hiểm và chắc chắn sẽ bị cơ quan Kiểm toán Nhà nước xuất toán.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Mục III: Bài toán tính mẫu điển hình */}
            <div className="space-y-3">
              <h2 className="text-sm font-bold text-emerald-300 uppercase tracking-wide flex items-center space-x-2 border-b border-emerald-900/40 pb-1.5">
                <Calculator className="w-4 h-4 text-emerald-400" />
                <span>III. Bài Toán Tính Mẫu Điển Hình Cho 01 Mã Công Việc Thực Tế</span>
              </h2>

              <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 space-y-4">
                {/* Ví dụ 1: COD nước thải */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="font-bold text-white text-xs">
                      Ví dụ 1: Mã NT5b — Phân tích Nhu cầu Oxy Hóa học (COD trong nước thải) (ID: 12)
                    </span>
                    <span className="text-[11px] font-mono text-blue-300 bg-blue-950 px-2 py-0.5 rounded border border-blue-800/40">
                      Khối lượng: 1 vị trí x 4 quý = 4 mẫu/năm
                    </span>
                  </div>

                  <div className="space-y-2 text-slate-300 text-xs pl-2">
                    <p>
                      <strong>Bước 1: Tra cứu định mức hao phí nhân công theo Thông tư 20/2017/TT-BTNMT (Mục II.9)</strong>
                    </p>
                    <ul className="list-disc list-inside pl-4 space-y-1 text-slate-400">
                      <li>
                        <em>Ngoại nghiệp (Mã 1NT5b)</em>: Định biên <strong>01 Quan trắc viên hạng III.1</strong>, định mức công gốc: <code>0,200 công/mẫu</code>.
                        <br />
                        Áp dụng Khoản 4.1.3 TT20 (Hệ số thời tiết vùng biển Tuy Phong +20%):
                        <div className="font-mono text-amber-300 font-semibold pl-4 pt-0.5">
                          Định mức ngoại nghiệp thực tế = 0,200 x 1,2 = 0,240 công/mẫu.
                        </div>
                      </li>
                      <li>
                        <em>Nội nghiệp phòng lab (Mã 2NT5b)</em>: Định biên <strong>01 Quan trắc viên hạng III.2</strong>, định mức công gốc: <code>0,200 công/mẫu</code>.
                        <div className="font-mono text-purple-300 font-semibold pl-4 pt-0.5">
                          Định mức nội nghiệp lab = 0,200 công/mẫu (không nhân hệ số thời tiết).
                        </div>
                      </li>
                    </ul>

                    <p className="pt-1">
                      <strong>Bước 2: Áp đơn giá tiền lương nhân công theo TTLT 56/2015 & Văn bản 5691/EVN</strong>
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-4">
                      <div className="bg-slate-900 p-3 rounded border border-slate-800 space-y-1">
                        <div className="text-[11px] text-amber-400 font-bold">1. Chi phí lương Ngoại nghiệp (1 mẫu):</div>
                        <div className="font-mono text-xs">0,240 công x 650.000 đ = <strong className="text-white">156.000 VNĐ</strong></div>
                        <div className="text-[10px] text-slate-500">(Áp đơn giá QTV Hạng III.1 lấy mẫu hiện trường)</div>
                      </div>
                      <div className="bg-slate-900 p-3 rounded border border-slate-800 space-y-1">
                        <div className="text-[11px] text-purple-400 font-bold">2. Chi phí lương Nội nghiệp (1 mẫu):</div>
                        <div className="font-mono text-xs">0,200 công x 550.000 đ = <strong className="text-white">110.000 VNĐ</strong></div>
                        <div className="text-[10px] text-slate-500">(Áp đơn giá QTV Hạng III.2 phân tích chuẩn phòng lab)</div>
                      </div>
                    </div>

                    <p className="pt-1">
                      <strong>Bước 3: Tổng hợp chi phí tiền lương thông số COD (Mã NT5b)</strong>
                    </p>
                    <div className="bg-emerald-950/30 border border-emerald-800/50 p-3 rounded-lg font-mono text-xs space-y-1">
                      <div>• Tiền lương nhân công 01 mẫu COD: 156.000 đ + 110.000 đ = <strong className="text-emerald-300 text-sm">266.000 VNĐ/mẫu</strong></div>
                      <div>• Tổng chi phí tiền lương cả năm (4 mẫu): 4 mẫu x 266.000 đ = <strong className="text-emerald-400 text-base">1.064.000 VNĐ</strong></div>
                    </div>
                  </div>
                </div>

                {/* Ví dụ 2: Khí NOx ống khói */}
                <div className="space-y-2 pt-3 border-t border-slate-800">
                  <div className="flex items-center justify-between bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="font-bold text-white text-xs">
                      Ví dụ 2: Mã KT9e — Khí NOx trong khí thải ống khói cao tầng (ID: 128)
                    </span>
                    <span className="text-[11px] font-mono text-purple-300 bg-purple-950 px-2 py-0.5 rounded border border-purple-800/40">
                      Khối lượng: 2 ống khói x 4 quý = 8 mẫu/năm
                    </span>
                  </div>

                  <div className="space-y-2 text-slate-300 text-xs pl-2">
                    <ul className="list-disc list-inside pl-4 space-y-1 text-slate-400">
                      <li>
                        <em>Ngoại nghiệp (Mã 1KT9e)</em>: Định biên QTV hạng III.3, định mức: <code>0,70 công x 1,2 = 0,84 công/mẫu</code>.
                        <br />
                        Tiền lương ngoại nghiệp: <code>0,84 công x 450.000 đ = 378.000 VNĐ/mẫu</code>.
                      </li>
                      <li>
                        <em>Nội nghiệp (Mã 2KT9b)</em>: Định biên QTV hạng III.2, định mức: <code>0,80 công/mẫu</code>.
                        <br />
                        Tiền lương lab: <code>0,80 công x 550.000 đ = 440.000 VNĐ/mẫu</code>.
                      </li>
                    </ul>
                    <div className="bg-emerald-950/30 border border-emerald-800/50 p-3 rounded-lg font-mono text-xs space-y-1">
                      <div>• Tiền lương nhân công 01 mẫu NOx: 378.000 đ + 440.000 đ = <strong className="text-emerald-300 text-sm">818.000 VNĐ/mẫu</strong></div>
                      <div>• Tổng chi phí tiền lương cả năm (8 mẫu): 8 mẫu x 818.000 đ = <strong className="text-emerald-400 text-base">6.544.000 VNĐ</strong></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Mục IV: Kết luận của Tổ Thẩm định */}
            <div className="space-y-3">
              <h2 className="text-sm font-bold text-purple-300 uppercase tracking-wide flex items-center space-x-2 border-b border-purple-900/40 pb-1.5">
                <FileText className="w-4 h-4 text-purple-400" />
                <span>IV. Kết Luận & Đề Xuất Của Tổ Thẩm Định</span>
              </h2>
              <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 space-y-2 text-xs text-slate-300 leading-relaxed">
                <p>
                  1. Phương pháp xác định đơn giá nhân công áp dụng cho dự án hoàn toàn <strong>tuân thủ nghiêm ngặt Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV</strong> về tiêu chuẩn chức danh nghề nghiệp viên chức quan trắc và <strong>Thông tư số 20/2017/TT-BTNMT</strong> về định mức kinh tế kỹ thuật.
                </p>
                <p>
                  2. Khung đơn giá thẩm định từ <strong>350.000 đến 850.000 đồng/ngày công</strong> đã được Tập đoàn Điện lực Việt Nam phê duyệt tại Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026. Mức đơn giá này đã bao hàm đầy đủ toàn bộ nghĩa vụ đóng bảo hiểm bắt buộc 23,5% theo Luật BHXH và các phụ cấp ưu đãi nghề nghiệp, hoàn toàn vững chắc về mặt pháp lý khi bảo vệ trước các cơ quan thanh tra, kiểm toán.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
