import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Trash2, 
  Camera, 
  ChefHat, 
  Search,
  X,
  Edit3,
  Check,
  Loader2
} from 'lucide-react';
import { usePantry } from '../contexts/PantryContext';
import { getIngredientEmoji } from '../utils/ingredientEmoji';

export default function PantryPage() {
  const { pantryItems, isLoading, removeItem, updateItem, addItem, clearPantry } = usePantry();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newIngredient, setNewIngredient] = useState('');

  const filteredItems = pantryItems.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleEdit = (id: number, name: string) => {
    setEditingId(id);
    setEditValue(name);
  };

  const handleSaveEdit = async (id: number) => {
    if (editValue.trim()) {
      await updateItem(id, { name: editValue.trim() });
    }
    setEditingId(null);
    setEditValue('');
  };

  const handleAddIngredient = async () => {
    if (newIngredient.trim()) {
      await addItem({ name: newIngredient.trim() });
      setNewIngredient('');
      setShowAddModal(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container flex items-center justify-center">
        <Loader2 className="animate-spin text-terracotta-500" size={32} />
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">My Pantry</h1>
            <p className="text-espresso-500 mt-1">
              {pantryItems.length} ingredient{pantryItems.length !== 1 ? 's' : ''} in stock
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="p-3 bg-terracotta-500 text-white rounded-xl hover:bg-terracotta-600 transition-colors"
          >
            <Plus size={22} />
          </button>
        </div>
      </div>

      <div className="px-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-espresso-400" size={20} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search ingredients..."
            className="input-field pl-12 pr-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-espresso-400 hover:text-espresso-600"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Quick Actions */}
        <div className="flex gap-3">
          <Link
            to="/scan"
            className="flex-1 card hover:shadow-lg transition-all flex items-center gap-3 py-4"
          >
            <div className="p-2 bg-terracotta-100 rounded-lg text-terracotta-600">
              <Camera size={20} />
            </div>
            <span className="font-medium text-espresso-700">Scan More</span>
          </Link>
          <Link
            to="/recipe"
            className="flex-1 card hover:shadow-lg transition-all flex items-center gap-3 py-4"
          >
            <div className="p-2 bg-sage-100 rounded-lg text-sage-600">
              <ChefHat size={20} />
            </div>
            <span className="font-medium text-espresso-700">Cook Now</span>
          </Link>
        </div>

        {/* Pantry Items */}
        {pantryItems.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card text-center py-12"
          >
            <div className="text-6xl mb-4">🧺</div>
            <h3 className="font-display text-xl font-semibold text-espresso-800 mb-2">
              Your pantry is empty
            </h3>
            <p className="text-espresso-500 mb-6">
              Start by scanning ingredients or adding them manually
            </p>
            <div className="flex justify-center gap-3">
              <Link to="/scan" className="btn-primary">
                <Camera size={18} className="mr-2 inline" />
                Scan Ingredients
              </Link>
            </div>
          </motion.div>
        ) : (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-espresso-800">
                Ingredients
              </h3>
              {pantryItems.length > 0 && (
                <button
                  onClick={async () => {
                    if (confirm('Are you sure you want to clear all ingredients?')) {
                      await clearPantry();
                    }
                  }}
                  className="text-sm text-espresso-400 hover:text-red-500 transition-colors"
                >
                  Clear all
                </button>
              )}
            </div>

            <AnimatePresence mode="popLayout">
              {filteredItems.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-8 text-espresso-500"
                >
                  No ingredients match your search
                </motion.div>
              ) : (
                <ul className="space-y-2">
                  {filteredItems.map((item, index) => (
                    <motion.li
                      key={item.id}
                      layout
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20, height: 0 }}
                      transition={{ delay: index * 0.03 }}
                      className="flex items-center gap-3 p-3 bg-cream-50 rounded-xl group hover:bg-cream-100 transition-colors"
                    >
                      <span className="text-xl">
                        {getIngredientEmoji(item.name)}
                      </span>
                      
                      {editingId === item.id ? (
                        <div className="flex-grow flex items-center gap-2">
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit(item.id)}
                            className="flex-grow px-3 py-1.5 rounded-lg border border-terracotta-300 focus:outline-none focus:border-terracotta-500"
                            autoFocus
                          />
                          <button
                            onClick={() => handleSaveEdit(item.id)}
                            className="p-1.5 text-sage-600 hover:bg-sage-100 rounded-lg"
                          >
                            <Check size={18} />
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="p-1.5 text-espresso-400 hover:bg-espresso-100 rounded-lg"
                          >
                            <X size={18} />
                          </button>
                        </div>
                      ) : (
                        <>
                          <span className="flex-grow text-espresso-700 font-medium">
                            {item.name}
                          </span>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(item.id, item.name)}
                              className="p-1.5 text-espresso-400 hover:text-terracotta-600 hover:bg-terracotta-50 rounded-lg transition-colors"
                            >
                              <Edit3 size={16} />
                            </button>
                            <button
                              onClick={() => removeItem(item.id)}
                              className="p-1.5 text-espresso-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </>
                      )}
                    </motion.li>
                  ))}
                </ul>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Add Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-lg bg-white rounded-2xl p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="font-display text-xl font-semibold text-espresso-800 mb-4">
                Add Ingredient
              </h3>
              
              <div className="flex gap-3">
                <input
                  type="text"
                  value={newIngredient}
                  onChange={(e) => setNewIngredient(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddIngredient()}
                  placeholder="Enter ingredient name"
                  className="input-field flex-grow"
                  autoFocus
                />
                <button
                  onClick={handleAddIngredient}
                  disabled={!newIngredient.trim()}
                  className="btn-primary"
                >
                  Add
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
