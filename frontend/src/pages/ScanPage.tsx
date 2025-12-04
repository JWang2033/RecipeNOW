import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  Upload, 
  Image, 
  X, 
  Check, 
  Loader2, 
  AlertCircle,
  Plus,
  Trash2,
  ArrowRight
} from 'lucide-react';
import { scanApi } from '../services/api';
import { usePantry } from '../contexts/PantryContext';
import { getIngredientEmoji } from '../utils/ingredientEmoji';

export default function ScanPage() {
  const [image, setImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [detectedIngredients, setDetectedIngredients] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [showResults, setShowResults] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const { addItems } = usePantry();
  const navigate = useNavigate();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = () => {
        setImage(reader.result as string);
      };
      reader.readAsDataURL(file);
      setDetectedIngredients([]);
      setShowResults(false);
      setError(null);
    }
  };

  const handleScan = async () => {
    if (!imageFile) return;
    
    setIsScanning(true);
    setError(null);
    
    try {
      const response = await scanApi.scanIngredients(imageFile);
      setDetectedIngredients(response.ingredients);
      setShowResults(true);
    } catch (err) {
      setError('Failed to scan image. Please try again.');
      console.error(err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleRemoveIngredient = (index: number) => {
    setDetectedIngredients((prev) => prev.filter((_, i) => i !== index));
  };

  const handleEditIngredient = (index: number) => {
    setEditingIndex(index);
    setEditValue(detectedIngredients[index]);
  };

  const handleSaveEdit = () => {
    if (editingIndex !== null && editValue.trim()) {
      setDetectedIngredients((prev) =>
        prev.map((item, i) => (i === editingIndex ? editValue.trim() : item))
      );
    }
    setEditingIndex(null);
    setEditValue('');
  };

  const handleAddManual = () => {
    const name = prompt('Enter ingredient name:');
    if (name?.trim()) {
      setDetectedIngredients((prev) => [...prev, name.trim()]);
    }
  };

  const handleConfirm = async () => {
    if (detectedIngredients.length > 0) {
      await addItems(detectedIngredients);
      navigate('/pantry');
    }
  };

  const handleReset = () => {
    setImage(null);
    setImageFile(null);
    setDetectedIngredients([]);
    setShowResults(false);
    setError(null);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Scan Ingredients</h1>
        <p className="text-espresso-500 mt-1">
          Take a photo or upload an image of your ingredients
        </p>
      </div>

      <div className="px-6">
        {/* Upload Section */}
        {!image && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Camera Button */}
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="w-full card hover:shadow-xl transition-all duration-300 hover:border-terracotta-200 group"
            >
              <div className="flex items-center gap-4">
                <div className="p-4 rounded-2xl bg-terracotta-100 text-terracotta-600 group-hover:scale-110 transition-transform">
                  <Camera size={28} />
                </div>
                <div className="text-left">
                  <h3 className="font-display font-semibold text-espresso-800">
                    Take Photo
                  </h3>
                  <p className="text-sm text-espresso-500">
                    Use your camera to capture ingredients
                  </p>
                </div>
              </div>
            </button>

            {/* Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full card hover:shadow-xl transition-all duration-300 hover:border-sage-200 group"
            >
              <div className="flex items-center gap-4">
                <div className="p-4 rounded-2xl bg-sage-100 text-sage-600 group-hover:scale-110 transition-transform">
                  <Upload size={28} />
                </div>
                <div className="text-left">
                  <h3 className="font-display font-semibold text-espresso-800">
                    Upload Image
                  </h3>
                  <p className="text-sm text-espresso-500">
                    Select a photo from your gallery
                  </p>
                </div>
              </div>
            </button>

            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={handleFileSelect}
            />
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileSelect}
            />

            {/* Info Card */}
            <div className="card bg-gradient-to-br from-cream-100 to-cream-200 border-cream-300">
              <div className="flex gap-3">
                <span className="text-2xl">📷</span>
                <div>
                  <h4 className="font-medium text-espresso-700 mb-1">Tips for best results</h4>
                  <ul className="text-sm text-espresso-500 space-y-1">
                    <li>• Spread ingredients on a clear surface</li>
                    <li>• Ensure good lighting</li>
                    <li>• Avoid blurry images</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Image Preview */}
        {image && !showResults && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-4"
          >
            <div className="relative rounded-2xl overflow-hidden shadow-lg">
              <img
                src={image}
                alt="Uploaded"
                className="w-full aspect-[4/3] object-cover"
              />
              <button
                onClick={handleReset}
                className="absolute top-3 right-3 p-2 bg-black/50 rounded-full text-white hover:bg-black/70 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

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

            <button
              onClick={handleScan}
              disabled={isScanning}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Analyzing image...
                </>
              ) : (
                <>
                  <Image size={20} />
                  Scan Ingredients
                </>
              )}
            </button>
          </motion.div>
        )}

        {/* Results */}
        <AnimatePresence>
          {showResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Image Thumbnail */}
              <div className="flex items-center gap-4">
                <div className="relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
                  <img
                    src={image!}
                    alt="Scanned"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-grow">
                  <h3 className="font-display font-semibold text-espresso-800">
                    Detected Ingredients
                  </h3>
                  <p className="text-sm text-espresso-500">
                    {detectedIngredients.length} item{detectedIngredients.length !== 1 ? 's' : ''} found
                  </p>
                </div>
                <button
                  onClick={handleReset}
                  className="text-espresso-400 hover:text-espresso-600"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Ingredients List */}
              <div className="card">
                {detectedIngredients.length === 0 ? (
                  <div className="text-center py-6">
                    <span className="text-4xl mb-3 block">🤔</span>
                    <p className="text-espresso-500">No ingredients detected</p>
                    <button
                      onClick={handleAddManual}
                      className="mt-3 text-terracotta-600 font-medium hover:underline"
                    >
                      Add manually
                    </button>
                  </div>
                ) : (
                  <ul className="space-y-2">
                    {detectedIngredients.map((ingredient, index) => (
                      <motion.li
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-center gap-3 p-3 bg-cream-50 rounded-xl group"
                      >
                        {editingIndex === index ? (
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onBlur={handleSaveEdit}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit()}
                            className="flex-grow px-3 py-1 rounded-lg border border-terracotta-300 focus:outline-none focus:border-terracotta-500"
                            autoFocus
                          />
                        ) : (
                          <>
                            <span className="text-lg">{getIngredientEmoji(ingredient)}</span>
                            <span
                              className="flex-grow text-espresso-700 cursor-pointer hover:text-terracotta-600"
                              onClick={() => handleEditIngredient(index)}
                            >
                              {ingredient}
                            </span>
                            <button
                              onClick={() => handleRemoveIngredient(index)}
                              className="opacity-0 group-hover:opacity-100 p-1.5 text-espresso-400 hover:text-red-500 transition-all"
                            >
                              <Trash2 size={16} />
                            </button>
                          </>
                        )}
                      </motion.li>
                    ))}
                  </ul>
                )}

                {/* Add Manual Button */}
                <button
                  onClick={handleAddManual}
                  className="mt-4 w-full flex items-center justify-center gap-2 py-3 border-2 border-dashed border-cream-300 rounded-xl text-espresso-500 hover:border-terracotta-300 hover:text-terracotta-600 transition-colors"
                >
                  <Plus size={18} />
                  Add ingredient manually
                </button>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button onClick={handleReset} className="btn-outline flex-1">
                  Scan Again
                </button>
                <button
                  onClick={handleConfirm}
                  disabled={detectedIngredients.length === 0}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <Check size={18} />
                  Add to Pantry
                  <ArrowRight size={18} />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
