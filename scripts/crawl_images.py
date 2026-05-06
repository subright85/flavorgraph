#!/usr/bin/env python3
"""
Crawl OpenVerse API for CC0 food images.
Saves: data/ingredient_images.json  (merge with KNOWN_IMAGES)
"""
import json, time, urllib.request, urllib.parse, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
INGREDIENTS_FILE = ROOT / "data/top300_ingredients.json"
OUTPUT_FILE = ROOT / "data/ingredient_images.json"

KNOWN = {
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
}

def openverse_url(ingredient: str):
    q = urllib.parse.quote(f"{ingredient} food")
    url = f"https://api.openverse.org/v1/images/?q={q}&license=cc0&page_size=3&category=photograph"
    req = urllib.request.Request(url, headers={"User-Agent": "FlavorGraph/1.0 (research)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        # use direct image url (not thumbnail which is an OpenVerse proxy)
        for r in results:
            img_url = r.get("url", "")
            if img_url and not img_url.startswith("https://api.openverse.org"):
                return img_url
        if results:
            return results[0].get("url")
    except Exception as e:
        print(f"  ERR {ingredient}: {e}", file=sys.stderr)
    return None

def main():
    with open(INGREDIENTS_FILE) as f:
        all_ingredients = [item["name"] for item in json.load(f)]

    # load existing output if partial run
    result: dict[str, str] = dict(KNOWN)
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            result.update(json.load(f))

    needed = [i for i in all_ingredients if i not in result]
    print(f"Need to fetch: {len(needed)} ingredients")

    for idx, ingredient in enumerate(needed, 1):
        url = openverse_url(ingredient)
        if url:
            result[ingredient] = url
            print(f"[{idx}/{len(needed)}] ✓ {ingredient}")
        else:
            print(f"[{idx}/{len(needed)}] ✗ {ingredient} (no result)")
        # save incrementally every 10
        if idx % 10 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  → saved {len(result)} total")
        time.sleep(2)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nDone! {len(result)} images saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
