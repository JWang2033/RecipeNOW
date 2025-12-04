import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Phone, Lock, Eye, EyeOff, ArrowRight, Loader2, Shield, ArrowLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  
  const { login, loginWith2FA } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(phoneNumber, password);
      
      if (result.requires2FA) {
        setRequires2FA(true);
      } else if (result.success) {
        navigate('/');
      }
    } catch {
      setError('Invalid phone number or password');
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await loginWith2FA(phoneNumber, password, totpCode);
      navigate('/');
    } catch {
      setError('Invalid authentication code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setRequires2FA(false);
    setTotpCode('');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-terracotta-50 via-cream-100 to-sage-50 flex items-center justify-center p-6">
      {/* Decorative Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 text-6xl opacity-20 animate-float">🥗</div>
        <div className="absolute top-40 right-10 text-5xl opacity-20 animate-float" style={{ animationDelay: '1s' }}>🍳</div>
        <div className="absolute bottom-40 left-20 text-5xl opacity-20 animate-float" style={{ animationDelay: '2s' }}>🥘</div>
        <div className="absolute bottom-20 right-20 text-6xl opacity-20 animate-float" style={{ animationDelay: '0.5s' }}>🍲</div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.2 }}
            className="inline-block mb-4"
          >
            <span className="text-6xl">🍳</span>
          </motion.div>
          <h1 className="font-display text-4xl font-bold gradient-text mb-2">
            RecipeNOW
          </h1>
          <p className="text-espresso-500">
            Turn your ingredients into delicious meals
          </p>
        </div>

        {/* Login Form / 2FA Form */}
        <div className="card">
          <AnimatePresence mode="wait">
            {!requires2FA ? (
              <motion.div
                key="login"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h2 className="font-display text-2xl font-semibold text-espresso-800 mb-6 text-center">
                  Welcome Back
                </h2>

                <form onSubmit={handleSubmit} className="space-y-5">
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm"
                    >
                      {error}
                    </motion.div>
                  )}

                  <div>
                    <label className="label">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-espresso-400" size={20} />
                      <input
                        type="tel"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        placeholder="Enter your phone number"
                        className="input-field pl-12"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="label">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-espresso-400" size={20} />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        className="input-field pl-12 pr-12"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-espresso-400 hover:text-espresso-600"
                      >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <Loader2 className="animate-spin" size={20} />
                    ) : (
                      <>
                        Sign In
                        <ArrowRight size={20} />
                      </>
                    )}
                  </button>
                </form>
              </motion.div>
            ) : (
              <motion.div
                key="2fa"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <button
                  onClick={handleBack}
                  className="flex items-center gap-2 text-espresso-500 hover:text-espresso-700 mb-4"
                >
                  <ArrowLeft size={18} />
                  Back
                </button>

                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-sage-100 rounded-full mb-4">
                    <Shield className="text-sage-600" size={32} />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-800">
                    Two-Factor Authentication
                  </h2>
                  <p className="text-espresso-500 mt-2">
                    Enter the 6-digit code from your authenticator app
                  </p>
                </div>

                <form onSubmit={handle2FASubmit} className="space-y-5">
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm"
                    >
                      {error}
                    </motion.div>
                  )}

                  <div>
                    <label className="label">Authentication Code</label>
                    <input
                      type="text"
                      value={totpCode}
                      onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="000000"
                      className="input-field text-center text-2xl tracking-widest font-mono"
                      maxLength={6}
                      autoFocus
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading || totpCode.length !== 6}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <Loader2 className="animate-spin" size={20} />
                    ) : (
                      <>
                        Verify & Sign In
                        <ArrowRight size={20} />
                      </>
                    )}
                  </button>
                </form>
              </motion.div>
            )}
          </AnimatePresence>

          {!requires2FA && (
            <div className="mt-6 text-center">
              <p className="text-espresso-500">
                Don't have an account?{' '}
                <Link to="/register" className="text-terracotta-600 font-medium hover:underline">
                  Sign up
                </Link>
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
