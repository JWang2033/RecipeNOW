import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ScanPage from './pages/ScanPage';
import PantryPage from './pages/PantryPage';
import RecipePage from './pages/RecipePage';
import ShoppingListPage from './pages/ShoppingListPage';
import PreferencesPage from './pages/PreferencesPage';
import SecurityPage from './pages/SecurityPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream-100">
        <div className="animate-pulse-soft">
          <span className="text-4xl">🍳</span>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/scan" element={<ScanPage />} />
                <Route path="/pantry" element={<PantryPage />} />
                <Route path="/recipe" element={<RecipePage />} />
                <Route path="/shopping-list" element={<ShoppingListPage />} />
                <Route path="/preferences" element={<PreferencesPage />} />
                <Route path="/security" element={<SecurityPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;

