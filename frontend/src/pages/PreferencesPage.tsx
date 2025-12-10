import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Leaf, 
  AlertTriangle, 
  Clock, 
  ChefHat,
  RotateCcw,
  Check,
  LogOut,
} from 'lucide-react';
import { usePreferences } from '../contexts/PreferencesContext';
import { useAuth } from '../contexts/AuthContext';
import type { DietaryPreference, Allergen } from '../types';

const dietaryOptions: { value: DietaryPreference; label: string; emoji: string }[] = [
  { value: 'vegetarian', label: 'Vegetarian', emoji: '🥬' },
  { value: 'vegan', label: 'Vegan', emoji: '🌱' },
  { value: 'pescatarian', label: 'Pescatarian', emoji: '🐟' },
  { value: 'keto', label: 'Keto', emoji: '🥑' },
  { value: 'paleo', label: 'Paleo', emoji: '🦴' },
  { value: 'gluten-free', label: 'Gluten-Free', emoji: '🌾' },
  { value: 'dairy-free', label: 'Dairy-Free', emoji: '🥛' },
  { value: 'low-carb', label: 'Low-Carb', emoji: '🍞' },
];

const allergenOptions: { value: Allergen; label: string; emoji: string }[] = [
  { value: 'peanut', label: 'Peanuts', emoji: '🥜' },
  { value: 'tree-nut', label: 'Tree Nuts', emoji: '🌰' },
  { value: 'milk', label: 'Milk/Dairy', emoji: '🥛' },
  { value: 'egg', label: 'Eggs', emoji: '🥚' },
  { value: 'wheat', label: 'Wheat', emoji: '🌾' },
  { value: 'soy', label: 'Soy', emoji: '🫘' },
  { value: 'fish', label: 'Fish', emoji: '🐟' },
  { value: 'shellfish', label: 'Shellfish', emoji: '🦐' },
];

const cookingTimeOptions = [
  { value: 15, label: '15 min' },
  { value: 30, label: '30 min' },
  { value: 45, label: '45 min' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
];

const difficultyOptions: { value: 'easy' | 'medium' | 'hard'; label: string; emoji: string }[] = [
  { value: 'easy', label: 'Easy', emoji: '😊' },
  { value: 'medium', label: 'Medium', emoji: '🤔' },
  { value: 'hard', label: 'Hard', emoji: '💪' },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 },
};

