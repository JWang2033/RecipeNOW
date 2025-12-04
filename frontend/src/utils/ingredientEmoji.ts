// Utility function to get emoji for ingredient names

const emojiMap: Record<string, string> = {
  // Proteins
  egg: '🥚',
  eggs: '🥚',
  chicken: '🍗',
  beef: '🥩',
  steak: '🥩',
  pork: '🥓',
  bacon: '🥓',
  fish: '🐟',
  salmon: '🐟',
  tuna: '🐟',
  shrimp: '🦐',
  prawn: '🦐',
  crab: '🦀',
  lobster: '🦞',
  
  // Vegetables
  tomato: '🍅',
  onion: '🧅',
  garlic: '🧄',
  carrot: '🥕',
  potato: '🥔',
  broccoli: '🥦',
  lettuce: '🥬',
  spinach: '🥬',
  kale: '🥬',
  cabbage: '🥬',
  pepper: '🌶️',
  chili: '🌶️',
  cucumber: '🥒',
  zucchini: '🥒',
  eggplant: '🍆',
  mushroom: '🍄',
  corn: '🌽',
  pea: '🫛',
  bean: '🫘',
  
  // Fruits
  apple: '🍎',
  banana: '🍌',
  orange: '🍊',
  lemon: '🍋',
  lime: '🍋',
  grape: '🍇',
  strawberry: '🍓',
  blueberry: '🫐',
  cherry: '🍒',
  peach: '🍑',
  pear: '🍐',
  watermelon: '🍉',
  melon: '🍈',
  pineapple: '🍍',
  mango: '🥭',
  coconut: '🥥',
  avocado: '🥑',
  kiwi: '🥝',
  grapefruit: '🍊',
  
  // Dairy
  milk: '🥛',
  cheese: '🧀',
  butter: '🧈',
  yogurt: '🥛',
  cream: '🥛',
  
  // Grains & Carbs
  rice: '🍚',
  bread: '🍞',
  pasta: '🍝',
  noodle: '🍜',
  flour: '🌾',
  wheat: '🌾',
  oat: '🌾',
  
  // Nuts & Seeds
  peanut: '🥜',
  almond: '🥜',
  walnut: '🥜',
  cashew: '🥜',
  nut: '🥜',
  
  // Seasonings & Condiments
  salt: '🧂',
  oil: '🫒',
  olive: '🫒',
  honey: '🍯',
  sugar: '🍬',
  vinegar: '🍶',
  soy: '🥫',
  sauce: '🥫',
  
  // Herbs
  basil: '🌿',
  mint: '🌿',
  parsley: '🌿',
  cilantro: '🌿',
  herb: '🌿',
  ginger: '🫚',
  turmeric: '🫚',
  
  // Beverages
  coffee: '☕',
  tea: '🍵',
  wine: '🍷',
  beer: '🍺',
  juice: '🧃',
  water: '💧',
  
  // Baked goods
  cake: '🍰',
  cookie: '🍪',
  pie: '🥧',
  donut: '🍩',
  
  // Other
  chocolate: '🍫',
  ice: '🧊',
  soup: '🍲',
  salad: '🥗',
  sandwich: '🥪',
  pizza: '🍕',
  taco: '🌮',
  burrito: '🌯',
  sushi: '🍣',
  tofu: '🧈',
};

export function getIngredientEmoji(name: string): string {
  const lowercaseName = name.toLowerCase();
  
  // Check for exact or partial matches
  for (const [key, emoji] of Object.entries(emojiMap)) {
    if (lowercaseName.includes(key)) {
      return emoji;
    }
  }
  
  // Default emoji
  return '🥬';
}

export default getIngredientEmoji;
