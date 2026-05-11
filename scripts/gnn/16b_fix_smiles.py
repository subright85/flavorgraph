"""
Fix: PubChem returns 'SMILES' key not 'IsomericSMILES'.
Re-fetch SMILES and update DB + JSON. Uses batch CID lookup for speed.
"""

import sqlite3, json, os, time, re
import urllib.request, urllib.parse

DB_PATH  = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
OUT_PATH = os.path.join(os.path.dirname(__file__), '../../data/compound_smiles.json')


def classify_compound(smiles):
    if not smiles:
        return 'unknown'
    s = smiles
    # Sulfur-containing (garlic, onion flavor)
    if 'S' in s:
        return 'sulfur'
    # Nitrogen
    if 'N' in s:
        return 'nitrogen'
    # Aromatic ring
    if 'c1' in s or 'C1=CC=' in s:
        if 'O' in s:
            return 'phenol'
        return 'aromatic'
    # Ester: -C(=O)O- (not at end)
    if re.search(r'C\(=O\)O[^)H]', s) or re.search(r'OC\(=O\)', s):
        return 'ester'
    # Lactone (cyclic ester)
    if re.search(r'C\(=O\)O\d', s) or re.search(r'OC\(=O\)\d', s):
        return 'lactone'
    # Aldehyde: ends C=O or has CHO
    if s.endswith('C=O') or re.search(r'\[H\]C=O', s):
        return 'aldehyde'
    # Ketone: C(=O) interior
    if re.search(r'[^O]C\(=O\)[^O]', s):
        return 'ketone'
    # Carboxylic acid
    if s.endswith('C(=O)O') or s.endswith('C(O)=O') or 'C(=O)O)' in s:
        return 'acid'
    # Terpene heuristic: no oxygen, C≥10, has C=C
    formula_c = len(re.findall(r'C', s.split('O')[0]))
    if 'O' not in s and 'C=C' in s and formula_c >= 8:
        return 'terpene'
    # Alcohol: -OH
    if 'O)' in s or s.endswith('O') or 'CO' in s:
        return 'alcohol'
    return 'other'


def fetch_smiles_batch(cas_list, name_list):
    """Fetch SMILES one-by-one using CAS (faster than name)."""
    results = {}
    for cas, name in zip(cas_list, name_list):
        identifier = cas if cas else name.replace('_', ' ')
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(identifier)}/property/CanonicalSMILES,MolecularFormula/JSON"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FlavorGraph/1.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
            props = data['PropertyTable']['Properties'][0]
            smiles = props.get('CanonicalSMILES', props.get('SMILES', ''))
            results[name] = smiles
        except Exception:
            results[name] = ''
        time.sleep(0.22)
    return results


def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, cas FROM compound ORDER BY id")
    compounds = cur.fetchall()

    with open(OUT_PATH) as f:
        cache = json.load(f)

    print(f"Re-fetching SMILES for {len(compounds)} compounds...")
    found, failed = 0, 0

    for i, (cid, name, cas) in enumerate(compounds):
        identifier = cas if cas else name.replace('_', ' ')
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(identifier)}/property/CanonicalSMILES/JSON"
        smiles = ''
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FlavorGraph/1.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
            props = data['PropertyTable']['Properties'][0]
            smiles = props.get('CanonicalSMILES', props.get('SMILES', ''))
            found += 1
        except Exception:
            failed += 1
        time.sleep(0.22)

        fc = classify_compound(smiles)
        cur.execute("UPDATE compound SET smiles=?, flavor_class=? WHERE id=?",
                    (smiles, fc, cid))

        if name in cache:
            cache[name]['smiles'] = smiles
            cache[name]['flavor_class'] = fc

        if (i+1) % 50 == 0:
            conn.commit()
            print(f"  {i+1}/{len(compounds)} — found: {found}, failed: {failed}")

    conn.commit()
    conn.close()

    with open(OUT_PATH, 'w') as f:
        json.dump(cache, f, indent=2)

    print(f"\nDone. SMILES found: {found}, failed: {failed}")

    # Class distribution
    from collections import Counter
    cur2 = sqlite3.connect(DB_PATH).cursor()
    cur2.execute("SELECT flavor_class, COUNT(*) FROM compound GROUP BY flavor_class ORDER BY COUNT(*) DESC")
    print("\nFlavor class distribution:")
    for cls, cnt in cur2.fetchall():
        print(f"  {cls:<20} {cnt:>4}")


if __name__ == '__main__':
    run()
