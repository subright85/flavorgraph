"""
Fetch SMILES + molecular properties from PubChem for all 822 compounds.

Uses CAS number (available in DB) → PubChem REST API.
Saves to data/compound_smiles.json and updates DB compound table.

PubChem rate limit: ~5 req/sec → 0.25s sleep between requests.
822 compounds ≈ 3-4 minutes.
"""

import sqlite3, json, os, sys, time, re
import urllib.request, urllib.error

DB_PATH  = os.path.join(os.path.dirname(__file__), '../../flavorgraph_v2.db')
OUT_PATH = os.path.join(os.path.dirname(__file__), '../../data/compound_smiles.json')

PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/IsomericSMILES,MolecularFormula,MolecularWeight,IUPACName/JSON"


def fetch_pubchem(identifier):
    url = PUBCHEM_URL.format(urllib.parse.quote(identifier))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FlavorGraph/1.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        props = data['PropertyTable']['Properties'][0]
        return {
            'smiles': props.get('IsomericSMILES', ''),
            'formula': props.get('MolecularFormula', ''),
            'weight': props.get('MolecularWeight', None),
            'iupac': props.get('IUPACName', ''),
        }
    except Exception:
        return None


def classify_compound(smiles, formula):
    """Rough flavor class from SMILES/formula patterns."""
    if not smiles:
        return 'unknown'
    s = smiles
    # Order matters — check specific before general
    if re.search(r'[SR]', s) or '-S-' in s or 'S(' in s:
        return 'sulfur'
    if 'N' in s and formula and 'N' in formula:
        return 'nitrogen'
    if re.search(r'C\(=O\)O[^H]', s) or re.search(r'OC\(=O\)', s):
        return 'ester'
    if re.search(r'C\(=O\)\[H\]', s) or re.search(r'\[H\]C=O', s) or s.endswith('C=O') or re.search(r'C=O$', s):
        return 'aldehyde'
    if re.search(r'C\(=O\)C', s) and 'O' not in s.replace('C(=O)', ''):
        return 'ketone'
    if re.search(r'C\(=O\)[^O]', s) and re.search(r'[^O]C\(=O\)', s):
        return 'ketone'
    if re.search(r'c1cc', s) or re.search(r'c1ccc', s):
        return 'aromatic_phenol' if 'O' in s else 'aromatic'
    if re.search(r'CC(C)=C', s) or re.search(r'C(/C=C/)', s) or (formula and formula.startswith('C') and 'H' in formula and 'O' not in formula and int(re.findall(r'C(\d+)', formula)[0] if re.findall(r'C(\d+)', formula) else ['0'])[0] >= 10):
        return 'terpene'
    if re.search(r'C\(=O\)O$', s) or re.search(r'CC\(=O\)O', s):
        return 'acid'
    if re.search(r'CO$', s) or re.search(r'CCO', s) or re.search(r'\[OH\]', s):
        return 'alcohol'
    if re.search(r'C=C', s):
        return 'alkene'
    return 'other'


def run():
    import urllib.parse

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Add columns if not exist
    try:
        cur.execute("ALTER TABLE compound ADD COLUMN smiles TEXT")
        cur.execute("ALTER TABLE compound ADD COLUMN formula TEXT")
        cur.execute("ALTER TABLE compound ADD COLUMN mol_weight REAL")
        cur.execute("ALTER TABLE compound ADD COLUMN flavor_class TEXT")
        conn.commit()
        print("Added smiles/formula/mol_weight/flavor_class columns to compound table.")
    except sqlite3.OperationalError:
        print("Columns already exist.")

    cur.execute("SELECT id, name, cas FROM compound ORDER BY id")
    compounds = cur.fetchall()
    print(f"Fetching {len(compounds)} compounds from PubChem...")

    results = {}
    found, not_found = 0, 0

    for i, (cid, name, cas) in enumerate(compounds):
        # Try CAS first, then name
        data = None
        if cas:
            data = fetch_pubchem(cas)
            time.sleep(0.22)
        if data is None:
            data = fetch_pubchem(name.replace('_', ' '))
            time.sleep(0.22)

        if data:
            fc = classify_compound(data['smiles'], data['formula'])
            cur.execute("""
                UPDATE compound SET smiles=?, formula=?, mol_weight=?, flavor_class=?
                WHERE id=?
            """, (data['smiles'], data['formula'], data['weight'], fc, cid))
            results[name] = {**data, 'cas': cas, 'flavor_class': fc}
            found += 1
        else:
            not_found += 1
            results[name] = {'smiles': '', 'formula': '', 'weight': None, 'flavor_class': 'unknown', 'cas': cas}

        if (i+1) % 50 == 0:
            conn.commit()
            print(f"  {i+1}/{len(compounds)} — found: {found}, not found: {not_found}")

    conn.commit()
    conn.close()

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Found: {found}, not found: {not_found}")
    print(f"Saved to {OUT_PATH}")

    # Summary by flavor class
    from collections import Counter
    cls_counts = Counter(v['flavor_class'] for v in results.values())
    print("\nFlavor class distribution:")
    for cls, cnt in cls_counts.most_common():
        print(f"  {cls:<20} {cnt:>4}")


if __name__ == '__main__':
    run()
