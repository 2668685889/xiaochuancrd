import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import MainLayout from './components/layout/MainLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ProductPage from './pages/ProductPage';
import ProductCategoryPage from './pages/ProductCategoryPage';
import ProductModelPage from './pages/ProductModelPage';
import ProductModelDeleteTestPage from './pages/ProductModelDeleteTestPage';
import SupplierPage from './pages/SupplierPage';
import InventoryPage from './pages/InventoryPage';
import PurchaseOrderPage from './pages/PurchaseOrderPage';
import PurchaseOrderDetailPage from './pages/PurchaseOrderDetailPage';
import SalesOrderPage from './pages/SalesOrderPage';
import SalesOrderDetailPage from './pages/SalesOrderDetailPage';
import CustomerPage from './pages/CustomerPage';
import CustomerDetailPage from './pages/CustomerDetailPage';
import ReportPage from './pages/ReportPage';
import SettingsPage from './pages/SettingsPage';
import UserPage from './pages/UserPage';
import OperationLogsPage from './pages/operation-logs/OperationLogsPage';
import CozeUploadPage from './pages/coze/CozeUploadPage';
import AuthDebugPage from './pages/AuthDebugPage';
import SmartAssistantPage from './pages/SmartAssistantPage';

// 路由保护组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// 公开路由组件（已登录用户重定向到仪表盘）
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        {/* Toast通知组件 */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
        
        <Routes>
          {/* 公开路由 */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } 
          />
          
          {/* 受保护的路由 */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="products" element={<ProductPage />} />
            <Route path="product-categories" element={<ProductCategoryPage />} />
            <Route path="product-models" element={<ProductModelPage />} />
            <Route path="product-models-delete-test" element={<ProductModelDeleteTestPage />} />
            <Route path="suppliers" element={<SupplierPage />} />
            <Route path="inventory" element={<InventoryPage />} />
            <Route path="purchase-orders" element={<PurchaseOrderPage />} />
            <Route path="purchase-orders/:uuid" element={<PurchaseOrderDetailPage />} />
            <Route path="sales-orders" element={<SalesOrderPage />} />
            <Route path="sales-orders/:uuid" element={<SalesOrderDetailPage />} />
            <Route path="customers" element={<CustomerPage />} />
            <Route path="customers/:uuid" element={<CustomerDetailPage />} />
            <Route path="operation-logs" element={<OperationLogsPage />} />
            <Route path="coze" element={<CozeUploadPage />} />
            <Route path="reports" element={<ReportPage />} />
            <Route path="smart-assistant" element={<SmartAssistantPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="users" element={<UserPage />} />
            <Route path="auth-debug" element={<AuthDebugPage />} />
          </Route>
          
          {/* 404 页面 */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;