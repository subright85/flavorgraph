import Database from "better-sqlite3";
import path from "path";

const DB_PATH = path.join(process.cwd(), "flavorgraph.db");

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH);
    _db.pragma("journal_mode = WAL");
    initSchema(_db);
  }
  return _db;
}

function initSchema(db: Database.Database) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS ingredient (
      id       INTEGER PRIMARY KEY AUTOINCREMENT,
      name     TEXT NOT NULL UNIQUE,
      category TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS compound (
      id   INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      cas  TEXT
    );
    CREATE TABLE IF NOT EXISTS ingredient_compound (
      ingredient_id INTEGER REFERENCES ingredient(id),
      compound_id   INTEGER REFERENCES compound(id),
      PRIMARY KEY (ingredient_id, compound_id)
    );
    CREATE INDEX IF NOT EXISTS idx_ic_ingredient ON ingredient_compound(ingredient_id);
    CREATE INDEX IF NOT EXISTS idx_ic_compound   ON ingredient_compound(compound_id);

    CREATE TABLE IF NOT EXISTS pair_score (
      ing_a            TEXT    NOT NULL,
      ing_b            TEXT    NOT NULL,
      score            INTEGER NOT NULL,
      shared_count     INTEGER NOT NULL,
      shared_compounds TEXT    NOT NULL,
      total_count      INTEGER NOT NULL,
      PRIMARY KEY (ing_a, ing_b)
    );
    CREATE INDEX IF NOT EXISTS idx_pair_score_a ON pair_score(ing_a, score DESC);

    CREATE TABLE IF NOT EXISTS triplet_score (
      ing_a            TEXT    NOT NULL,
      ing_b            TEXT    NOT NULL,
      ing_c            TEXT    NOT NULL,
      avg_pair_score   INTEGER NOT NULL,
      shared_count     INTEGER NOT NULL,
      shared_compounds TEXT    NOT NULL,
      PRIMARY KEY (ing_a, ing_b, ing_c)
    );
    CREATE INDEX IF NOT EXISTS idx_triplet_score ON triplet_score(avg_pair_score DESC, shared_count DESC);
  `);
}

export function isSeeded(): boolean {
  const db = getDb();
  const row = db.prepare("SELECT COUNT(*) as n FROM ingredient").get() as { n: number };
  return row.n > 0;
}

export function isPrecomputed(): boolean {
  const db = getDb();
  const row = db.prepare("SELECT COUNT(*) as n FROM pair_score").get() as { n: number };
  return row.n > 0;
}
