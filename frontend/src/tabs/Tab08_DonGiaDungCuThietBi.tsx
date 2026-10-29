import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { 
  Wrench, Cpu, Search, X, Save, FileSpreadsheet, 
  CheckCircle2, Eye, ShieldCheck, 
  ExternalLink, Zap
} from 'lucide-react';
import type { ToolPriceItem, EquipmentPriceItem, PaktItem } from '../types';

interface Tab08Props {
  paktItems: PaktItem[];
  onSelectDrawerItem?: (item: PaktItem) => void;
}

export const Tab08_DonGiaDungCuThietBi: React.FC<Tab08Props> = ({ paktItems, onSelectDrawerItem }) => {
  const [subTab, setSubTab] = useState<'tools' | 'equipment'>('tools');
  const [tools, setTools] = useState<ToolPriceItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentPriceItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'filled' | 'pending'>('all');
  const [selectedToolForDetail, setSelectedToolForDetail] = useState<ToolPriceItem | null>(null);
  const [selectedEqForDetail, setSelectedEqForDetail] = useState<EquipmentPriceItem | null>(null);
  const [saveToast, setSaveToast] = useState<string | null>(null);

  // 1. Fetch dữ liệu tra cứu MSC cho Dụng cụ và Thiết bị
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [toolsRes, eqRes] = await Promise.allSettled([
        fetch('/api/msc-lookup/tools'),
        fetch('/api/msc-lookup/equipment')
      ]);

      if (toolsRes.status === 'fulfilled' && toolsRes.value.ok) {
        const d = await toolsRes.value.json();
        setTools(d.items || []);
      } else {
        const fbTools = await fetch('/msc_lookup_tools.json');
        const d = await fbTools.json();
        setTools(d.items || []);
      }

      if (eqRes.status === 'fulfilled' && eqRes.value.ok) {
        const d = await eqRes.value.json();
        setEquipment(d.items || []);
      } else {
        const fbEq = await fetch('/msc_lookup_equipment.json');
        const d = await fbEq.json();
        setEquipment(d.items || []);
      }
    } catch (err) {
      console.warn('Backend not responding for MSC lookup, trying static fallback:', err);
      try {
        const [fbTools, fbEq] = await Promise.all([
          fetch('/msc_lookup_tools.json'),
          fetch('/msc_lookup_equipment.json')
        ]);
        const dTools = await fbTools.json();
        const dEq = await fbEq.json();
        setTools(dTools.items || []);
        setEquipment(dEq.items || []);
      } catch (fbErr) {
        console.error('All data loading failed:', fbErr);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 2. Cập nhật giá Dụng cụ
  const handleUpdateTool = (id: string, field: keyof ToolPriceItem, value: any) => {
    setTools(prev => prev.map(t => {
      if (t.id === id) {
        const updated = { ...t, [field]: value };
        if (field === 'msc_original_price') {
          const orig = Math.max(0, Number(value) || 0);
          const shiftRate = Math.round((orig / (t.standard_shifts || 264.0)) * 1.10);
          updated.msc_original_price = orig;
          updated.shift_unit_price = shiftRate;
          updated.total_amount = Math.round(t.total_shifts * shiftRate);
        }
        return updated;
      }
      return t;
    }));
  };

  // 3. Cập nhật giá Thiết bị ca máy
  const handleUpdateEquipment = (id: string, field: keyof EquipmentPriceItem, value: any) => {
    setEquipment(prev => prev.map(e => {
      if (e.id === id) {
        const updated = { ...e, [field]: value };
        if (field === 'msc_original_price') {
          const orig = Math.max(0, Number(value) || 0);
          const deprec = Math.round(orig / ((e.deprec_years || 5.0) * (e.annual_shifts || 500.0)));
          const maint = Math.round((0.04 * orig) / (e.annual_shifts || 500.0));
          const power = Math.round(e.power_kw * 8.0 * 2100.0);
          const totalRate = deprec + maint + power;
          updated.msc_original_price = orig;
          updated.deprec_per_shift = deprec;
          updated.maint_per_shift = maint;
          updated.power_cost_per_shift = power;
          updated.shift_unit_rate = totalRate;
          updated.total_amount = Math.round(e.total_shifts * totalRate);
        }
        return updated;
      }
      return e;
    }));
  };

  // 4. Lưu CSDL Tra cứu MSC vào Backend & OneDrive
  const handleSaveAll = async () => {
    setIsSaving(true);
    try {
      await Promise.all([
        fetch('/api/msc-lookup/tools', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ metadata: { total: tools.length, last_updated: new Date().toISOString() }, items: tools })
        }),
        fetch('/api/msc-lookup/equipment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ metadata: { total: equipment.length, last_updated: new Date().toISOString() }, items: equipment })
        })
      ]);
      setSaveToast('Đã lưu thành công CSDL Tra cứu Mua sắm công vào hệ thống!');
      setTimeout(() => setSaveToast(null), 4000);
    } catch (err) {
      console.error('Failed to save to backend:', err);
      alert('Lỗi lưu CSDL. Vui lòng kiểm tra API backend.');
    } finally {
      setIsSaving(false);
    }
  };

  // 5. KPI Tổng hợp
  const kpis = useMemo(() => {
    const totalToolsCost = tools.reduce((acc, t) => acc + (t.total_amount || 0), 0);
    const totalEqCost = equipment.reduce((acc, e) => acc + (e.total_amount || 0), 0);
    const totalPowerCost = equipment.reduce((acc, e) => acc + (e.total_kwh * 2100), 0);
    const totalKwh = equipment.reduce((acc, e) => acc + e.total_kwh, 0);

    const toolsFilled = tools.filter(t => t.msc_tbmt_code && t.msc_tbmt_code.trim()).length;
    const eqFilled = equipment.filter(e => e.msc_tbmt_code && e.msc_tbmt_code.trim()).length;

    return {
      totalToolsCount: tools.length,
      totalToolsCost,
      toolsFilled,
      totalEqCount: equipment.length,
      totalEqCost,
      eqFilled,
      totalPowerCost: Math.round(totalPowerCost),
      totalKwh: Math.round(totalKwh),
      combinedTotal: totalToolsCost + totalEqCost
    };
  }, [tools, equipment]);

  // 6. Danh sách lọc Dụng cụ
  const filteredTools = useMemo(() => {
    return tools.filter(t => {
      if (statusFilter === 'filled' && (!t.msc_tbmt_code || !t.msc_tbmt_code.trim())) return false;
      if (statusFilter === 'pending' && t.msc_tbmt_code && t.msc_tbmt_code.trim()) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const mName = t.name.toLowerCase().includes(q);
        const mId = t.id.toLowerCase().includes(q);
        const mTbmt = (t.msc_tbmt_code || '').toLowerCase().includes(q);
        const mContractor = (t.msc_contractor || '').toLowerCase().includes(q);
        if (!mName && !mId && !mTbmt && !mContractor) return false;
      }
      return true;
    });
  }, [tools, statusFilter, searchQuery]);

  // 7. Danh sách lọc Thiết bị
  const filteredEquipment = useMemo(() => {
    return equipment.filter(e => {
      if (statusFilter === 'filled' && (!e.msc_tbmt_code || !e.msc_tbmt_code.trim())) return false;
      if (statusFilter === 'pending' && e.msc_tbmt_code && e.msc_tbmt_code.trim()) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const mName = e.name.toLowerCase().includes(q);
        const mId = e.id.toLowerCase().includes(q);
        const mTbmt = (e.msc_tbmt_code || '').toLowerCase().includes(q);
        const mContractor = (e.msc_contractor || '').toLowerCase().includes(q);
        if (!mName && !mId && !mTbmt && !mContractor) return false;
      }
      return true;
    });
  }, [equipment, statusFilter, searchQuery]);

  // 8. Tra cứu ngược thông số sử dụng Dụng cụ đang chọn
  const paramsUsingSelectedTool = useMemo(() => {
    if (!selectedToolForDetail) return [];
    const targetName = selectedToolForDetail.name.trim().toLowerCase();
    const result: { item: PaktItem; normPerSample: number; totalShifts: number }[] = [];

    paktItems.forEach(pakt => {
      const N = pakt.so_luong_mau || 1;
      const tt = pakt.tt20_data;
      if (!tt) return;

      let foundNorm = 0;
      for (const k of ['field', 'lab', 'single'] as const) {
        const sub = tt[k];
        if (sub && sub.tools) {
          for (const t of sub.tools) {
            const rawName = String(t.name || '').trim();
            const rawUnit = String(t.unit || '').trim();
            const toolName = /^\d+$/.test(rawName) ? rawUnit : rawName;
            if (toolName.trim().toLowerCase() === targetName) {
              const stdShifts = selectedToolForDetail.standard_shifts || 264.0;
              foundNorm += (1.0 / stdShifts) * 1.10;
            }
          }
        }
      }

      if (foundNorm > 0) {
        result.push({
          item: pakt,
          normPerSample: Number(foundNorm.toFixed(6)),
          totalShifts: Number((foundNorm * N).toFixed(4))
        });
      }
    });

    return result;
  }, [selectedToolForDetail, paktItems]);

  // 9. Tra cứu ngược thông số sử dụng Thiết bị đang chọn
  const paramsUsingSelectedEq = useMemo(() => {
    if (!selectedEqForDetail) return [];
    const targetName = selectedEqForDetail.name.trim().toLowerCase();
    const result: { item: PaktItem; normShift: number; totalShifts: number; totalKwh: number }[] = [];

    paktItems.forEach(pakt => {
      const N = pakt.so_luong_mau || 1;
      const tt = pakt.tt20_data;
      if (!tt) return;

      let foundNorm = 0;
      for (const k of ['field', 'lab', 'single'] as const) {
        const sub = tt[k];
        if (sub && sub.equipment) {
          for (const e of sub.equipment) {
            if (String(e.name || '').trim().toLowerCase() === targetName) {
              foundNorm += Number(e.norm || 0);
            }
          }
        }
      }

      if (foundNorm > 0) {
        const totS = foundNorm * N;
        result.push({
          item: pakt,
          normShift: foundNorm,
          totalShifts: Number(totS.toFixed(4)),
          totalKwh: Number((selectedEqForDetail.power_kw * 8.0 * totS).toFixed(2))
        });
      }
    });

    return result;
  }, [selectedEqForDetail, paktItems]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 bg-slate-950">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></span>
          <span className="text-sm font-medium">Đang tải CSDL Tra Cứu Mua Sắm Công (Dụng cụ & Thiết bị)...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950 text-slate-100">
      {/* 1. Header & Filter Toolbar */}
      <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center space-x-2">
          {/* Sub-tab switch */}
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => setSubTab('tools')}
              className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${
                subTab === 'tools'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Wrench className="w-3.5 h-3.5" />
              <span>Dụng Cụ & BHLĐ ({tools.length})</span>
            </button>
            <button
              onClick={() => setSubTab('equipment')}
              className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${
                subTab === 'equipment'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>Thiết Bị & Ca Máy ({equipment.length})</span>
            </button>
          </div>

          {/* Status filter */}
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-2.5 py-1 rounded ${statusFilter === 'all' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setStatusFilter('filled')}
              className={`px-2.5 py-1 rounded ${statusFilter === 'filled' ? 'bg-emerald-950 text-emerald-300 font-bold border border-emerald-800/60' : 'text-slate-400 hover:text-white'}`}
            >
              Đã có mã MSC
            </button>
            <button
              onClick={() => setStatusFilter('pending')}
              className={`px-2.5 py-1 rounded ${statusFilter === 'pending' ? 'bg-amber-950 text-amber-300 font-bold border border-amber-800/60' : 'text-slate-400 hover:text-white'}`}
            >
              Chưa tra cứu
            </button>
          </div>
        </div>

        {/* Search Input */}
        <div className="flex-1 max-w-sm relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={subTab === 'tools' ? "Tìm theo tên dụng cụ, mã DC, TBMT..." : "Tìm theo tên thiết bị, công suất, TBMT..."}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-8 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="absolute right-2.5 top-2.5 text-slate-500 hover:text-white">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Actions: Download Excel & Save */}
        <div className="flex items-center space-x-2">
          <a
            href="/DANH_MUC_TRA_CUU_MUA_SAM_CONG_2026.xlsx"
            download="DANH_MUC_TRA_CUU_MUA_SAM_CONG_2026.xlsx"
            className="px-2.5 py-1.5 bg-blue-900/40 hover:bg-blue-800/60 text-blue-200 border border-blue-700/50 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition active:scale-95 shadow-sm"
            title="Tải tệp Excel 3 Sheet chứa sẵn công thức phục vụ tra cứu Mua sắm công"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-blue-400" />
            <span>Tải Excel Tra Cứu</span>
          </a>

          <button
            onClick={handleSaveAll}
            disabled={isSaving}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-600/30 transition active:scale-95 flex items-center space-x-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Đang lưu...' : 'Lưu CSDL'}</span>
          </button>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2.5 p-3 bg-slate-900/60 border-b border-slate-800 text-xs shrink-0">
        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
            <Wrench className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Chi Phí Dụng Cụ (CDC)</div>
            <div className="text-sm font-bold text-emerald-300 tabular-nums">
              {kpis.totalToolsCost.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-slate-400">đ</span>
            </div>
            <div className="text-[10px] text-slate-500">
              Đã tra cứu: {kpis.toolsFilled}/{kpis.totalToolsCount}
            </div>
          </div>
        </div>

        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-purple-500/20 text-purple-400 flex items-center justify-center shrink-0">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Chi Phí Ca Máy (CTB)</div>
            <div className="text-sm font-bold text-purple-300 tabular-nums">
              {kpis.totalEqCost.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-slate-400">đ</span>
            </div>
            <div className="text-[10px] text-slate-500">
              Đã tra cứu: {kpis.eqFilled}/{kpis.totalEqCount}
            </div>
          </div>
        </div>

        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Tiền Điện Phòng Lab</div>
            <div className="text-sm font-bold text-amber-300 tabular-nums">
              {kpis.totalPowerCost.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-slate-400">đ</span>
            </div>
            <div className="text-[10px] text-slate-500">
              {kpis.totalKwh.toLocaleString('vi-VN')} kWh @ 2.100 đ
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-950/60 to-indigo-950/60 border border-blue-500/40 rounded-lg p-2.5 flex items-center space-x-2.5 shadow-sm">
          <div className="w-8 h-8 rounded-md bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-md">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-blue-300">Tổng CDC + CTB Toàn Gói</div>
            <div className="text-base font-bold text-white tabular-nums">
              {kpis.combinedTotal.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-blue-200">đ</span>
            </div>
            <div className="text-[10px] text-blue-300/80">
              Cơ sở pháp lý: K4.2 & K4.3 TT20
            </div>
          </div>
        </div>

        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-slate-700 text-slate-300 flex items-center justify-center shrink-0">
            <ExternalLink className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Hệ Thống Mạng Đấu Thầu</div>
            <a
              href="https://muasamcong.mpi.gov.vn"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 hover:underline flex items-center space-x-1 mt-0.5"
            >
              <span>muasamcong.mpi.gov.vn</span>
            </a>
            <div className="text-[10px] text-slate-500">Tra cứu KQLCNT tương tự</div>
          </div>
        </div>
      </div>

      {/* Save Notification Toast */}
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

      {/* 3. Main Data Table */}
      <div className="flex-1 overflow-auto">
        {subTab === 'tools' ? (
          /* ================== TABLE 1: DỤNG CỤ ================== */
          <table className="w-full border-collapse text-left text-xs">
            <thead className="bg-slate-900/95 sticky top-0 z-10 border-b border-slate-800 text-[11px] text-slate-300 font-semibold tracking-wider uppercase select-none">
              <tr>
                <th className="py-2.5 px-2 text-center w-12">STT</th>
                <th className="py-2.5 px-2 w-20">Mã DC</th>
                <th className="py-2.5 px-3 min-w-[200px]">Tên Dụng Cụ / Thiết Bị BHLĐ</th>
                <th className="py-2.5 px-2 text-center w-14">ĐVT</th>
                <th className="py-2.5 px-2 text-center w-20" title="Niên hạn sử dụng tháng theo TT20">Niên Hạn (Tháng)</th>
                <th className="py-2.5 px-2 text-center w-20" title="Số ca chuẩn trong niên hạn = Tm x 22 ca">Ca Chuẩn</th>
                <th className="py-2.5 px-2 text-right w-24" title="Tổng số ca định mức toàn gói thầu (+10% phụ)">Tổng Ca ĐM</th>
                <th className="py-2.5 px-2.5 text-right w-36 bg-blue-950/40 text-blue-300 border-x border-slate-800" title="Nguyên giá mua mới tra cứu trên Mạng đấu thầu quốc gia">
                  Nguyên Giá MSC (đ)
                </th>
                <th className="py-2.5 px-2 w-28" title="Mã Thông Báo Mời Thầu / Kết quả lựa chọn nhà thầu">Mã TBMT</th>
                <th className="py-2.5 px-2 w-24">Ngày Duyệt</th>
                <th className="py-2.5 px-2 min-w-[150px]">Đơn Vị Trúng Thầu</th>
                <th className="py-2.5 px-2.5 text-right w-28 bg-emerald-950/30 text-emerald-300 border-l border-slate-800" title="Đơn giá 1 ca = (Nguyên giá / Ca chuẩn) x 1.10">
                  ĐG 1 Ca (đ/ca)
                </th>
                <th className="py-2.5 px-3 text-right w-32 bg-emerald-950/50 text-emerald-200">Thành Tiền (đ)</th>
                <th className="py-2.5 px-2 text-center w-12">Xem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-normal">
              {filteredTools.length === 0 ? (
                <tr>
                  <td colSpan={14} className="py-12 text-center text-slate-500">
                    Không tìm thấy dụng cụ nào phù hợp với bộ lọc tra cứu.
                  </td>
                </tr>
              ) : (
                filteredTools.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-900/60 transition group">
                    <td className="py-2 px-2 text-center text-slate-500 tabular-nums">{t.stt}</td>
                    <td className="py-2 px-2 font-mono text-[11px] text-slate-400 font-semibold">{t.id}</td>
                    <td className="py-2 px-3 text-slate-200 font-medium">
                      <div className="line-clamp-1">{t.name}</div>
                    </td>
                    <td className="py-2 px-2 text-center text-slate-400 text-[11px]">{t.unit}</td>
                    <td className="py-2 px-2 text-center font-mono tabular-nums text-slate-300">{t.lifespan_months}</td>
                    <td className="py-2 px-2 text-center font-mono tabular-nums text-slate-400">{t.standard_shifts}</td>
                    <td className="py-2 px-2 text-right font-mono tabular-nums font-semibold text-slate-300">
                      {t.total_shifts.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                    </td>
                    {/* Input Nguyên giá MSC */}
                    <td className="py-1.5 px-2 bg-blue-950/20 border-x border-slate-800">
                      <input
                        type="number"
                        value={t.msc_original_price || ''}
                        onChange={(e) => handleUpdateTool(t.id, 'msc_original_price', e.target.value)}
                        placeholder="0"
                        className="w-full text-right bg-slate-900 border border-slate-700/80 rounded px-2 py-1 text-xs text-blue-200 font-mono font-bold focus:outline-none focus:border-blue-400"
                      />
                    </td>
                    {/* Input Mã TBMT */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={t.msc_tbmt_code || ''}
                        onChange={(e) => handleUpdateTool(t.id, 'msc_tbmt_code', e.target.value)}
                        placeholder="Mã TBMT..."
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 font-mono focus:outline-none focus:border-emerald-500"
                      />
                    </td>
                    {/* Input Ngày duyệt */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={t.msc_approval_date || ''}
                        onChange={(e) => handleUpdateTool(t.id, 'msc_approval_date', e.target.value)}
                        placeholder="dd/mm/yyyy"
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 font-mono focus:outline-none focus:border-emerald-500"
                      />
                    </td>
                    {/* Input Đơn vị trúng thầu */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={t.msc_contractor || ''}
                        onChange={(e) => handleUpdateTool(t.id, 'msc_contractor', e.target.value)}
                        placeholder="Nhà thầu..."
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-emerald-500"
                      />
                    </td>
                    {/* Đơn giá 1 ca */}
                    <td className="py-2 px-2.5 text-right font-mono tabular-nums font-bold text-emerald-400 bg-emerald-950/20 border-l border-slate-800">
                      {t.shift_unit_price.toLocaleString('vi-VN')}
                    </td>
                    {/* Thành tiền */}
                    <td className="py-2 px-3 text-right font-mono tabular-nums font-bold text-emerald-300 bg-emerald-950/30">
                      {t.total_amount.toLocaleString('vi-VN')}
                    </td>
                    {/* Xem chi tiết */}
                    <td className="py-2 px-2 text-center">
                      <button
                        onClick={() => setSelectedToolForDetail(t)}
                        className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
                        title="Xem các thông số sử dụng dụng cụ này"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : (
          /* ================== TABLE 2: THIẾT BỊ CA MÁY ================== */
          <table className="w-full border-collapse text-left text-xs">
            <thead className="bg-slate-900/95 sticky top-0 z-10 border-b border-slate-800 text-[11px] text-slate-300 font-semibold tracking-wider uppercase select-none">
              <tr>
                <th className="py-2.5 px-2 text-center w-12">STT</th>
                <th className="py-2.5 px-2 w-20">Mã TB</th>
                <th className="py-2.5 px-3 min-w-[200px]">Tên Máy Móc / Thiết Bị Đo</th>
                <th className="py-2.5 px-2 text-center w-14">ĐVT</th>
                <th className="py-2.5 px-2 text-center w-16" title="Công suất thiết bị tính bằng kW">P (kW)</th>
                <th className="py-2.5 px-2 text-center w-24" title="Ca chuẩn hàng năm theo Khoản 4.3 TT20: 250 đất / 200 biển / 500 lab">Ca Chuẩn</th>
                <th className="py-2.5 px-2 text-right w-24" title="Tổng số ca định mức toàn gói thầu">Tổng Ca ĐM</th>
                <th className="py-2.5 px-2 text-right w-24 text-amber-300" title="Tổng điện năng tiêu thụ (kWh)">Điện (kWh)</th>
                <th className="py-2.5 px-2.5 text-right w-36 bg-blue-950/40 text-blue-300 border-x border-slate-800" title="Nguyên giá mua mới tra cứu trên Mạng đấu thầu quốc gia">
                  Nguyên Giá MSC (đ)
                </th>
                <th className="py-2.5 px-2 w-28">Mã TBMT</th>
                <th className="py-2.5 px-2 w-24">Ngày Duyệt</th>
                <th className="py-2.5 px-2 min-w-[140px]">Đơn Vị Trúng Thầu</th>
                <th className="py-2.5 px-2 text-right w-24 text-slate-400" title="Khấu hao 1 ca = Nguyên giá / (5 năm x Ca chuẩn)">KH 1 Ca</th>
                <th className="py-2.5 px-2.5 text-right w-28 bg-purple-950/30 text-purple-300 border-l border-slate-800" title="Đơn giá 1 ca máy = Khấu hao + Sửa chữa 4% + Tiền điện">
                  ĐG Ca (đ/ca)
                </th>
                <th className="py-2.5 px-3 text-right w-32 bg-purple-950/50 text-purple-200">Thành Tiền (đ)</th>
                <th className="py-2.5 px-2 text-center w-12">Xem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-normal">
              {filteredEquipment.length === 0 ? (
                <tr>
                  <td colSpan={16} className="py-12 text-center text-slate-500">
                    Không tìm thấy thiết bị nào phù hợp với bộ lọc tra cứu.
                  </td>
                </tr>
              ) : (
                filteredEquipment.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-900/60 transition group">
                    <td className="py-2 px-2 text-center text-slate-500 tabular-nums">{e.stt}</td>
                    <td className="py-2 px-2 font-mono text-[11px] text-slate-400 font-semibold">{e.id}</td>
                    <td className="py-2 px-3 text-slate-200 font-medium">
                      <div className="line-clamp-1">{e.name}</div>
                      {e.spec && <div className="text-[10px] text-slate-500 line-clamp-1">{e.spec}</div>}
                    </td>
                    <td className="py-2 px-2 text-center text-slate-400 text-[11px]">{e.unit}</td>
                    <td className="py-2 px-2 text-center font-mono tabular-nums text-slate-300">{e.power_kw || '-'}</td>
                    <td className="py-2 px-2 text-center">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        e.annual_shifts === 250 ? 'bg-blue-950 text-blue-300' :
                        e.annual_shifts === 200 ? 'bg-cyan-950 text-cyan-300' : 'bg-purple-950 text-purple-300'
                      }`}>
                        {e.annual_shifts} ca
                      </span>
                    </td>
                    <td className="py-2 px-2 text-right font-mono tabular-nums font-semibold text-slate-300">
                      {e.total_shifts.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                    </td>
                    <td className="py-2 px-2 text-right font-mono tabular-nums text-amber-300">
                      {e.total_kwh > 0 ? e.total_kwh.toLocaleString('vi-VN') : '-'}
                    </td>
                    {/* Input Nguyên giá MSC */}
                    <td className="py-1.5 px-2 bg-blue-950/20 border-x border-slate-800">
                      <input
                        type="number"
                        value={e.msc_original_price || ''}
                        onChange={(ev) => handleUpdateEquipment(e.id, 'msc_original_price', ev.target.value)}
                        placeholder="0"
                        className="w-full text-right bg-slate-900 border border-slate-700/80 rounded px-2 py-1 text-xs text-blue-200 font-mono font-bold focus:outline-none focus:border-blue-400"
                      />
                    </td>
                    {/* Input Mã TBMT */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={e.msc_tbmt_code || ''}
                        onChange={(ev) => handleUpdateEquipment(e.id, 'msc_tbmt_code', ev.target.value)}
                        placeholder="Mã TBMT..."
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 font-mono focus:outline-none focus:border-purple-500"
                      />
                    </td>
                    {/* Input Ngày duyệt */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={e.msc_approval_date || ''}
                        onChange={(ev) => handleUpdateEquipment(e.id, 'msc_approval_date', ev.target.value)}
                        placeholder="dd/mm/yyyy"
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 font-mono focus:outline-none focus:border-purple-500"
                      />
                    </td>
                    {/* Input Đơn vị trúng thầu */}
                    <td className="py-1.5 px-1.5">
                      <input
                        type="text"
                        value={e.msc_contractor || ''}
                        onChange={(ev) => handleUpdateEquipment(e.id, 'msc_contractor', ev.target.value)}
                        placeholder="Nhà thầu..."
                        className="w-full bg-slate-900 border border-slate-800 rounded px-1.5 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-purple-500"
                      />
                    </td>
                    {/* Khấu hao 1 ca */}
                    <td className="py-2 px-2 text-right font-mono tabular-nums text-slate-400">
                      {e.deprec_per_shift.toLocaleString('vi-VN')}
                    </td>
                    {/* Đơn giá 1 ca máy */}
                    <td className="py-2 px-2.5 text-right font-mono tabular-nums font-bold text-purple-300 bg-purple-950/20 border-l border-slate-800">
                      {e.shift_unit_rate.toLocaleString('vi-VN')}
                    </td>
                    {/* Thành tiền */}
                    <td className="py-2 px-3 text-right font-mono tabular-nums font-bold text-purple-200 bg-purple-950/30">
                      {e.total_amount.toLocaleString('vi-VN')}
                    </td>
                    {/* Xem chi tiết */}
                    <td className="py-2 px-2 text-center">
                      <button
                        onClick={() => setSelectedEqForDetail(e)}
                        className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
                        title="Xem các thông số sử dụng thiết bị này"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* 4. Slide-Over Detail Drawer for Tools */}
      {selectedToolForDetail && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
          <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800/60">
                    {selectedToolForDetail.id}
                  </span>
                  <h3 className="text-sm font-bold text-white">{selectedToolForDetail.name}</h3>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Niên hạn: <strong>{selectedToolForDetail.lifespan_months} tháng</strong> ({selectedToolForDetail.standard_shifts} ca) • Đơn giá: <strong className="text-emerald-400">{selectedToolForDetail.shift_unit_price.toLocaleString('vi-VN')} đ/ca</strong>
                </p>
              </div>
              <button onClick={() => setSelectedToolForDetail(null)} className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
              <div className="text-[11px] font-semibold text-slate-300">
                Có <strong>{paramsUsingSelectedTool.length}</strong> thông số quan trắc sử dụng dụng cụ này:
              </div>
              <div className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden bg-slate-950/60">
                {paramsUsingSelectedTool.map((entry, idx) => (
                  <div
                    key={idx}
                    onClick={() => onSelectDrawerItem && onSelectDrawerItem(entry.item)}
                    className={`p-2.5 flex items-center justify-between hover:bg-slate-800/40 transition ${onSelectDrawerItem ? 'cursor-pointer' : ''}`}
                  >
                    <div>
                      <div className="font-semibold text-white">{entry.item.thong_so}</div>
                      <div className="text-[10px] text-slate-400">
                        {entry.item.khu_vuc} • {entry.item.moi_truong} • Số mẫu N: {entry.item.so_luong_mau}
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-emerald-300 font-bold">{entry.totalShifts.toLocaleString('vi-VN')} ca</div>
                      <div className="text-[10px] text-slate-500">({entry.normPerSample} đm/mẫu)</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 border-t border-slate-800 bg-slate-950 flex justify-end">
              <button onClick={() => setSelectedToolForDetail(null)} className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold">
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Slide-Over Detail Drawer for Equipment */}
      {selectedEqForDetail && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
          <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-800/60">
                    {selectedEqForDetail.id}
                  </span>
                  <h3 className="text-sm font-bold text-white">{selectedEqForDetail.name}</h3>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Ca chuẩn: <strong>{selectedEqForDetail.annual_shifts} ca/năm</strong> • Công suất: <strong>{selectedEqForDetail.power_kw} kW</strong> • Đơn giá 1 ca: <strong className="text-purple-400">{selectedEqForDetail.shift_unit_rate.toLocaleString('vi-VN')} đ/ca</strong>
                </p>
              </div>
              <button onClick={() => setSelectedEqForDetail(null)} className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
              <div className="text-[11px] font-semibold text-slate-300">
                Có <strong>{paramsUsingSelectedEq.length}</strong> thông số quan trắc sử dụng thiết bị này:
              </div>
              <div className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden bg-slate-950/60">
                {paramsUsingSelectedEq.map((entry, idx) => (
                  <div
                    key={idx}
                    onClick={() => onSelectDrawerItem && onSelectDrawerItem(entry.item)}
                    className={`p-2.5 flex items-center justify-between hover:bg-slate-800/40 transition ${onSelectDrawerItem ? 'cursor-pointer' : ''}`}
                  >
                    <div>
                      <div className="font-semibold text-white">{entry.item.thong_so}</div>
                      <div className="text-[10px] text-slate-400">
                        {entry.item.khu_vuc} • {entry.item.moi_truong} • Số mẫu N: {entry.item.so_luong_mau}
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-purple-300 font-bold">{entry.totalShifts.toLocaleString('vi-VN')} ca</div>
                      {entry.totalKwh > 0 && <div className="text-[10px] text-amber-400">{entry.totalKwh.toLocaleString('vi-VN')} kWh</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 border-t border-slate-800 bg-slate-950 flex justify-end">
              <button onClick={() => setSelectedEqForDetail(null)} className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold">
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
