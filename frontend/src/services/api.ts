import type { 
  AuthResponse, 
  ScanResponse, 
  GenerateRecipeResponse, 
  ShoppingListResponse,
  Ingredient 
} from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token');
  
  const headers: HeadersInit = {
    ...options.headers,
  };
  
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  
  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  const responseText = await response.text();

  if (!responseText) {
    return undefined as T;
  }

  if (contentType.includes('application/json')) {
    return JSON.parse(responseText) as T;
  }

  return responseText as unknown as T;
}

// Auth response types
interface LoginResponse extends AuthResponse {
  requires_2fa?: boolean;
  message?: string;
}

interface TwoFASetupResponse {
  secret: string;
  qr_code: string;
  manual_entry_key: string;
}

interface TwoFAStatusResponse {
  is_enabled: boolean;
}

// Auth endpoints
export const authApi = {
  login: async (phoneNumber: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', phoneNumber);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new ApiError(response.status, 'Invalid credentials');
    }
    
    return response.json();
  },
  
  register: async (phoneNumber: string, username: string, password: string) => {
    return fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ 
        phone_number: phoneNumber, 
        name: username, 
        password 
      }),
    });
  },
};

// Scan endpoints
export const scanApi = {
  scanIngredients: async (imageFile: File): Promise<ScanResponse> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const token = localStorage.getItem('token');
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE}/scan/ingredients`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText);
    }
    
    return response.json();
  },
};

// Recipe generation endpoints
type RecipePreferencesPayload = {
  ingredients: string[];
  diets?: string[];
  allergens?: string[];
  max_cooking_time?: number | null;
  difficulty?: string | null;
};

export const recipeApi = {
  generateRecipe: async (payload: RecipePreferencesPayload): Promise<GenerateRecipeResponse> => {
    return fetchApi('/generate/ingredients', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

// Shopping list endpoints
export const shoppingListApi = {
  generateShoppingList: async (
    pantryIngredients: Ingredient[], 
    recipeIngredients: Ingredient[]
  ): Promise<ShoppingListResponse> => {
    return fetchApi('/shopping-list/generate', {
      method: 'POST',
      body: JSON.stringify({
        pantry_ingredients: pantryIngredients,
        recipe_ingredients: recipeIngredients,
      }),
    });
  },
};

export { ApiError };


// Pantry API endpoints
export const pantryApi = {
  getItems: async () => {
    return fetchApi<{ id: number; name: string; quantity?: string; unit?: string; notes?: string }[]>('/pantry/');
  },
  
  addItem: async (item: { name: string; quantity?: string; unit?: string; notes?: string }) => {
    return fetchApi('/pantry/', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  },
  
  addItemsBulk: async (items: { name: string; quantity?: string; unit?: string; notes?: string }[]) => {
    return fetchApi('/pantry/bulk', {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  },
  
  updateItem: async (id: number, updates: { name?: string; quantity?: string; unit?: string; notes?: string }) => {
    return fetchApi(`/pantry/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
  
  deleteItem: async (id: number) => {
    return fetchApi(`/pantry/${id}`, {
      method: 'DELETE',
    });
  },
  
  clearAll: async () => {
    return fetchApi('/pantry/', {
      method: 'DELETE',
    });
  },
};

// Preferences API endpoints
export const preferencesApi = {
  get: async () => {
    return fetchApi<{
      diets: string[];
      allergens: string[];
      max_cooking_time: number | null;
      difficulty: string | null;
    }>('/preferences/');
  },
  
  update: async (prefs: {
    diets?: string[];
    allergens?: string[];
    max_cooking_time?: number | null;
    difficulty?: string | null;
  }) => {
    return fetchApi('/preferences/', {
      method: 'PUT',
      body: JSON.stringify(prefs),
    });
  },
  
  clear: async () => {
    return fetchApi('/preferences/', {
      method: 'DELETE',
    });
  },
};
