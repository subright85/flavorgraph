// Curated Unsplash food-photography URLs for the 20 ingredients in the
// FlavorGraph database. Single-source for visual consistency — Wikipedia
// thumbnails were inconsistent (some product shots, some raw plants),
// which broke the cinematic glass-morphism look.
//
// All URLs verified 200 OK on 2026-05-04. Format:
//   https://images.unsplash.com/photo-<id>?w=600&q=80&auto=format&fit=crop
// (no API key needed; Unsplash CDN is public).
export const KNOWN_IMAGES: Record<string, string> = {
  "chocolate":   "https://images.unsplash.com/photo-1511381939415-e44015466834?w=600&q=80&auto=format&fit=crop",
  "blue cheese": "https://images.unsplash.com/photo-1452195100486-9cc805987862?w=600&q=80&auto=format&fit=crop",
  "strawberry":  "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=600&q=80&auto=format&fit=crop",
  "coffee":      "https://images.unsplash.com/photo-1690983323458-ec4a54fc9552?w=600&q=80&auto=format&fit=crop",
  "vanilla":     "https://images.unsplash.com/photo-1592788174877-3f99727fd23d?w=600&q=80&auto=format&fit=crop",
  "lamb":        "https://images.unsplash.com/photo-1630334337820-84afb05acf3a?w=600&q=80&auto=format&fit=crop",
  "salmon":      "https://images.unsplash.com/photo-1559058789-672da06263d8?w=600&q=80&auto=format&fit=crop",
  "truffle":     "https://images.unsplash.com/photo-1606419093310-d5ef610cc381?w=600&q=80&auto=format&fit=crop",
  "parmesan":    "https://images.unsplash.com/photo-1655662844300-e59c3d2e7587?w=600&q=80&auto=format&fit=crop",
  "tomato":      "https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=600&q=80&auto=format&fit=crop",
  "basil":       "https://images.unsplash.com/photo-1629157247277-48f870757026?w=600&q=80&auto=format&fit=crop",
  "garlic":      "https://images.unsplash.com/photo-1579705744772-f26014b5e084?w=600&q=80&auto=format&fit=crop",
  "butter":      "https://images.unsplash.com/photo-1603596310923-dbb12732f9c7?w=600&q=80&auto=format&fit=crop",
  "caramel":     "https://images.unsplash.com/photo-1653750660628-49a3414cf892?w=600&q=80&auto=format&fit=crop",
  "lemon":       "https://images.unsplash.com/photo-1590502593747-42a996133562?w=600&q=80&auto=format&fit=crop",
  "rose":        "https://images.unsplash.com/photo-1612185290152-5c5862fcc167?w=600&q=80&auto=format&fit=crop",
  "oyster":      "https://images.unsplash.com/photo-1717251752308-2ef72f07484e?w=600&q=80&auto=format&fit=crop",
  "lavender":    "https://images.unsplash.com/photo-1528756514091-dee5ecaa3278?w=600&q=80&auto=format&fit=crop",
  "cucumber":    "https://images.unsplash.com/photo-1589621316382-008455b857cd?w=600&q=80&auto=format&fit=crop",
  "mint":        "https://images.unsplash.com/photo-1600223933926-70910c9229e2?w=600&q=80&auto=format&fit=crop",
};

// Runtime cache for any future lookups (kept for compatibility).
const runtimeCache = new Map<string, string>();

export function getCachedImage(name: string): string | undefined {
  return KNOWN_IMAGES[name] ?? runtimeCache.get(name);
}

export function setCachedImage(name: string, url: string) {
  runtimeCache.set(name, url);
}
