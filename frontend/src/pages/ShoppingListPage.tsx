import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShoppingCart, 
  Loader2, 
  Check, 
  AlertCircle,
  Sparkles,
  Package,
  ChefHat,
  Download,
  Share2,
  Trash2,
  X,
  PartyPopper
} from 'lucide-react';
import { shoppingListApi } from '../services/api';
import { usePantry } from '../contexts/PantryContext';
import type { ShoppingListItem, Ingredient } from '../types';

export default function ShoppingListPage() {
  const { getIngredientsForApi, pantryItems } = usePantry();
  const [isGenerating, setIsGenerating] = useState(false);
  const [shoppingList, setShoppingList] = useState<ShoppingListItem[]>([]);
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [recipeTitle, setRecipeTitle] = useState<string | null>(null);
  const [recipeIngredients, setRecipeIngredients] = useState<Ingredient[]>([]);
  const [hasGenerated, setHasGenerated] = useState(false); // Track if we've generated

  // Load recipe ingredients from session storage (coming from Recipe page)
  useEffect(() => {
    const storedIngredients = sessionStorage.getItem('recipeIngredients');
    const storedTitle = sessionStorage.getItem('recipeTitle');
    
    if (storedIngredients) {
      try {
        setRecipeIngredients(JSON.parse(storedIngredients));
      } catch {
        // Ignore parse errors
      }
    }
    if (storedTitle) {
      setRecipeTitle(storedTitle);
    }
  }, []);

  const handleGenerate = async () => {
    if (recipeIngredients.length === 0) {
      setError('No recipe selected. Please generate a recipe first.');
      return;
    }
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const pantryIngredients = getIngredientsForApi();
      const response = await shoppingListApi.generateShoppingList(
        pantryIngredients,
        recipeIngredients
      );
      
      setShoppingList(response.to_buy || []);
      setCheckedItems(new Set());
      setHasGenerated(true); // Mark as generated
    } catch (err) {
      setError('Failed to generate shopping list. Please try again.');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleItem = (name: string) => {
    setCheckedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(name)) {
        newSet.delete(name);
      } else {
        newSet.add(name);
      }
      return newSet;
    });
  };

  const clearCompleted = () => {
    setShoppingList((prev) => prev.filter((item) => !checkedItems.has(item.name)));
    setCheckedItems(new Set());
  };

  const exportList = () => {
    const text = shoppingList
      .map((item) => {
        const qty = item.quantity ? `${item.quantity} ${item.unit || ''}` : '';
        return `${checkedItems.has(item.name) ? '✓' : '○'} ${item.name}${qty ? ` - ${qty.trim()}` : ''}`;
      })
      .join('\n');
    
    const blob = new Blob([`Shopping List${recipeTitle ? ` for ${recipeTitle}` : ''}\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'shopping-list.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const shareList = async () => {
    const text = shoppingList
      .map((item) => {
        const qty = item.quantity ? `${item.quantity} ${item.unit || ''}` : '';
        return `• ${item.name}${qty ? ` (${qty.trim()})` : ''}`;
      })
      .join('\n');
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Shopping List${recipeTitle ? ` for ${recipeTitle}` : ''}`,
          text: text,
        });
      } catch {
        // User cancelled or share failed
      }
    }
  };

  const resetList = () => {
    sessionStorage.removeItem('recipeIngredients');
    sessionStorage.removeItem('recipeTitle');
    setRecipeTitle(null);
    setRecipeIngredients([]);
    setShoppingList([]);
    setHasGenerated(false);
  };

  const completedCount = checkedItems.size;
  const totalCount = shoppingList.length;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Shopping List</h1>
        <p className="text-espresso-500 mt-1">
          Items you need to buy for your recipes
        </p>
      </div>

      <div className="px-6 space-y-4">
        {/* Recipe Info */}
        {recipeTitle && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-terracotta-50 to-cream-100"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-terracotta-200 rounded-xl">
                <ChefHat size={20} className="text-terracotta-700" />
              </div>
              <div className="flex-grow">
                <p className="text-sm text-espresso-500">Recipe</p>
                <p className="font-medium text-espresso-700">{recipeTitle}</p>
              </div>
              <button
                onClick={resetList}
                className="p-2 text-espresso-400 hover:text-espresso-600"
              >
                <X size={18} />
              </button>
            </div>
          </motion.div>
        )}

        {/* Pantry Summary */}
        <div className="card bg-gradient-to-r from-sage-50 to-cream-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sage-200 rounded-xl">
              <Package size={20} className="text-sage-700" />
            </div>
            <div>
              <p className="font-medium text-espresso-700">Your Pantry</p>
              <p className="text-sm text-espresso-500">
                {pantryItems.length} ingredient{pantryItems.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>
        </div>

        {/* No Recipe Selected */}
        {recipeIngredients.length === 0 && !hasGenerated && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="card text-center py-8">
              <div className="text-5xl mb-4">📋</div>
              <h3 className="font-display text-lg font-semibold text-espresso-800 mb-2">
                No recipe selected
              </h3>
              <p className="text-espresso-500 mb-4">
                Generate a recipe first to create a shopping list
              </p>
            </div>
          </motion.div>
        )}

        {/* Generate Button - Show when recipe is selected but not yet generated */}
        {recipeIngredients.length > 0 && !hasGenerated && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full card bg-gradient-to-r from-sage-500 to-sage-600 text-white hover:from-sage-600 hover:to-sage-700 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/20 rounded-xl group-hover:scale-110 transition-transform">
                    {isGenerating ? (
                      <Loader2 className="animate-spin" size={28} />
                    ) : (
                      <Sparkles size={28} />
                    )}
                  </div>
                  <div className="text-left">
                    <h3 className="font-display text-xl font-semibold">
                      {isGenerating ? 'Comparing...' : 'Generate Shopping List'}
                    </h3>
                    <p className="text-sage-100 text-sm">
                      {isGenerating 
                        ? 'Finding what you need to buy'
                        : 'Compare recipe with your pantry'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </button>
          </motion.div>
        )}

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="flex items-center gap-3 bg-red-50 text-red-600 px-4 py-3 rounded-xl"
          >
            <AlertCircle size={20} />
            <span className="text-sm">{error}</span>
          </motion.div>
        )}

        {/* You Have Everything! - Show when generated but list is empty */}
        {hasGenerated && shoppingList.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card bg-gradient-to-r from-sage-100 to-sage-50 text-center py-8"
          >
            <div className="text-5xl mb-4">🎉</div>
            <h3 className="font-display text-xl font-semibold text-sage-800 mb-2">
              You have everything!
            </h3>
            <p className="text-sage-600 mb-4">
              Your pantry has all the ingredients needed for this recipe.
            </p>
            <p className="text-sage-500 text-sm">
              Time to start cooking! 👨‍🍳
            </p>
            <button
              onClick={resetList}
              className="mt-4 btn-outline"
            >
              Choose Another Recipe
            </button>
          </motion.div>
        )}

        {/* Shopping List - Show when we have items to buy */}
        <AnimatePresence>
          {shoppingList.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Progress */}
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-display font-semibold text-espresso-800">
                    Items to Buy
                  </h3>
                  <span className="text-sm text-espresso-500">
                    {completedCount}/{totalCount} checked
                  </span>
                </div>
                
                <div className="w-full bg-cream-200 rounded-full h-2 mb-4">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(completedCount / totalCount) * 100}%` }}
                    className="bg-sage-500 h-2 rounded-full"
                  />
                </div>

                {/* Items */}
                <ul className="space-y-2">
                  {shoppingList.map((item, index) => {
                    const isChecked = checkedItems.has(item.name);
                    return (
                      <motion.li
                        key={item.name}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        onClick={() => toggleItem(item.name)}
                        className={`flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-all ${
                          isChecked 
                            ? 'bg-sage-50 opacity-60' 
                            : 'bg-cream-50 hover:bg-cream-100'
                        }`}
                      >
                        <div className={`mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                          isChecked 
                            ? 'bg-sage-500 border-sage-500' 
                            : 'border-cream-400'
                        }`}>
                          {isChecked && <Check size={14} className="text-white" />}
                        </div>
                        <div className="flex-grow">
                          <span className={`font-medium ${isChecked ? 'line-through text-espresso-400' : 'text-espresso-700'}`}>
                            {item.name}
                          </span>
                          {(item.quantity || item.unit) && (
                            <span className="text-espresso-400 ml-2">
                              {item.quantity} {item.unit}
                            </span>
                          )}
                          {item.reason && (
                            <p className="text-xs text-espresso-400 mt-1">
                              {item.reason}
                            </p>
                          )}
                        </div>
                      </motion.li>
                    );
                  })}
                </ul>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={exportList}
                  className="btn-outline flex-1 flex items-center justify-center gap-2"
                >
                  <Download size={18} />
                  Export
                </button>
                {navigator.share && (
                  <button
                    onClick={shareList}
                    className="btn-outline flex-1 flex items-center justify-center gap-2"
                  >
                    <Share2 size={18} />
                    Share
                  </button>
                )}
                {completedCount > 0 && (
                  <button
                    onClick={clearCompleted}
                    className="btn-outline flex items-center justify-center gap-2 text-red-500 border-red-300 hover:bg-red-50"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>

              {/* Generate New */}
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full text-center text-sage-600 font-medium py-3 hover:underline"
              >
                {isGenerating ? 'Refreshing...' : 'Refresh list'}
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* All items purchased */}
        {shoppingList.length > 0 && completedCount === totalCount && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card bg-gradient-to-r from-sage-100 to-sage-50 text-center py-6"
          >
            <span className="text-4xl mb-3 block">🎉</span>
            <h3 className="font-display text-lg font-semibold text-sage-800">
              All items checked!
            </h3>
            <p className="text-sage-600 text-sm">You're ready to cook!</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
