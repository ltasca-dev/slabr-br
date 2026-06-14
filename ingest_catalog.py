#!/usr/bin/env python3
"""
Ingestão de catálogo — SLABR.br
================================
Puxa dados factuais de cartas (nome, set, número, raridade, data) da base
pública do Pokémon TCG e estrutura num catálogo SQLite pronto para a plataforma.

DESENHO IMPORTANTE (IP):
- A tabela `cards` é o CATÁLOGO de referência (dados factuais + URL da imagem
  oficial, usada só para referência/dev). NÃO baixamos as imagens.
- A tabela `graded_items` é o NOSSO ativo de produção: cada slab graduado, com
  o número de certificado, NOTA, subnotas e o caminho do NOSSO scan HD.
- A verificação pública (cert_id) faz JOIN: graded_items -> cards -> sets.
  É exatamente o que o MVP de verificação consome.

Fonte de dados: repositório público PokemonTCG/pokemon-tcg-data (inglês).
Para PT/multilíngue, a mesma estrutura aceita ingestão da TCGdex com language='pt'.

Uso:
    python3 ingest_catalog.py --data ./pokemon-tcg-data --db ./pokemon_catalog.db
    python3 ingest_catalog.py --limit 5      # ingere só 5 sets (teste rápido)
"""
import argparse, json, os, sqlite3, glob, datetime

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sets (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    series        TEXT,
    printed_total INTEGER,
    total         INTEGER,
    ptcgo_code    TEXT,
    release_date  TEXT,
    symbol_url    TEXT,
    logo_url      TEXT,
    language      TEXT NOT NULL DEFAULT 'en'
);

-- CATÁLOGO de referência (dados factuais vindos da API/base pública)
CREATE TABLE IF NOT EXISTS cards (
    id                     TEXT PRIMARY KEY,         -- ex.: base1-1
    set_id                 TEXT NOT NULL,
    name                   TEXT NOT NULL,
    number                 TEXT,                     -- número impresso na carta
    supertype              TEXT,                     -- Pokémon / Trainer / Energy
    subtypes               TEXT,                     -- json list
    rarity                 TEXT,
    types                  TEXT,                     -- json list
    national_pokedex_nums  TEXT,                     -- json list
    artist                 TEXT,
    flavor_text            TEXT,
    regulation_mark        TEXT,
    hp                     TEXT,
    release_date           TEXT,                     -- denormalizado do set
    official_image_small   TEXT,                     -- REFERÊNCIA (dev) — não rehospedar
    official_image_large   TEXT,                     -- REFERÊNCIA (dev) — não rehospedar
    language               TEXT NOT NULL DEFAULT 'en',
    ingested_at            TEXT,
    FOREIGN KEY (set_id) REFERENCES sets(id)
);
CREATE INDEX IF NOT EXISTS idx_cards_set    ON cards(set_id);
CREATE INDEX IF NOT EXISTS idx_cards_name   ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity);

-- PRODUÇÃO: cada slab graduado (NOSSO ativo). Liga o catálogo ao certificado.
CREATE TABLE IF NOT EXISTS graded_items (
    cert_id          TEXT PRIMARY KEY,               -- ex.: 0041-A77B (vai no slab/QR)
    card_id          TEXT,                           -- FK p/ catálogo (pode ser NULL p/ nichos sem catálogo)
    vertical         TEXT NOT NULL DEFAULT 'TCG',    -- TCG / Futebol BR / Figurinhas / Numismática...
    grade            REAL NOT NULL,
    gem              INTEGER NOT NULL DEFAULT 0,      -- 1 = GEM MINT 10
    sub_centering    REAL,
    sub_corners      REAL,
    sub_edges        REAL,
    sub_surface      REAL,
    scan_url_front   TEXT,                            -- NOSSO scan HD (ativo de produção)
    scan_url_back    TEXT,
    owner_handle     TEXT,
    declared_value_cents INTEGER,
    graded_at        TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(id)
);
CREATE INDEX IF NOT EXISTS idx_graded_card ON graded_items(card_id);
"""

def j(v):
    return json.dumps(v, ensure_ascii=False) if v is not None else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./pokemon-tcg-data")
    ap.add_argument("--db",   default="./pokemon_catalog.db")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--limit", type=int, default=0, help="ingerir só N sets (0 = todos)")
    args = ap.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    con = sqlite3.connect(args.db)
    con.executescript(SCHEMA)
    cur = con.cursor()

    # --- sets ---
    sets = json.load(open(os.path.join(args.data, "sets", f"{args.lang}.json"), encoding="utf-8"))
    set_release = {}
    for s in sets:
        imgs = s.get("images", {})
        set_release[s["id"]] = s.get("releaseDate")
        cur.execute("""INSERT OR REPLACE INTO sets
            (id,name,series,printed_total,total,ptcgo_code,release_date,symbol_url,logo_url,language)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (s["id"], s.get("name"), s.get("series"), s.get("printedTotal"), s.get("total"),
             s.get("ptcgoCode"), s.get("releaseDate"), imgs.get("symbol"), imgs.get("logo"), args.lang))

    # --- cards ---
    card_files = sorted(glob.glob(os.path.join(args.data, "cards", args.lang, "*.json")))
    if args.limit:
        card_files = card_files[:args.limit]

    n_cards = 0
    for cf in card_files:
        set_id = os.path.splitext(os.path.basename(cf))[0]
        cards = json.load(open(cf, encoding="utf-8"))
        rows = []
        for c in cards:
            imgs = c.get("images", {})
            rows.append((
                c["id"], set_id, c.get("name"), c.get("number"), c.get("supertype"),
                j(c.get("subtypes")), c.get("rarity"), j(c.get("types")),
                j(c.get("nationalPokedexNumbers")), c.get("artist"), c.get("flavorText"),
                c.get("regulationMark"), c.get("hp"), set_release.get(set_id),
                imgs.get("small"), imgs.get("large"), args.lang, now))
        cur.executemany("""INSERT OR REPLACE INTO cards
            (id,set_id,name,number,supertype,subtypes,rarity,types,national_pokedex_nums,
             artist,flavor_text,regulation_mark,hp,release_date,
             official_image_small,official_image_large,language,ingested_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
        n_cards += len(rows)

    con.commit()

    # --- demo: 2 itens graduados ligando catálogo -> certificado (alimenta o MVP) ---
    demos = [
        ("0041-A77B", "base1-4", "TCG", 10, 1, 10, 10, 9.5, 10,
         "https://scans.slabr.br/0041-A77B-front.webp", "https://scans.slabr.br/0041-A77B-back.webp",
         "raf10", 2240000, now),   # base1-4 = Charizard (Base Set)
        ("0099-K3M2", "base1-2", "TCG", 9, 0, 9, 9, 9.5, 8.5,
         "https://scans.slabr.br/0099-K3M2-front.webp", "https://scans.slabr.br/0099-K3M2-back.webp",
         "colec_mg", 180000, now),  # base1-2 = Blastoise
    ]
    cur.executemany("""INSERT OR REPLACE INTO graded_items
        (cert_id,card_id,vertical,grade,gem,sub_centering,sub_corners,sub_edges,sub_surface,
         scan_url_front,scan_url_back,owner_handle,declared_value_cents,graded_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", demos)
    con.commit()

    # --- relatório ---
    print(f"Sets ingeridos:   {cur.execute('SELECT COUNT(*) FROM sets').fetchone()[0]}")
    print(f"Cartas ingeridas: {n_cards}")
    print(f"Itens graduados:  {cur.execute('SELECT COUNT(*) FROM graded_items').fetchone()[0]}")
    con.close()

if __name__ == "__main__":
    main()
