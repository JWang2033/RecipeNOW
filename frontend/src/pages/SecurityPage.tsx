import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  ShieldCheck, 
  ShieldOff,
  Loader2, 
  AlertCircle,
  Check,
  Copy,
  Smartphone,
  Key
} from 'lucide-react';
import { twoFAApi } from '../services/api';

interface SetupData {
  secret: string;
  qr_code: string;
  manual_entry_key: string;
}

export default function SecurityPage() {
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Setup state
  const [showSetup, setShowSetup] = useState(false);
  const [setupData, setSetupData] = useState<SetupData | null>(null);
  const [verifyCode, setVerifyCode] = useState('');
  
  // Disable state
  const [showDisable, setShowDisable] = useState(false);
  const [disableCode, setDisableCode] = useState('');
  
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const status = await twoFAApi.getStatus();
      setIs2FAEnabled(status.is_enabled);
    } catch (err) {
      setError('Failed to fetch 2FA status');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartSetup = async () => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const data = await twoFAApi.setup();
      setSetupData(data);
      setShowSetup(true);
    } catch (err) {
      setError('Failed to generate 2FA setup. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVerifyAndEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError(null);
    
    try {
      await twoFAApi.verify(verifyCode);
      setIs2FAEnabled(true);
      setShowSetup(false);
      setSetupData(null);
      setVerifyCode('');
      setSuccess('Two-factor authentication has been enabled!');
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError('Invalid verification code. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError(null);
    
    try {
      await twoFAApi.disable(disableCode);
      setIs2FAEnabled(false);
      setShowDisable(false);
      setDisableCode('');
      setSuccess('Two-factor authentication has been disabled.');
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError('Invalid verification code. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
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
        <h1 className="page-title">Security Settings</h1>
        <p className="text-espresso-500 mt-1">
          Protect your account with two-factor authentication
        </p>
      </div>

      <div className="px-6 space-y-4">
        {/* Success Message */}
        <AnimatePresence>
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center gap-3 bg-sage-50 text-sage-700 px-4 py-3 rounded-xl"
            >
              <Check size={20} />
              <span>{success}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center gap-3 bg-red-50 text-red-600 px-4 py-3 rounded-xl"
            >
              <AlertCircle size={20} />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 2FA Status Card */}
        <div className="card">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-xl ${is2FAEnabled ? 'bg-sage-100' : 'bg-cream-200'}`}>
              {is2FAEnabled ? (
                <ShieldCheck className="text-sage-600" size={28} />
              ) : (
                <Shield className="text-espresso-400" size={28} />
              )}
            </div>
            <div className="flex-grow">
              <h3 className="font-display font-semibold text-espresso-800">
                Two-Factor Authentication
              </h3>
              <p className={`text-sm ${is2FAEnabled ? 'text-sage-600' : 'text-espresso-500'}`}>
                {is2FAEnabled ? 'Enabled - Your account is protected' : 'Not enabled'}
              </p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              is2FAEnabled 
                ? 'bg-sage-100 text-sage-700' 
                : 'bg-cream-200 text-espresso-600'
            }`}>
              {is2FAEnabled ? 'Active' : 'Inactive'}
            </div>
          </div>
        </div>

        {/* Enable/Disable Button */}
        {!showSetup && !showDisable && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {is2FAEnabled ? (
              <button
                onClick={() => setShowDisable(true)}
                className="w-full card hover:shadow-lg transition-all group border-red-100 hover:border-red-200"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-red-100 rounded-xl text-red-600 group-hover:scale-110 transition-transform">
                    <ShieldOff size={24} />
                  </div>
                  <div className="text-left">
                    <h4 className="font-medium text-espresso-800">Disable 2FA</h4>
                    <p className="text-sm text-espresso-500">
                      Remove two-factor authentication from your account
                    </p>
                  </div>
                </div>
              </button>
            ) : (
              <button
                onClick={handleStartSetup}
                disabled={isProcessing}
                className="w-full card bg-gradient-to-r from-sage-500 to-sage-600 text-white hover:from-sage-600 hover:to-sage-700 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/20 rounded-xl group-hover:scale-110 transition-transform">
                    {isProcessing ? (
                      <Loader2 className="animate-spin" size={24} />
                    ) : (
                      <ShieldCheck size={24} />
                    )}
                  </div>
                  <div className="text-left">
                    <h4 className="font-medium">Enable Two-Factor Authentication</h4>
                    <p className="text-sm text-sage-100">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                </div>
              </button>
            )}
          </motion.div>
        )}

        {/* Setup Flow */}
        <AnimatePresence>
          {showSetup && setupData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Step 1: Install Authenticator */}
              <div className="card">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-terracotta-100 text-terracotta-600 flex items-center justify-center font-semibold">
                    1
                  </div>
                  <div>
                    <h4 className="font-medium text-espresso-800 mb-1">
                      Install an Authenticator App
                    </h4>
                    <p className="text-sm text-espresso-500">
                      Download Google Authenticator, Authy, or any TOTP-compatible app on your phone.
                    </p>
                  </div>
                </div>
              </div>

              {/* Step 2: Scan QR Code */}
              <div className="card">
                <div className="flex items-start gap-4 mb-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-terracotta-100 text-terracotta-600 flex items-center justify-center font-semibold">
                    2
                  </div>
                  <div>
                    <h4 className="font-medium text-espresso-800 mb-1">
                      Scan QR Code
                    </h4>
                    <p className="text-sm text-espresso-500">
                      Open your authenticator app and scan this QR code:
                    </p>
                  </div>
                </div>

                <div className="flex justify-center mb-4">
                  <img 
                    src={setupData.qr_code} 
                    alt="2FA QR Code" 
                    className="w-48 h-48 rounded-xl border-4 border-cream-200"
                  />
                </div>

                {/* Manual Entry */}
                <div className="bg-cream-50 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Key size={16} className="text-espresso-500" />
                    <span className="text-sm font-medium text-espresso-700">
                      Can't scan? Enter this code manually:
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="flex-grow bg-white px-3 py-2 rounded-lg font-mono text-sm text-espresso-700 border border-cream-200">
                      {setupData.manual_entry_key}
                    </code>
                    <button
                      onClick={() => copyToClipboard(setupData.manual_entry_key)}
                      className="p-2 text-espresso-500 hover:text-terracotta-600 hover:bg-cream-100 rounded-lg transition-colors"
                    >
                      {copied ? <Check size={18} /> : <Copy size={18} />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 3: Verify */}
              <div className="card">
                <div className="flex items-start gap-4 mb-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-terracotta-100 text-terracotta-600 flex items-center justify-center font-semibold">
                    3
                  </div>
                  <div>
                    <h4 className="font-medium text-espresso-800 mb-1">
                      Verify Setup
                    </h4>
                    <p className="text-sm text-espresso-500">
                      Enter the 6-digit code from your authenticator app:
                    </p>
                  </div>
                </div>

                <form onSubmit={handleVerifyAndEnable}>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={verifyCode}
                      onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="000000"
                      className="input-field flex-grow text-center text-xl tracking-widest font-mono"
                      maxLength={6}
                    />
                    <button
                      type="submit"
                      disabled={isProcessing || verifyCode.length !== 6}
                      className="btn-primary"
                    >
                      {isProcessing ? (
                        <Loader2 className="animate-spin" size={20} />
                      ) : (
                        'Verify'
                      )}
                    </button>
                  </div>
                </form>
              </div>

              {/* Cancel Button */}
              <button
                onClick={() => {
                  setShowSetup(false);
                  setSetupData(null);
                  setVerifyCode('');
                  setError(null);
                }}
                className="w-full text-center text-espresso-500 hover:text-espresso-700 py-3"
              >
                Cancel Setup
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Disable Flow */}
        <AnimatePresence>
          {showDisable && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="card border-red-100"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="p-2 bg-red-100 rounded-lg">
                  <AlertCircle className="text-red-600" size={20} />
                </div>
                <div>
                  <h4 className="font-medium text-espresso-800 mb-1">
                    Disable Two-Factor Authentication
                  </h4>
                  <p className="text-sm text-espresso-500">
                    Enter your current authentication code to disable 2FA:
                  </p>
                </div>
              </div>

              <form onSubmit={handleDisable}>
                <div className="flex gap-3 mb-4">
                  <input
                    type="text"
                    value={disableCode}
                    onChange={(e) => setDisableCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    className="input-field flex-grow text-center text-xl tracking-widest font-mono"
                    maxLength={6}
                  />
                  <button
                    type="submit"
                    disabled={isProcessing || disableCode.length !== 6}
                    className="px-6 py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
                  >
                    {isProcessing ? (
                      <Loader2 className="animate-spin" size={20} />
                    ) : (
                      'Disable'
                    )}
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setShowDisable(false);
                    setDisableCode('');
                    setError(null);
                  }}
                  className="w-full text-center text-espresso-500 hover:text-espresso-700 py-2"
                >
                  Cancel
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Info Card */}
        <div className="card bg-gradient-to-br from-cream-100 to-cream-200 border-cream-300">
          <div className="flex gap-3">
            <Smartphone className="text-espresso-500 flex-shrink-0" size={24} />
            <div>
              <h4 className="font-medium text-espresso-700 mb-1">
                Why use two-factor authentication?
              </h4>
              <p className="text-sm text-espresso-500">
                2FA adds an extra layer of security by requiring both your password and a code from your phone to sign in. This helps protect your account even if your password is compromised.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

