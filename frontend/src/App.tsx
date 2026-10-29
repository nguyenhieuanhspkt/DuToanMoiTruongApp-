import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { HeaderNav } from './components/HeaderNav';
import { SidebarNav } from './components/SidebarNav';
import { FooterNav } from './components/FooterNav';
import { KPICards } from './components/KPICards';
import { ToolbarFilter } from './components/ToolbarFilter';
import { EmptyState } from './components/EmptyState';
import { MultiLevelDrawer } from './components/MultiLevelDrawer';
import { Tab01_KhoiLuong } from './tabs/Tab01_KhoiLuong';
import { Tab02_NhanCong } from './tabs/Tab02_NhanCong';
import { Tab03_VatLieu } from './tabs/Tab03_VatLieu';
import { Tab04_DungCu } from './tabs/Tab04_DungCu';
import { Tab05_ThietBi } from './tabs/Tab05_ThietBi';
import { Tab06_DonGiaNhanCong } from './tabs/Tab06_DonGiaNhanCong';
import { Tab07_DonGiaVatLieu } from './tabs/Tab07_DonGiaVatLieu';
import { Tab08_DonGiaDungCuThietBi } from './tabs/Tab08_DonGiaDungCuThietBi';
import type { PaktItem, FilterState, PricingConfigData } from './types';

