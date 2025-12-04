// User types
export interface User {
  id: number;
  phone_number: string;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Ingredient types
export interface Ingredient {
  name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
}

export interface DetectedIngredient {
  name: string;
  confidence?: number;
}

export interface ScanResponse {
  ingredients: string[];
  ingredients_raw: string;
  raw_vertex: Record<string, unknown>;
}

// Recipe types
export interface RecipeIngredient {
  name: string;
  amount: number;
  unit: string;
}

export interface Recipe {
  title: string;
  servings: number;
  ingredients: RecipeIngredient[];
  steps: string[];
  estimated_time_minutes: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface GenerateRecipeResponse {
  ingredients: string[];
  recipe_raw: string;
  raw_vertex: Record<string, unknown>;
}

// Shopping list types
export interface ShoppingListItem {
  name: string;
  quantity: number | null;
  unit: string | null;
  reason: string;
  matched_existing: string[];
  matched_recipe: string[];
}

export interface ShoppingListResponse {
  to_buy: ShoppingListItem[];
  shopping_list_raw: string;
  raw_vertex: Record<string, unknown>;
}

// Filter/Preferences types
export type DietaryPreference = 
  | 'vegetarian' 
  | 'vegan' 
  | 'pescatarian' 
  | 'keto' 
  | 'paleo' 
  | 'gluten-free'
  | 'dairy-free'
  | 'low-carb';

export type Allergen = 
  | 'peanut' 
  | 'tree-nut' 
  | 'milk' 
  | 'egg' 
  | 'wheat' 
  | 'soy' 
  | 'fish' 
  | 'shellfish';

export interface UserPreferences {
  diets: DietaryPreference[];
  allergens: Allergen[];
  maxCookingTime?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
}

// Pantry types
export interface PantryItem extends Ingredient {
  id: string;
  addedAt: Date;
  expiresAt?: Date;
}

