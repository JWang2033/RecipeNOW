# RecipeNOW Frontend

A beautiful, modern React frontend for the RecipeNOW recipe suggestion app.

## 🎨 Features

- **Scan Ingredients** - Upload or capture photos to detect ingredients using AI
- **Pantry Management** - View, edit, and organize your ingredient inventory
- **Recipe Generation** - Get AI-powered recipe suggestions based on your pantry
- **Smart Shopping List** - Automatically generate shopping lists for missing ingredients
- **Dietary Preferences** - Set allergies, dietary restrictions, and cooking preferences

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Framer Motion** for smooth animations
- **React Router** for navigation
- **Lucide React** for icons

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- The backend server running on `localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   └── Layout.tsx   # Main layout with navigation
│   ├── contexts/        # React contexts for state management
│   │   ├── AuthContext.tsx
│   │   ├── PantryContext.tsx
│   │   └── PreferencesContext.tsx
│   ├── pages/           # Page components
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ScanPage.tsx
│   │   ├── PantryPage.tsx
│   │   ├── RecipePage.tsx
│   │   ├── ShoppingListPage.tsx
│   │   └── PreferencesPage.tsx
│   ├── services/        # API service layer
│   │   └── api.ts
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx          # Main app component with routing
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles and Tailwind
├── public/              # Static assets
├── index.html           # HTML template
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🎨 Design System

### Colors

- **Terracotta** - Primary accent color (buttons, highlights)
- **Sage** - Secondary accent (success states, nature elements)
- **Cream** - Background tones
- **Espresso** - Text and dark elements

### Typography

- **Playfair Display** - Headings and display text
- **DM Sans** - Body text and UI elements

## 🔗 API Integration

The frontend connects to the backend via a proxy configured in `vite.config.ts`. All API calls to `/api/*` are proxied to `http://localhost:8000`.

### Endpoints Used

- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `POST /scan/ingredients` - Upload image to detect ingredients
- `POST /generate/ingredients` - Generate recipe from ingredients
- `POST /shopping-list/generate` - Create shopping list

## 📱 Pages Overview

### Home Page
Dashboard with quick stats and navigation to main features.

### Scan Page
Upload or capture photos of ingredients. AI detects and lists found items for user confirmation.

### Pantry Page
Manage your ingredient inventory with search, edit, and delete capabilities.

### Recipe Page
Generate AI-powered recipes based on pantry contents. View ingredients and step-by-step instructions.

### Shopping List Page
Compare recipe requirements with pantry inventory. Check off items as you shop.

### Preferences Page
Set dietary restrictions (vegetarian, vegan, etc.), allergens to avoid, max cooking time, and difficulty preferences.

## 🌙 Local Storage

The app uses localStorage for:
- JWT authentication token
- Pantry items
- User preferences

Data persists across browser sessions.