export default function PreferencesPage() {
  const { 
    preferences, 
    toggleDiet, 
    toggleAllergen, 
    setMaxCookingTime,
    setDifficulty,
    clearPreferences 
  } = usePreferences();
  const { logout } = useAuth();

  const activeCount = 
    preferences.diets.length + 
    preferences.allergens.length + 
    (preferences.maxCookingTime ? 1 : 0) + 
    (preferences.difficulty ? 1 : 0);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Preferences</h1>
            <p className="text-espresso-500 mt-1">
              Customize your recipe recommendations
            </p>
          </div>
          <div className="p-3 bg-terracotta-100 rounded-xl">
            <Settings size={24} className="text-terracotta-600" />
          </div>
        </div>
      </div>

      <div className="px-6 space-y-6">
        {/* Active Preferences Summary */}
        {activeCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-sage-50 to-cream-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-espresso-700">
                  {activeCount} preference{activeCount !== 1 ? 's' : ''} active
                </p>
                <p className="text-sm text-espresso-500">
                  Recipes will be filtered accordingly
                </p>
              </div>
              <button
                onClick={() => {
                  if (confirm('Reset all preferences to default?')) {
                    clearPreferences();
                  }
                }}
                className="flex items-center gap-1.5 text-sm text-espresso-500 hover:text-terracotta-600 transition-colors"
              >
                <RotateCcw size={16} />
                Reset
              </button>
            </div>
          </motion.div>
        )}

        {/* Dietary Preferences */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-sage-100 rounded-lg">
              <Leaf size={20} className="text-sage-600" />
            </div>
            <h3 className="font-display text-lg font-semibold text-espresso-800">
              Dietary Preferences
            </h3>
          </div>
          
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="flex flex-wrap gap-2"
          >
            {dietaryOptions.map((option) => {
              const isSelected = preferences.diets.includes(option.value);
              return (
                <motion.button
                  key={option.value}
                  variants={item}
                  onClick={() => toggleDiet(option.value)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all ${
                    isSelected
                      ? 'bg-sage-500 text-white shadow-lg shadow-sage-500/25'
                      : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
                  }`}
                >
                  <span>{option.emoji}</span>
                  <span>{option.label}</span>
                  {isSelected && <Check size={16} />}
                </motion.button>
              );
            })}
          </motion.div>
        </div>

        {/* Allergens */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle size={20} className="text-red-600" />
            </div>
            <div>
              <h3 className="font-display text-lg font-semibold text-espresso-800">
                Allergens to Avoid
              </h3>
              <p className="text-sm text-espresso-500">
                FALCPA major allergens
              </p>
            </div>
          </div>
          
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="flex flex-wrap gap-2"
          >
            {allergenOptions.map((option) => {
              const isSelected = preferences.allergens.includes(option.value);
              return (
                <motion.button
                  key={option.value}
                  variants={item}
                  onClick={() => toggleAllergen(option.value)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all ${
                    isSelected
                      ? 'bg-red-500 text-white shadow-lg shadow-red-500/25'
                      : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
                  }`}
                >
                  <span>{option.emoji}</span>
                  <span>{option.label}</span>
                  {isSelected && <Check size={16} />}
                </motion.button>
              );
            })}
          </motion.div>
        </div>

        {/* Max Cooking Time */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-terracotta-100 rounded-lg">
              <Clock size={20} className="text-terracotta-600" />
            </div>
            <h3 className="font-display text-lg font-semibold text-espresso-800">
              Max Cooking Time
            </h3>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setMaxCookingTime(undefined)}
              className={`px-4 py-2.5 rounded-xl font-medium transition-all ${
                !preferences.maxCookingTime
                  ? 'bg-terracotta-500 text-white shadow-lg shadow-terracotta-500/25'
                  : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
              }`}
            >
              Any time
            </button>
            {cookingTimeOptions.map((option) => {
              const isSelected = preferences.maxCookingTime === option.value;
              return (
                <button
                  key={option.value}
                  onClick={() => setMaxCookingTime(option.value)}
                  className={`px-4 py-2.5 rounded-xl font-medium transition-all ${
                    isSelected
                      ? 'bg-terracotta-500 text-white shadow-lg shadow-terracotta-500/25'
                      : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
                  }`}
                >
                  ≤ {option.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Difficulty */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-cream-200 rounded-lg">
              <ChefHat size={20} className="text-espresso-600" />
            </div>
            <h3 className="font-display text-lg font-semibold text-espresso-800">
              Preferred Difficulty
            </h3>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setDifficulty(undefined)}
              className={`flex-1 px-4 py-3 rounded-xl font-medium transition-all ${
                !preferences.difficulty
                  ? 'bg-espresso-700 text-white'
                  : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
              }`}
            >
              Any
            </button>
            {difficultyOptions.map((option) => {
              const isSelected = preferences.difficulty === option.value;
              return (
                <button
                  key={option.value}
                  onClick={() => setDifficulty(option.value)}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                    isSelected
                      ? 'bg-espresso-700 text-white'
                      : 'bg-cream-100 text-espresso-600 hover:bg-cream-200'
                  }`}
                >
                  <span>{option.emoji}</span>
                  <span>{option.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Info */}
        <div className="card bg-gradient-to-br from-cream-100 to-cream-200 border-cream-300">
          <div className="flex gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <h4 className="font-medium text-espresso-700 mb-1">About Preferences</h4>
              <p className="text-sm text-espresso-500">
                Your preferences are saved locally and will be used when generating 
                recipes. The AI will try to respect these constraints while creating 
                delicious meals from your ingredients.
              </p>
            </div>
          </div>
        </div>

        {/* Account Settings Section */}
        <div className="pt-4 border-t border-cream-200">
          <h3 className="text-sm font-medium text-espresso-500 mb-3 px-1">
            Account Settings
          </h3>
          
          {/* Logout Button */}
          <button
            onClick={() => {
              if (confirm('Are you sure you want to log out?')) {
                logout();
              }
            }}
            className="mt-3 w-full card hover:shadow-lg transition-all group flex items-center gap-4 border-red-100 hover:border-red-200"
          >
            <div className="p-2 bg-red-100 rounded-lg group-hover:scale-110 transition-transform">
              <LogOut size={20} className="text-red-600" />
            </div>
            <div className="text-left">
              <h4 className="font-medium text-red-600">Log Out</h4>
              <p className="text-sm text-espresso-500">Sign out of your account</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