export const App: React.FC = () => {
  const [items, setItems] = useState<PaktItem[]>([]);
  const [pricingConfig, setPricingConfig] = useState<PricingConfigData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<number>(1);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [selectedDrawerItem, setSelectedDrawerItem] = useState<PaktItem | null>(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  // Filters State
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    program: 'all',
    plant: 'all',
    environment: 'all',
  });

  const searchInputRef = useRef<HTMLInputElement>(null);

  // 1. Fetch Master Dataset & Pricing Configuration from Local Backend
  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      // Tải song song danh sách công việc và cấu hình đơn giá
      const [paktRes, pricingRes] = await Promise.allSettled([
        fetch('/api/pakt-items'),
        fetch('/api/pricing/labor')
      ]);

      if (paktRes.status === 'fulfilled' && paktRes.value.ok) {
        const data = await paktRes.value.json();
        setItems(data);
      } else {
        const fallbackRes = await fetch('/pakt_253_items.json');
        const fallbackData = await fallbackRes.json();
        setItems(fallbackData);
      }

      if (pricingRes.status === 'fulfilled' && pricingRes.value.ok) {
        const pData = await pricingRes.value.json();
        setPricingConfig(pData);
      }
    } catch (err) {
      console.warn('Backend not responding, attempting fallback fetch:', err);
      try {
        const fallbackRes = await fetch('/pakt_253_items.json');
        const fallbackData = await fallbackRes.json();
        setItems(fallbackData);
      } catch (fbErr) {
        console.error('All data sources failed:', fbErr);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleUpdatePricing = async (newConfig: PricingConfigData): Promise<boolean> => {
    try {
      const res = await fetch('/api/pricing/labor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      if (res.ok) {
        setPricingConfig(newConfig);
        return true;
      }
      return false;
    } catch (e) {
      console.error('Failed to update pricing on backend:', e);
      setPricingConfig(newConfig);
      return true;
    }
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  // 2. Global Keyboard Shortcuts Handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl + F: Focus search
      if (e.ctrlKey && (e.key === 'f' || e.key === 'F')) {
        e.preventDefault();
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
        return;
      }

      // Alt + 1..0: Tab Switch
      if (e.altKey && !e.ctrlKey && !e.shiftKey) {
        if (e.key >= '1' && e.key <= '9') {
          e.preventDefault();
          setActiveTab(Number(e.key));
        } else if (e.key === '0') {
          e.preventDefault();
          setActiveTab(10);
        }
      }

      // Esc: Close Drawer or Clear Search
      if (e.key === 'Escape') {
        if (selectedDrawerItem) {
          setSelectedDrawerItem(null);
        } else if (filters.search) {
          setFilters(prev => ({ ...prev, search: '' }));
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedDrawerItem, filters.search]);

  // 3. Filtered Master Items (Single Source of Truth)
  const filteredItems = useMemo(() => {
    return items.filter((row) => {
      if (filters.program !== 'all' && !row.nhom.includes(filters.program)) return false;
      if (filters.plant !== 'all' && !row.khu_vuc.includes(filters.plant)) return false;
      if (filters.environment !== 'all' && !row.moi_truong.toLowerCase().includes(filters.environment)) return false;

      if (filters.search) {
        const q = filters.search.trim().toLowerCase();
        const mName = row.thong_so.toLowerCase().includes(q);
        const mEnv = row.moi_truong.toLowerCase().includes(q);
        const mCode = (row.ma_gop || '').toLowerCase().includes(q);
        const mLoc = (row.vi_tri || '').toLowerCase().includes(q);
        if (!mName && !mEnv && !mCode && !mLoc) return false;
      }

      return true;
    });
  }, [items, filters]);

  // 4. Calculate Aggregate KPIs from Filtered Items
  const kpis = useMemo(() => {
    let samples = 0;
    let field = 0;
    let lab = 0;

    filteredItems.forEach((row) => {
      if (row.is_header) return;
      const N = row.so_luong_mau || 0;
      samples += N;
      const tt = row.tt20_data;
      if (tt) {
        if (tt.field) field += Number(tt.field.dinh_muc_cong || 0) * 1.2 * N;
        if (tt.lab) lab += Number(tt.lab.dinh_muc_cong || 0) * N;
        if (tt.single) field += Number(tt.single.dinh_muc_cong || 0) * 1.2 * N;
      }
    });

    return {
      totalItems: filteredItems.length,
      totalSamples: samples,
      totalFieldDays: field,
      totalLabDays: lab,
    };
  }, [filteredItems]);

  // 5. Paginated Slice of Items for Table
  const paginatedItems = useMemo(() => {
    if (pageSize === -1) return filteredItems;
    const start = (currentPage - 1) * pageSize;
    return filteredItems.slice(start, start + pageSize);
  }, [filteredItems, currentPage, pageSize]);

  // Reset to Page 1 when filters change
  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setFilters({
      search: '',
      program: 'all',
      plant: 'all',
      environment: 'all',
    });
    setCurrentPage(1);
  };

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col bg-slate-950 text-slate-100 select-none">
      {/* 1. Fixed Header */}
      <HeaderNav onRefresh={loadData} isLoading={isLoading} />

      {/* 2. Middle Body: Sidebar + Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Collapsible Sidebar */}
        <SidebarNav
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(prev => !prev)}
        />

        {/* Right Main Content Area (Viewport-Fit) */}
        <main className="flex-1 flex flex-col overflow-hidden bg-slate-950">
          {/* Top Filter Controls */}
          <ToolbarFilter
            ref={searchInputRef}
            filters={filters}
            onFilterChange={handleFilterChange}
            onClearFilters={handleClearFilters}
          />

          {/* KPI Summary Cards */}
          <KPICards
            totalItems={kpis.totalItems}
            totalSamples={kpis.totalSamples}
            totalFieldDays={kpis.totalFieldDays}
            totalLabDays={kpis.totalLabDays}
          />

          {/* Active Tab Table Display */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {isLoading ? (
              <div className="flex-1 flex items-center justify-center text-slate-400">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></span>
                  <span className="text-sm font-medium">Đang nạp dữ liệu từ CSDL OneDrive...</span>
                </div>
              </div>
            ) : filteredItems.length === 0 ? (
              <EmptyState searchQuery={filters.search} onClearFilters={handleClearFilters} />
            ) : activeTab === 1 ? (
              <Tab01_KhoiLuong
                items={paginatedItems}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 2 ? (
              <Tab02_NhanCong
                items={paginatedItems}
                pricingConfig={pricingConfig}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 3 ? (
              <Tab03_VatLieu
                items={paginatedItems}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 4 ? (
              <Tab04_DungCu
                items={paginatedItems}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 5 ? (
              <Tab05_ThietBi
                items={paginatedItems}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 6 ? (
              <Tab06_DonGiaNhanCong
                items={items}
                pricingConfig={pricingConfig}
                onUpdatePricing={handleUpdatePricing}
              />
            ) : activeTab === 7 ? (
              <Tab07_DonGiaVatLieu
                paktItems={items}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : activeTab === 8 ? (
              <Tab08_DonGiaDungCuThietBi
                paktItems={items}
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-slate-950">
                <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 mb-3 shadow-lg">
                  <span className="font-bold text-lg">{activeTab}</span>
                </div>
                <h3 className="text-base font-bold text-white mb-1">
                  Tab {activeTab}: Sẵn sàng phát triển ở Giai đoạn 2 (Đơn giá & Phí gián tiếp)
                </h3>
                <p className="text-xs text-slate-400 max-w-md">
                  Toàn bộ 5 Tab Định mức Kỹ thuật (Khối lượng, Nhân công, Vật liệu, Dụng cụ, Thiết bị) đã hoàn thành! Tab Đơn giá này sẽ được kết nối ở Giai đoạn tiếp theo.
                </p>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* 3. Fixed Footer with Smart Pagination */}
      <FooterNav
        totalItems={filteredItems.length}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={setCurrentPage}
        onPageSizeChange={setPageSize}
      />

      {/* 4. Multi-Level Slide-Over Drawer */}
      <MultiLevelDrawer
        item={selectedDrawerItem}
        onClose={() => setSelectedDrawerItem(null)}
      />
    </div>
  );
};
