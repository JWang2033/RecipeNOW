import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { pantryApi } from '../services/api';
import { useAuth } from './AuthContext';
import type { Ingredient } from '../types';

interface PantryItem {
  id: number;
  name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
  addedAt: string;
}

interface PantryContextType {
  pantryItems: PantryItem[];
  isLoading: boolean;
  error: string | null;
  refreshPantry: () => Promise<void>;
  addItems: (ingredients: string[]) => Promise<void>;
  addItem: (item: { name: string; quantity?: number; unit?: string; notes?: string }) => Promise<void>;
  removeItem: (id: number) => Promise<void>;
  updateItem: (id: number, updates: { name?: string; quantity?: number; unit?: string; notes?: string }) => Promise<void>;
  clearPantry: () => Promise<void>;
  getIngredientsForApi: () => Ingredient[];
}

const PantryContext = createContext<PantryContextType | null>(null);

export function PantryProvider({ children }: { children: ReactNode }) {
  const [pantryItems, setPantryItems] = useState<PantryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const refreshPantry = useCallback(async () => {
    if (!isAuthenticated) {
      setPantryItems([]);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    try {
      const items = await pantryApi.getItems();
      setPantryItems(items.map(item => ({
        id: item.id,
        name: item.name,
        quantity: item.quantity ?? undefined,
        unit: item.unit ?? undefined,
        notes: item.notes ?? undefined,
        addedAt: item.added_at,
      })));
    } catch (err) {
      setError('Failed to load pantry');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Load pantry when authenticated
  useEffect(() => {
    refreshPantry();
  }, [refreshPantry]);

  const addItems = async (ingredients: string[]) => {
    if (!isAuthenticated) return;
    
    try {
      const items = ingredients.map(name => ({ name }));
      await pantryApi.addItemsBulk(items);
      await refreshPantry();
    } catch (err) {
      setError('Failed to add items');
      console.error(err);
    }
  };

  const addItem = async (item: { name: string; quantity?: number; unit?: string; notes?: string }) => {
    if (!isAuthenticated) return;
    
    try {
      await pantryApi.addItem(item);
      await refreshPantry();
    } catch (err) {
      setError('Failed to add item');
      console.error(err);
    }
  };

  const removeItem = async (id: number) => {
    if (!isAuthenticated) return;
    
    try {
      await pantryApi.deleteItem(id);
      setPantryItems(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      setError('Failed to remove item');
      console.error(err);
    }
  };

  const updateItem = async (id: number, updates: { name?: string; quantity?: number; unit?: string; notes?: string }) => {
    if (!isAuthenticated) return;
    
    try {
      await pantryApi.updateItem(id, updates);
      await refreshPantry();
    } catch (err) {
      setError('Failed to update item');
      console.error(err);
    }
  };

  const clearPantry = async () => {
    if (!isAuthenticated) return;
    
    try {
      await pantryApi.clearAll();
      setPantryItems([]);
    } catch (err) {
      setError('Failed to clear pantry');
      console.error(err);
    }
  };

  const getIngredientsForApi = (): Ingredient[] => {
    return pantryItems.map(({ name, quantity, unit, notes }) => ({
      name,
      quantity,
      unit,
      notes,
    }));
  };

  return (
    <PantryContext.Provider value={{ 
      pantryItems, 
      isLoading,
      error,
      refreshPantry,
      addItems,
      addItem,
      removeItem, 
      updateItem, 
      clearPantry,
      getIngredientsForApi 
    }}>
      {children}
    </PantryContext.Provider>
  );
}

export function usePantry() {
  const context = useContext(PantryContext);
  if (!context) {
    throw new Error('usePantry must be used within a PantryProvider');
  }
  return context;
}
