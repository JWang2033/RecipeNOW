import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { preferencesApi } from '../services/api';
import { useAuth } from './AuthContext';
import type { UserPreferences, DietaryPreference, Allergen } from '../types';

interface PreferencesContextType {
  preferences: UserPreferences;
  isLoading: boolean;
  error: string | null;
  refreshPreferences: () => Promise<void>;
  toggleDiet: (diet: DietaryPreference) => Promise<void>;
  toggleAllergen: (allergen: Allergen) => Promise<void>;
  setMaxCookingTime: (time: number | undefined) => Promise<void>;
  setDifficulty: (difficulty: 'easy' | 'medium' | 'hard' | undefined) => Promise<void>;
  clearPreferences: () => Promise<void>;
}

const defaultPreferences: UserPreferences = {
  diets: [],
  allergens: [],
  maxCookingTime: undefined,
  difficulty: undefined,
};

const PreferencesContext = createContext<PreferencesContextType | null>(null);

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const refreshPreferences = useCallback(async () => {
    if (!isAuthenticated) {
      setPreferences(defaultPreferences);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    try {
      const prefs = await preferencesApi.get();
      setPreferences({
        diets: prefs.diets as DietaryPreference[],
        allergens: prefs.allergens as Allergen[],
        maxCookingTime: prefs.max_cooking_time ?? undefined,
        difficulty: prefs.difficulty as 'easy' | 'medium' | 'hard' | undefined,
      });
    } catch (err) {
      // If 404, preferences don't exist yet - that's okay
      setPreferences(defaultPreferences);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Load preferences when authenticated
  useEffect(() => {
    refreshPreferences();
  }, [refreshPreferences]);

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    if (!isAuthenticated) return;
    
    const newPrefs = { ...preferences, ...updates };
    setPreferences(newPrefs);
    
    try {
      await preferencesApi.update({
        diets: newPrefs.diets,
        allergens: newPrefs.allergens,
        max_cooking_time: newPrefs.maxCookingTime ?? null,
        difficulty: newPrefs.difficulty ?? null,
      });
    } catch (err) {
      setError('Failed to save preferences');
      console.error(err);
      // Revert on error
      await refreshPreferences();
    }
  };

  const toggleDiet = async (diet: DietaryPreference) => {
    const newDiets = preferences.diets.includes(diet)
      ? preferences.diets.filter((d) => d !== diet)
      : [...preferences.diets, diet];
    await updatePreferences({ diets: newDiets });
  };

  const toggleAllergen = async (allergen: Allergen) => {
    const newAllergens = preferences.allergens.includes(allergen)
      ? preferences.allergens.filter((a) => a !== allergen)
      : [...preferences.allergens, allergen];
    await updatePreferences({ allergens: newAllergens });
  };

  const setMaxCookingTime = async (time: number | undefined) => {
    await updatePreferences({ maxCookingTime: time });
  };

  const setDifficulty = async (difficulty: 'easy' | 'medium' | 'hard' | undefined) => {
    await updatePreferences({ difficulty });
  };

  const clearPreferences = async () => {
    if (!isAuthenticated) return;
    
    try {
      await preferencesApi.clear();
      setPreferences(defaultPreferences);
    } catch (err) {
      setError('Failed to clear preferences');
      console.error(err);
    }
  };

  return (
    <PreferencesContext.Provider value={{ 
      preferences, 
      isLoading,
      error,
      refreshPreferences,
      toggleDiet, 
      toggleAllergen, 
      setMaxCookingTime,
      setDifficulty,
      clearPreferences 
    }}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const context = useContext(PreferencesContext);
  if (!context) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
}
