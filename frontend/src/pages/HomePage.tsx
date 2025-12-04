import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Camera, Package, ChefHat, ShoppingCart, Sparkles, ArrowRight, LogOut } from 'lucide-react';
import { usePantry } from '../contexts/PantryContext';
import { useAuth } from '../contexts/AuthContext';

const features = [
  {
    icon: Camera,
    title: 'Scan Ingredients',
    description: 'Take a photo and let AI identify your ingredients',
    path: '/scan',
    color: 'terracotta',
    emoji: '📸',
  },
  {
    icon: Package,
    title: 'My Pantry',
    description: 'View and manage your ingredient inventory',
    path: '/pantry',
    color: 'sage',
    emoji: '🥬',
  },
  {
    icon: ChefHat,
    title: 'Generate Recipe',
    description: 'Get personalized recipe suggestions from your pantry',
    path: '/recipe',
    color: 'terracotta',
    emoji: '👨‍🍳',
  },
  {
    icon: ShoppingCart,
    title: 'Shopping List',
    description: 'Create smart shopping lists for missing ingredients',
    path: '/shopping-list',
    color: 'sage',
    emoji: '🛒',
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function HomePage() {
  const { pantryItems } = usePantry();
  const { logout } = useAuth();

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="px-6 pt-8 pb-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="font-display text-4xl font-bold text-espresso-800 mb-3">
            What's Cooking?
          </h1>
          <p className="text-espresso-500 text-lg">
            Transform your ingredients into delicious meals
          </p>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6 card bg-gradient-to-r from-terracotta-500 to-terracotta-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-terracotta-100 text-sm font-medium">Your Pantry</p>
              <p className="text-3xl font-bold mt-1">
                {pantryItems.length}
                <span className="text-lg font-normal ml-2">
                  ingredient{pantryItems.length !== 1 ? 's' : ''}
                </span>
              </p>
            </div>
            <div className="text-5xl">🧺</div>
          </div>
          {pantryItems.length > 0 && (
            <Link
              to="/recipe"
              className="mt-4 flex items-center gap-2 text-sm font-medium text-white/90 hover:text-white transition-colors"
            >
              <Sparkles size={16} />
              Generate a recipe now
              <ArrowRight size={16} />
            </Link>
          )}
        </motion.div>
      </div>

      {/* Features Grid */}
      <div className="px-6">
        <h2 className="section-title flex items-center gap-2">
          <span>Quick Actions</span>
        </h2>
        
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 gap-4"
        >
          {features.map((feature) => (
            <motion.div key={feature.path} variants={item}>
              <Link
                to={feature.path}
                className={`card group hover:shadow-xl transition-all duration-300 h-full flex flex-col ${
                  feature.color === 'terracotta' 
                    ? 'hover:border-terracotta-200' 
                    : 'hover:border-sage-200'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2.5 rounded-xl ${
                    feature.color === 'terracotta' 
                      ? 'bg-terracotta-100 text-terracotta-600' 
                      : 'bg-sage-100 text-sage-600'
                  }`}>
                    <feature.icon size={22} />
                  </div>
                  <span className="text-2xl group-hover:scale-110 transition-transform">
                    {feature.emoji}
                  </span>
                </div>
                <h3 className="font-display font-semibold text-espresso-800 mb-1">
                  {feature.title}
                </h3>
                <p className="text-sm text-espresso-500 flex-grow">
                  {feature.description}
                </p>
                <div className={`mt-3 flex items-center gap-1 text-sm font-medium ${
                  feature.color === 'terracotta' 
                    ? 'text-terracotta-600' 
                    : 'text-sage-600'
                }`}>
                  <span>Get started</span>
                  <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Tips Section */}
      <div className="px-6 mt-8">
        <div className="card bg-gradient-to-br from-sage-50 to-cream-100 border-sage-200">
          <div className="flex items-start gap-4">
            <span className="text-3xl">💡</span>
            <div>
              <h3 className="font-display font-semibold text-espresso-800 mb-1">
                Pro Tip
              </h3>
              <p className="text-sm text-espresso-600">
                Start by scanning ingredients from your fridge or pantry. Our AI will recognize 
                them and add to your inventory automatically!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Logout Button */}
      <div className="px-6 mt-8">
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-3 text-espresso-500 hover:text-terracotta-600 transition-colors"
        >
          <LogOut size={18} />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </div>
  );
}

