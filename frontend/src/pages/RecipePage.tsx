import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChefHat, 
  Loader2, 
  Clock, 
  Users,
  AlertCircle,
  ShoppingCart,
  Sparkles,
  ArrowRight,
  Check,
  Package,
  Settings
} from 'lucide-react';
import { recipeApi } from '../services/api';
import { usePantry } from '../contexts/PantryContext';
import { usePreferences } from '../contexts/PreferencesContext';
import type { Recipe, Ingredient } from '../types';

export default function RecipePage() {
  const { pantryItems } = usePantry();
  const { preferences } = usePreferences();
  const [isGenerating, setIsGenerating] = useState(false);
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const hasPreferences = preferences.diets.length > 0 || 
                         preferences.allergens.length > 0 || 
                         preferences.maxCookingTime || 
                         preferences.difficulty;

  const handleGenerate = async () => {
    if (pantryItems.length === 0) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const ingredientNames = pantryItems.map((item) => item.name);
      
      // Include preferences in the API call
      const response = await recipeApi.generateRecipe({
        ingredients: ingredientNames,
        diets: preferences.diets.length > 0 ? preferences.diets : undefined,
        allergens: preferences.allergens.length > 0 ? preferences.allergens : undefined,
        max_cooking_time: preferences.maxCookingTime || null,
        difficulty: preferences.difficulty || null,
      });
      
      if (response.recipe_raw) {
        const parsedRecipe = JSON.parse(response.recipe_raw);
        setRecipe(parsedRecipe);
      } else {
        setError('No recipe could be generated with your ingredients.');
      }
    } catch (err) {
      setError('Failed to generate recipe. Please try again.');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreateShoppingList = () => {
    if (!recipe) return;
    
    // Store recipe ingredients in session storage for shopping list page
    const recipeIngredients: Ingredient[] = recipe.ingredients.map((ing) => ({
      name: ing.name,
      quantity: ing.amount,
      unit: ing.unit,
    }));
    
    sessionStorage.setItem('recipeIngredients', JSON.stringify(recipeIngredients));
    sessionStorage.setItem('recipeTitle', recipe.title);
    navigate('/shopping-list');
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'hard':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Generate Recipe</h1>
        <p className="text-espresso-500 mt-1">
          Create delicious recipes from your ingredients
        </p>
      </div>

      <div className="px-6 space-y-6">
        {/* Pantry Summary */}
        <div className="card bg-gradient-to-r from-sage-50 to-cream-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-sage-200 rounded-xl">
                <Package size={20} className="text-sage-700" />
              </div>
              <div>
                <p className="font-medium text-espresso-700">Available Ingredients</p>
                <p className="text-sm text-espresso-500">
                  {pantryItems.length} item{pantryItems.length !== 1 ? 's' : ''} in pantry
                </p>
              </div>
            </div>
            <Link to="/pantry" className="text-sage-600 font-medium hover:underline text-sm">
              View all
            </Link>
          </div>

          {pantryItems.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {pantryItems.slice(0, 8).map((item) => (
                <span key={item.id} className="chip chip-sage">
                  {item.name}
                </span>
              ))}
              {pantryItems.length > 8 && (
                <span className="chip">+{pantryItems.length - 8} more</span>
              )}
            </div>
          )}
        </div>

        {/* Active Preferences Badge */}
        {hasPreferences && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-terracotta-50 to-cream-100"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-terracotta-200 rounded-xl">
                  <Settings size={20} className="text-terracotta-700" />
                </div>
                <div>
                  <p className="font-medium text-espresso-700">Preferences Active</p>
                  <p className="text-sm text-espresso-500">
                    Recipe will respect your dietary settings
                  </p>
                </div>
              </div>
              <Link to="/preferences" className="text-terracotta-600 font-medium hover:underline text-sm">
                Edit
              </Link>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {preferences.diets.map((diet) => (
                <span key={diet} className="chip chip-active text-xs">
                  {diet}
                </span>
              ))}
              {preferences.allergens.map((allergen) => (
                <span key={allergen} className="chip bg-red-100 text-red-700 text-xs">
                  No {allergen}
                </span>
              ))}
              {preferences.maxCookingTime && (
                <span className="chip text-xs">
                  ≤{preferences.maxCookingTime} min
                </span>
              )}
              {preferences.difficulty && (
                <span className="chip text-xs capitalize">
                  {preferences.difficulty}
                </span>
              )}
            </div>
          </motion.div>
        )}

        {/* Generate Button */}
        {!recipe && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {pantryItems.length === 0 ? (
              <div className="card text-center py-8">
                <div className="text-5xl mb-4">🥗</div>
                <h3 className="font-display text-lg font-semibold text-espresso-800 mb-2">
                  No ingredients yet
                </h3>
                <p className="text-espresso-500 mb-4">
                  Add some ingredients to your pantry first
                </p>
                <Link to="/scan" className="btn-primary inline-flex items-center gap-2">
                  <Sparkles size={18} />
                  Scan Ingredients
                </Link>
              </div>
            ) : (
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full card bg-gradient-to-r from-terracotta-500 to-terracotta-600 text-white hover:from-terracotta-600 hover:to-terracotta-700 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white/20 rounded-xl group-hover:scale-110 transition-transform">
                      {isGenerating ? (
                        <Loader2 className="animate-spin" size={28} />
                      ) : (
                        <ChefHat size={28} />
                      )}
                    </div>
                    <div className="text-left">
                      <h3 className="font-display text-xl font-semibold">
                        {isGenerating ? 'Creating Recipe...' : 'Generate Recipe'}
                      </h3>
                      <p className="text-terracotta-100 text-sm">
                        {isGenerating 
                          ? 'Our AI chef is cooking up something special'
                          : hasPreferences 
                            ? 'AI will create a recipe matching your preferences'
                            : 'AI will create a recipe using your ingredients'
                        }
                      </p>
                    </div>
                  </div>
                  {!isGenerating && (
                    <ArrowRight size={24} className="group-hover:translate-x-1 transition-transform" />
                  )}
                </div>
              </button>
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="flex items-center gap-3 bg-red-50 text-red-600 px-4 py-3 rounded-xl mt-4"
              >
                <AlertCircle size={20} />
                <span className="text-sm">{error}</span>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Recipe Card */}
        <AnimatePresence>
          {recipe && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Recipe Header */}
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="font-display text-2xl font-bold text-espresso-800">
                      {recipe.title}
                    </h2>
                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                      <span className="flex items-center gap-1 text-sm text-espresso-500">
                        <Clock size={16} />
                        {recipe.estimated_time_minutes} min
                      </span>
                      <span className="flex items-center gap-1 text-sm text-espresso-500">
                        <Users size={16} />
                        {recipe.servings} servings
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${getDifficultyColor(recipe.difficulty)}`}>
                        {recipe.difficulty}
                      </span>
                    </div>
                  </div>
                  <span className="text-4xl">👨‍🍳</span>
                </div>
              </div>

              {/* Ingredients */}
              <div className="card">
                <h3 className="font-display text-lg font-semibold text-espresso-800 mb-4">
                  Ingredients
                </h3>
                <ul className="space-y-2">
                  {recipe.ingredients.map((ing, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center gap-3 p-2 bg-cream-50 rounded-lg"
                    >
                      <Check size={16} className="text-sage-500 flex-shrink-0" />
                      <span className="text-espresso-700">
                        <span className="font-medium">{ing.amount} {ing.unit}</span>{' '}
                        {ing.name}
                      </span>
                    </motion.li>
                  ))}
                </ul>
              </div>

              {/* Steps */}
              <div className="card">
                <h3 className="font-display text-lg font-semibold text-espresso-800 mb-4">
                  Instructions
                </h3>
                <ol className="space-y-4">
                  {recipe.steps.map((step, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex gap-4"
                    >
                      <span className="flex-shrink-0 w-8 h-8 bg-terracotta-100 text-terracotta-600 rounded-full flex items-center justify-center font-semibold text-sm">
                        {index + 1}
                      </span>
                      <p className="text-espresso-700 pt-1">{step}</p>
                    </motion.li>
                  ))}
                </ol>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => setRecipe(null)}
                  className="btn-outline flex-1"
                >
                  New Recipe
                </button>
                <button
                  onClick={handleCreateShoppingList}
                  className="btn-secondary flex-1 flex items-center justify-center gap-2"
                >
                  <ShoppingCart size={18} />
                  Shopping List
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
