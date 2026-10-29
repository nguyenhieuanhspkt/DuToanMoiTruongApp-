import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { 
  Percent, FileText, Plus, Trash2, Save, RotateCcw, 
  CheckCircle2, ShieldCheck, Scale, Info, Building2,
  Ship, Plane, Truck, Sparkles, X, Calculator
} from 'lucide-react';
import type { OverheadConfigData, SeparateExpenseItem, PaktItem } from '../types';

interface Tab09Props {
  paktItems: PaktItem[];
  pricingConfig?: any;
}

export const Tab09_ChiPhiGianTiep: React.FC<Tab09Props> = ({ paktItems }) => {
  const [activeSubTab, setActiveSubTab] = useState<'overhead' | 'separate' | 'legal'>('overhead');
  const [overheadConfig, setOverheadConfig] = useState<OverheadConfigData>({
    general_overhead_rate: 0.15,
    taxable_income_rate: 0.06,
    contingency_rate: 0.05,
    vat_rate: 0.08,
    multiplier_integrated: 1.3823,
    source: "Quyết định số 80/2026/QĐ-UBND ngày 19/10/2026 & NĐ 24/2024/NĐ-CP",
    separate_expenses: []
  });

  const [expenses, setExpenses] = useState<SeparateExpenseItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveToast, setSaveToast] = useState<string | null>(null);

  // Modal / Form thêm khoản chi phí tính riêng mới
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [newExpense, setNewExpense] = useState<Partial<SeparateExpenseItem>>({
    name: '',
    category: 'khac',
    standard: '',
    unit: 'lần',
    quantity: 1,
    unit_price: 0,
    method: 'Báo giá thị trường (NĐ 24/2024)',
    note: ''
  });

  // 1. Fetch cấu hình chi phí gián tiếp từ backend
  const fetchOverhead = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/overhead-config');
      if (res.ok) {
        const data: OverheadConfigData = await res.json();
        setOverheadConfig(data);
        if (data.separate_expenses && data.separate_expenses.length > 0) {
          setExpenses(data.separate_expenses);
        }
      } else {
        const fbRes = await fetch('/overhead_config.json');
        const fbData: OverheadConfigData = await fbRes.json();
        setOverheadConfig(fbData);
        if (fbData.separate_expenses && fbData.separate_expenses.length > 0) {
          setExpenses(fbData.separate_expenses);
        }
      }
    } catch (err) {
      console.warn('Backend not responding for overhead config, loading static fallback:', err);
      try {
        const fbRes = await fetch('/overhead_config.json');
        const fbData: OverheadConfigData = await fbRes.json();
        setOverheadConfig(fbData);
        if (fbData.separate_expenses && fbData.separate_expenses.length > 0) {
          setExpenses(fbData.separate_expenses);
        }
      } catch (fbErr) {
        console.error('All data sources failed:', fbErr);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverhead();
  }, [fetchOverhead]);

  // 2. Tính toán hệ số tích hợp tự động
  const multiplier = useMemo(() => {
    const k_c = overheadConfig.general_overhead_rate || 0.15;
    const tl = overheadConfig.taxable_income_rate || 0.06;
    const dp = overheadConfig.contingency_rate || 0.05;
    const vat = overheadConfig.vat_rate || 0.08;

    const integrated = (1 + k_c) * (1 + tl) * (1 + dp) * (1 + vat);
    return Number(integrated.toFixed(4));
  }, [
    overheadConfig.general_overhead_rate,
    overheadConfig.taxable_income_rate,
    overheadConfig.contingency_rate,
    overheadConfig.vat_rate
  ]);

  // 3. Tổng chi phí ngoài định mức tính riêng
  const totalSeparateAmount = useMemo(() => {
    return expenses.reduce((acc, it) => acc + (it.total_amount || 0), 0);
  }, [expenses]);

  // 4. Cập nhật tỷ lệ
  const handleRateChange = (field: keyof OverheadConfigData, value: number) => {
    setOverheadConfig(prev => {
      const updated = { ...prev, [field]: value };
      const k_c = field === 'general_overhead_rate' ? value : prev.general_overhead_rate;
      const tl = field === 'taxable_income_rate' ? value : prev.taxable_income_rate;
      const dp = field === 'contingency_rate' ? value : prev.contingency_rate;
      const vat = field === 'vat_rate' ? value : prev.vat_rate;
      updated.multiplier_integrated = Number(((1 + k_c) * (1 + tl) * (1 + dp) * (1 + vat)).toFixed(4));
      return updated;
    });
  };

  // 5. Cập nhật khoản chi phí tính riêng
  const handleUpdateExpense = (id: string, field: keyof SeparateExpenseItem, value: any) => {
    setExpenses(prev => prev.map(it => {
      if (it.id === id) {
        const updated = { ...it, [field]: value };
        if (field === 'quantity' || field === 'unit_price') {
          const q = field === 'quantity' ? Number(value) || 0 : it.quantity;
          const p = field === 'unit_price' ? Number(value) || 0 : it.unit_price;
          updated.total_amount = Math.round(q * p);
        }
        return updated;
      }
      return it;
    }));
  };

  // 6. Xóa khoản chi phí tính riêng
  const handleDeleteExpense = (id: string) => {
    if (confirm('Bạn có chắc chắn muốn xóa khoản chi phí tính riêng này khỏi dự toán?')) {
      setExpenses(prev => prev.filter(it => it.id !== id));
    }
  };

  // 7. Thêm khoản mới
  const handleAddExpenseSubmit = () => {
    if (!newExpense.name || !newExpense.name.trim()) {
      alert('Vui lòng nhập tên khoản chi phí tính riêng!');
      return;
    }
    const q = Number(newExpense.quantity) || 1;
    const p = Number(newExpense.unit_price) || 0;
    const item: SeparateExpenseItem = {
      id: `CPTR_${String(expenses.length + 1).padStart(3, '0')}`,
      name: newExpense.name.trim(),
      category: (newExpense.category as any) || 'khac',
      standard: newExpense.standard || 'Theo hồ sơ dự toán',
      unit: newExpense.unit || 'gói',
      quantity: q,
      unit_price: p,
      total_amount: Math.round(q * p),
      method: newExpense.method || 'Báo giá cạnh tranh',
      note: newExpense.note || ''
    };
    setExpenses(prev => [...prev, item]);
    setShowAddModal(false);
    setNewExpense({
      name: '',
      category: 'khac',
      standard: '',
      unit: 'lần',
      quantity: 1,
      unit_price: 0,
      method: 'Báo giá thị trường (NĐ 24/2024)',
      note: ''
    });
  };

  // 8. Đặt lại mặc định chuẩn 38,23%
  const handleResetDefaults = () => {
    if (confirm('Khôi phục các tỷ lệ gián tiếp về mức chuẩn quy định Nhà nước (+38,23%)?')) {
      setOverheadConfig(prev => ({
        ...prev,
        general_overhead_rate: 0.15,
        taxable_income_rate: 0.06,
        contingency_rate: 0.05,
        vat_rate: 0.08,
        multiplier_integrated: 1.3823
      }));
    }
  };

  // 9. Lưu cấu hình lên Backend & OneDrive
  const handleSaveToBackend = async () => {
    setIsSaving(true);
    try {
      const payload: OverheadConfigData = {
        ...overheadConfig,
        multiplier_integrated: multiplier,
        separate_expenses: expenses
      };

      const res = await fetch('/api/overhead-config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Failed to save overhead config');
      setSaveToast('Đã lưu thành công Chi phí gián tiếp & Chi phí tính riêng vào hệ thống!');
      setTimeout(() => setSaveToast(null), 4000);
    } catch (err) {
      console.error('Error saving overhead:', err);
      alert('Không thể lưu vào backend. Vui lòng kiểm tra API.');
    } finally {
      setIsSaving(false);
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'xay_dung_bxd':
        return <Building2 className="w-4 h-4 text-blue-400" />;
      case 'cong_tac_phi':
        return <Plane className="w-4 h-4 text-emerald-400" />;
      case 'thue_tau_bien':
        return <Ship className="w-4 h-4 text-cyan-400" />;
      case 'van_chuyen_mau':
        return <Truck className="w-4 h-4 text-amber-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 bg-slate-950">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></span>
          <span className="text-sm font-medium">Đang tải Cấu hình Chi phí Gián tiếp & Khoản 4.5 TT20...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950 text-slate-100">
      {/* 1. Header Toolbar */}
      <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center space-x-2">
          {/* Sub-tab navigation */}
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => setActiveSubTab('overhead')}
              className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${
                activeSubTab === 'overhead'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Percent className="w-3.5 h-3.5" />
              <span>Hệ Số Gián Tiếp (+{((multiplier - 1) * 100).toFixed(2)}%)</span>
            </button>
            <button
              onClick={() => setActiveSubTab('separate')}
              className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${
                activeSubTab === 'separate'
                  ? 'bg-amber-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Khoản 4.5 Tính Riêng ({expenses.length} khoản)</span>
            </button>
            <button
              onClick={() => setActiveSubTab('legal')}
              className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${
                activeSubTab === 'legal'
                  ? 'bg-slate-800 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Thuyết Minh Căn Cứ Pháp Lý</span>
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2 text-xs">
          {activeSubTab === 'overhead' && (
            <button
              onClick={handleResetDefaults}
              className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg font-semibold transition active:scale-95 flex items-center space-x-1"
              title="Khôi phục các tỷ lệ chuẩn (+38,23%)"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Mặc Định Chuẩn</span>
            </button>
          )}

          {activeSubTab === 'separate' && (
            <button
              onClick={() => setShowAddModal(true)}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold shadow-md shadow-blue-600/30 transition active:scale-95 flex items-center space-x-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Thêm Khoản Tính Riêng</span>
            </button>
          )}

          <button
            onClick={handleSaveToBackend}
            disabled={isSaving}
            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow-md shadow-emerald-600/30 transition active:scale-95 flex items-center space-x-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Đang lưu...' : 'Lưu Cấu Hình'}</span>
          </button>
        </div>
      </div>

      {/* Save Toast Notification */}
      {saveToast && (
        <div className="bg-emerald-600 text-white text-xs px-4 py-2 flex items-center justify-between shadow-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{saveToast}</span>
          </div>
          <button onClick={() => setSaveToast(null)} className="text-emerald-200 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 p-3 bg-slate-900/60 border-b border-slate-800 text-xs shrink-0">
        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
            <Percent className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Hệ Số Tích Hợp Gián Tiếp (Φ)</div>
            <div className="text-base font-bold text-blue-300 tabular-nums">
              {multiplier.toFixed(4)} <span className="text-xs font-normal text-emerald-400">(+{((multiplier - 1) * 100).toFixed(2)}%)</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <Scale className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Chi Phí Tính Riêng (K4.5 TT20)</div>
            <div className="text-base font-bold text-amber-300 tabular-nums">
              {totalSeparateAmount.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-slate-400">đ</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-purple-500/20 text-purple-400 flex items-center justify-center shrink-0">
            <Building2 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Sàn Giàn Giáo Ống Khói Lò Hơi</div>
            <div className="text-sm font-bold text-purple-300 tabular-nums">
              {(expenses.find(e => e.category === 'xay_dung_bxd')?.total_amount || 280000000).toLocaleString('vi-VN')} đ
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-emerald-950/60 to-teal-950/60 border border-emerald-500/40 rounded-lg p-2.5 flex items-center space-x-2.5 shadow-sm">
          <div className="w-8 h-8 rounded-md bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-md">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-emerald-300">Cơ Sở Pháp Lý Thẩm Định</div>
            <div className="text-xs font-bold text-white truncate max-w-[200px]" title="QĐ 80/2026/QĐ-UBND & K4.5 TT20/2017">
              QĐ 80/2026 & Khoản 4.5 TT20
            </div>
            <div className="text-[10px] text-emerald-300/80">Khép kín 100% hồ sơ pháp lý</div>
          </div>
        </div>
      </div>

      {/* 3. Main Content Views */}
      <div className="flex-1 overflow-auto p-4">
        {activeSubTab === 'overhead' && (
          /* ================== SUB-TAB 1: HỆ SỐ GIÁN TIẾP ================== */
          <div className="max-w-5xl mx-auto space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <Calculator className="w-5 h-5 text-blue-400" />
                    <span>Cấu Thành 4 Tỷ Lệ Chi Phí Gián Tiếp & Thuế (Áp dụng cho {paktItems.length} thông số PAKT)</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Công thức tích hợp: <code className="text-blue-300 bg-slate-950 px-2 py-0.5 rounded font-mono">Φ = (1 + k_chung) × (1 + TL) × (1 + DP) × (1 + VAT)</code>
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Hệ số tích hợp Φ</div>
                  <div className="text-2xl font-black text-blue-400 font-mono tabular-nums">{multiplier.toFixed(4)}</div>
                </div>
              </div>

              {/* 4 Rate Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* 1. Chi phí Quản lý chung */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">1. Chi Phí Chung (k_c)</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">15%</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Tính trên Chi phí trực tiếp <strong className="text-slate-300">T</strong>. Chi trả bộ máy quản lý, văn phòng, kiểm soát an toàn lao động.
                  </p>
                  <div className="flex items-center space-x-2 pt-1">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={overheadConfig.general_overhead_rate}
                      onChange={(e) => handleRateChange('general_overhead_rate', Number(e.target.value))}
                      className="w-24 bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs font-mono font-bold text-blue-300 focus:outline-none focus:border-blue-500"
                    />
                    <span className="text-xs text-slate-400">({(overheadConfig.general_overhead_rate * 100).toFixed(1)}%)</span>
                  </div>
                </div>

                {/* 2. Thu nhập chịu thuế tính trước */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">2. Lợi Nhuận (TL)</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono">6%</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Thu nhập chịu thuế tính trước: tính bằng <strong className="text-slate-300">6% × (T + C_chung)</strong> theo quy định tài chính dịch vụ sự nghiệp công.
                  </p>
                  <div className="flex items-center space-x-2 pt-1">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={overheadConfig.taxable_income_rate}
                      onChange={(e) => handleRateChange('taxable_income_rate', Number(e.target.value))}
                      className="w-24 bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs font-mono font-bold text-emerald-300 focus:outline-none focus:border-emerald-500"
                    />
                    <span className="text-xs text-slate-400">({(overheadConfig.taxable_income_rate * 100).toFixed(1)}%)</span>
                  </div>
                </div>

                {/* 3. Chi phí dự phòng */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">3. Dự Phòng (DP)</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 font-mono">5%</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Dự phòng khối lượng phát sinh và trượt giá: <strong className="text-slate-300">5% × (T + C_chung + TL)</strong>.
                  </p>
                  <div className="flex items-center space-x-2 pt-1">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={overheadConfig.contingency_rate}
                      onChange={(e) => handleRateChange('contingency_rate', Number(e.target.value))}
                      className="w-24 bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs font-mono font-bold text-amber-300 focus:outline-none focus:border-amber-500"
                    />
                    <span className="text-xs text-slate-400">({(overheadConfig.contingency_rate * 100).toFixed(1)}%)</span>
                  </div>
                </div>

                {/* 4. Thuế GTGT */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">4. Thuế VAT</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-950 text-purple-300 font-mono">8%</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Thuế Giá trị gia tăng áp dụng chính sách giảm thuế: <strong className="text-slate-300">8%</strong> (hoặc 10% theo quy định từng thời kỳ).
                  </p>
                  <div className="flex items-center space-x-2 pt-1">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={overheadConfig.vat_rate}
                      onChange={(e) => handleRateChange('vat_rate', Number(e.target.value))}
                      className="w-24 bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs font-mono font-bold text-purple-300 focus:outline-none focus:border-purple-500"
                    />
                    <span className="text-xs text-slate-400">({(overheadConfig.vat_rate * 100).toFixed(1)}%)</span>
                  </div>
                </div>
              </div>

              {/* Ví dụ phân rã chi phí minh họa */}
              <div className="mt-5 p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <div className="font-bold text-white mb-2 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>Ví dụ Tính Thực Tế: Đối với Chi phí Trực tiếp T = 1.000.000.000 đ (1 Tỷ đồng)</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-6 gap-2 pt-2 text-center font-mono">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <div className="text-[10px] text-slate-400 font-sans">Chi phí Trực tiếp T</div>
                    <div className="font-bold text-white mt-1">1.000.000.000 đ</div>
                  </div>
                  <div className="p-2 rounded bg-blue-950/40 border border-blue-900/60">
                    <div className="text-[10px] text-blue-300 font-sans">+15% Quản lý chung</div>
                    <div className="font-bold text-blue-200 mt-1">150.000.000 đ</div>
                  </div>
                  <div className="p-2 rounded bg-emerald-950/40 border border-emerald-900/60">
                    <div className="text-[10px] text-emerald-300 font-sans">+6% Thu nhập trước</div>
                    <div className="font-bold text-emerald-200 mt-1">69.000.000 đ</div>
                  </div>
                  <div className="p-2 rounded bg-amber-950/40 border border-amber-900/60">
                    <div className="text-[10px] text-amber-300 font-sans">+5% Dự phòng</div>
                    <div className="font-bold text-amber-200 mt-1">60.950.000 đ</div>
                  </div>
                  <div className="p-2 rounded bg-purple-950/40 border border-purple-900/60">
                    <div className="text-[10px] text-purple-300 font-sans">+8% Thuế VAT</div>
                    <div className="font-bold text-purple-200 mt-1">102.396.000 đ</div>
                  </div>
                  <div className="p-2 rounded bg-blue-600 text-white shadow-md">
                    <div className="text-[10px] text-blue-100 font-sans font-bold">TỔNG SAU THUẾ</div>
                    <div className="font-black text-white mt-1">1.382.346.000 đ</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeSubTab === 'separate' && (
          /* ================== SUB-TAB 2: KHOẢN 4.5 TÍNH RIÊNG ================== */
          <div className="max-w-6xl mx-auto space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
              <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                    <Scale className="w-4 h-4 text-amber-400" />
                    <span>Danh Mục Chi Phí Ngoài Định Mức Được Lập Dự Toán Riêng (Khoản 4.5 TT20)</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Áp dụng cho các hạng mục giàn giáo ống khói, lưu trú công tác phí, thuê tàu biển và bảo quản chuyển phát mẫu lạnh
                  </p>
                </div>
                <div className="text-right font-mono">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Tổng kinh phí tính riêng</div>
                  <div className="text-lg font-black text-amber-400 tabular-nums">
                    {totalSeparateAmount.toLocaleString('vi-VN')} đ
                  </div>
                </div>
              </div>

              {/* Table of Separate Expenses */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-slate-300 uppercase font-semibold">
                    <tr>
                      <th className="py-2.5 px-3 w-12 text-center">STT</th>
                      <th className="py-2.5 px-3 w-24">Mã</th>
                      <th className="py-2.5 px-3 min-w-[220px]">Nội Dung Khoản Chi Phí Tính Riêng</th>
                      <th className="py-2.5 px-3 min-w-[180px]">Căn Cứ Pháp Lý & Tiêu Chuẩn</th>
                      <th className="py-2.5 px-2 text-center w-20">ĐVT</th>
                      <th className="py-2.5 px-2 text-right w-20">Khối Lượng</th>
                      <th className="py-2.5 px-3 text-right w-32 bg-amber-950/20 text-amber-300">Đơn Giá (đ)</th>
                      <th className="py-2.5 px-3 text-right w-36 bg-amber-950/40 text-amber-200 font-bold">Thành Tiền (đ)</th>
                      <th className="py-2.5 px-2 text-center w-12">Xóa</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-normal">
                    {expenses.length === 0 ? (
                      <tr>
                        <td colSpan={9} className="py-8 text-center text-slate-500">
                          Chưa có khoản chi phí tính riêng nào. Nhấn "Thêm Khoản Tính Riêng" để bổ sung.
                        </td>
                      </tr>
                    ) : (
                      expenses.map((exp, idx) => (
                        <tr key={exp.id} className="hover:bg-slate-800/40 transition group">
                          <td className="py-2.5 px-3 text-center text-slate-500 tabular-nums">{idx + 1}</td>
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400 font-semibold">{exp.id}</td>
                          <td className="py-2.5 px-3 text-white font-medium">
                            <div className="flex items-center space-x-2">
                              {getCategoryIcon(exp.category)}
                              <span>{exp.name}</span>
                            </div>
                            {exp.note && <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{exp.note}</div>}
                          </td>
                          <td className="py-2.5 px-3 text-slate-300">
                            <div className="text-[11px] font-medium">{exp.standard}</div>
                            <div className="text-[10px] text-slate-500">{exp.method}</div>
                          </td>
                          <td className="py-2.5 px-2 text-center text-slate-400">{exp.unit}</td>
                          <td className="py-2 px-2 text-right">
                            <input
                              type="number"
                              value={exp.quantity}
                              onChange={(e) => handleUpdateExpense(exp.id, 'quantity', e.target.value)}
                              className="w-16 bg-slate-950 border border-slate-700 rounded px-1.5 py-1 text-right text-xs font-mono text-white focus:outline-none focus:border-blue-400"
                            />
                          </td>
                          <td className="py-2 px-2 text-right bg-amber-950/10">
                            <input
                              type="number"
                              value={exp.unit_price}
                              onChange={(e) => handleUpdateExpense(exp.id, 'unit_price', e.target.value)}
                              className="w-28 bg-slate-950 border border-slate-700 rounded px-1.5 py-1 text-right text-xs font-mono font-bold text-amber-300 focus:outline-none focus:border-amber-400"
                            />
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono font-bold text-amber-300 tabular-nums bg-amber-950/20">
                            {exp.total_amount.toLocaleString('vi-VN')}
                          </td>
                          <td className="py-2.5 px-2 text-center">
                            <button
                              onClick={() => handleDeleteExpense(exp.id)}
                              className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                              title="Xóa khoản này"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeSubTab === 'legal' && (
          /* ================== SUB-TAB 3: THUYẾT MINH PHÁP LÝ ================== */
          <div className="max-w-4xl mx-auto space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg text-xs leading-relaxed">
              <div className="border-b border-slate-800 pb-3 flex items-center space-x-2">
                <Info className="w-5 h-5 text-blue-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Căn Cứ Pháp Lý Về Chi Phí Gián Tiếp & Phân Hệ Tính Riêng (Khoản 4.5 TT20)
                </h3>
              </div>

              <div className="space-y-3 text-slate-300">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <h4 className="font-bold text-white text-xs mb-1">1. Khoản 4.5 Thông tư 20/2017/TT-BTNMT</h4>
                  <p className="text-slate-400 italic">
                    "Đối với các khoản chi phí chưa được quy định định mức trong Thông tư này (như chi phí đi lại, lưu trú, vận chuyển thiết bị, thuê phương tiện đường thủy, làm giàn giáo, sàn thao tác, kéo điện, mua mẫu...) thì được lập dự toán theo thiết kế kỹ thuật - dự toán được duyệt hoặc theo hóa đơn chứng từ hợp lệ, hợp pháp."
                  </p>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <h4 className="font-bold text-white text-xs mb-1">2. Quyết định số 80/2026/QĐ-UBND ngày 19/10/2026 của UBND TP.HCM</h4>
                  <p className="text-slate-400">
                    Khẳng định định mức kinh tế kỹ thuật hoạt động quan trắc môi trường tuân thủ chuẩn gốc của Bộ TNMT (Thông tư 20/2017). Chi phí quản lý chung áp dụng 15% tính trên chi phí trực tiếp, kết hợp thu nhập chịu thuế tính trước 6% và dự phòng phí 5%.
                  </p>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <h4 className="font-bold text-white text-xs mb-1">3. Thông tư số 12/2021/TT-BXD của Bộ Xây dựng</h4>
                  <p className="text-slate-400">
                    Ban hành Định mức dự toán xây dựng công trình làm căn cứ lập dự toán hạng mục sàn thao tác, giàn giáo trèo cao tại ống khói lò hơi Vĩnh Tân 4 ở độ cao 60m - 210m, lắp đặt mặt bích lấy mẫu 4 inch theo US-EPA Method 1.
                  </p>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <h4 className="font-bold text-white text-xs mb-1">4. Thông tư số 40/2017/TT-BTC của Bộ Tài chính</h4>
                  <p className="text-slate-400">
                    Quy định chế độ công tác phí, chế độ hội nghị. Là căn cứ lập dự toán chi phí vé máy bay/tàu hỏa/xe đưa đón đoàn chuyên gia và phụ cấp lưu trú ăn ở cho các đợt quan trắc ngoại nghiệp tại Tuy Phong, Bình Thuận.
                  </p>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <h4 className="font-bold text-white text-xs mb-1">5. Điều 16 Nghị định số 24/2024/NĐ-CP của Chính phủ</h4>
                  <p className="text-slate-400">
                    Quy định phương pháp xác định giá gói thầu thông qua tối thiểu 03 bảng báo giá cạnh tranh của các nhà cung cấp đối với các dịch vụ đặc thù không có định mức Nhà nước (thuê tàu biển chuyên dụng khảo sát ngoài khơi bãi xỉ Vĩnh Tân, cước chuyển phát nhanh mẫu lạnh hỏa tốc bảo quản 4°C).
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 4. Modal Thêm Khoản Tính Riêng Mới */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Plus className="w-4 h-4 text-blue-400" />
                <span>Thêm Khoản Chi Phí Tính Riêng Mới (Khoản 4.5 TT20)</span>
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Tên nội dung chi phí (*)</label>
                <input
                  type="text"
                  value={newExpense.name}
                  onChange={(e) => setNewExpense({ ...newExpense, name: e.target.value })}
                  placeholder="Ví dụ: Thuê ca-nô khảo sát kênh xả nước làm mát..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Phân loại hạng mục</label>
                  <select
                    value={newExpense.category}
                    onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    <option value="xay_dung_bxd">Giàn giáo / Xây dựng BXD</option>
                    <option value="cong_tac_phi">Công tác phí / Vé máy bay (TT40)</option>
                    <option value="thue_tau_bien">Thuê tàu biển / Ca-nô</option>
                    <option value="van_chuyen_mau">Vận chuyển mẫu lạnh hỏa tốc</option>
                    <option value="khac">Khoản đặc thù khác</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Đơn vị tính</label>
                  <input
                    type="text"
                    value={newExpense.unit}
                    onChange={(e) => setNewExpense({ ...newExpense, unit: e.target.value })}
                    placeholder="đợt, chuyến, ngày tàu, trọn gói..."
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Khối lượng (Số lượng)</label>
                  <input
                    type="number"
                    value={newExpense.quantity}
                    onChange={(e) => setNewExpense({ ...newExpense, quantity: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-mono focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Đơn giá dự toán (VNĐ)</label>
                  <input
                    type="number"
                    value={newExpense.unit_price}
                    onChange={(e) => setNewExpense({ ...newExpense, unit_price: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-amber-300 font-mono font-bold focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Căn cứ pháp lý & Tiêu chuẩn kỹ thuật</label>
                <input
                  type="text"
                  value={newExpense.standard}
                  onChange={(e) => setNewExpense({ ...newExpense, standard: e.target.value })}
                  placeholder="Ví dụ: Thông tư số 40/2017/TT-BTC, 03 Báo giá cạnh tranh..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Ghi chú chi tiết</label>
                <textarea
                  value={newExpense.note}
                  onChange={(e) => setNewExpense({ ...newExpense, note: e.target.value })}
                  placeholder="Mô tả phạm vi thực hiện..."
                  rows={2}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold"
              >
                Hủy Bỏ
              </button>
              <button
                onClick={handleAddExpenseSubmit}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold shadow-md shadow-blue-600/30"
              >
                Lưu Khoản Mới
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
