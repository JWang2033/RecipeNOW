import { type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Home, Camera, Package, ChefHat, ShoppingCart, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/scan', icon: Camera, label: 'Scan' },
  { path: '/pantry', icon: Package, label: 'Pantry' },
  { path: '/recipe', icon: ChefHat, label: 'Recipe' },
  { path: '/shopping-list', icon: ShoppingCart, label: 'Shop' },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-cream-50 via-cream-100 to-cream-200">
      {/* Header */}
      <header className="sticky top-0 z-40 glass border-b border-cream-200">
        <div className="max-w-lg mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🍳</span>
            <h1 className="font-display text-xl font-semibold gradient-text">
              RecipeNOW
            </h1>
          </div>
          <NavLink 
            to="/preferences"
            className={({ isActive }) => 
              `p-2 rounded-xl transition-colors ${
                isActive 
                  ? 'bg-terracotta-100 text-terracotta-600' 
                  : 'text-espresso-500 hover:bg-cream-200'
              }`
            }
          >
            <Settings size={22} />
          </NavLink>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto pb-28">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 glass border-t border-cream-200">
        <div className="max-w-lg mx-auto px-4">
          <div className="flex items-center justify-around py-2">
            {navItems.map(({ path, icon: Icon, label }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'text-terracotta-600 bg-terracotta-50'
                      : 'text-espresso-400 hover:text-espresso-600 hover:bg-cream-200'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <motion.div
                      initial={false}
                      animate={{ scale: isActive ? 1.1 : 1 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    >
                      <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
                    </motion.div>
                    <span className="text-xs font-medium">{label}</span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
    </div>
  );
}

