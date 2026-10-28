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
import type { PaktItem, FilterState } from './types';

export const App: React.FC = () => {
  const [items, setItems] = useState<PaktItem[]>([]);
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

  // 1. Fetch Master Dataset from Local Backend
  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/pakt-items');
      if (!res.ok) throw new Error('Failed to fetch from backend');
      const data = await res.json();
      setItems(data);
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
      const N = row.so_luong_mau || 1;
      samples += N;
      const tt = row.tt20_data;
      if (tt) {
        if (tt.field) field += Number(tt.field.dinh_muc_cong || 0) * N;
        if (tt.lab) lab += Number(tt.lab.dinh_muc_cong || 0) * N;
        if (tt.single) field += Number(tt.single.dinh_muc_cong || 0) * N;
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
                onSelectDrawerItem={setSelectedDrawerItem}
              />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-slate-950">
                <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 mb-3 shadow-lg">
                  <span className="font-bold text-lg">{activeTab}</span>
                </div>
                <h3 className="text-base font-bold text-white mb-1">
                  Tab {activeTab}: Sẵn sàng phát triển ở Giai đoạn tiếp theo
                </h3>
                <p className="text-xs text-slate-400 max-w-md">
                  Toàn bộ dữ liệu 253 dòng và CSDL 13 học phần đã sẵn sàng trong Master State. Tab này sẽ được mở rộng ngay sau mốc Baseline v0.1.0!
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
