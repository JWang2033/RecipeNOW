import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';
import { PantryProvider } from './contexts/PantryContext';
import { PreferencesProvider } from './contexts/PreferencesContext';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PantryProvider>
          <PreferencesProvider>
            <App />
          </PreferencesProvider>
        </PantryProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);

