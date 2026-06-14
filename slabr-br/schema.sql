CREATE TABLE cards (
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

CREATE TABLE graded_items (
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

CREATE TABLE sets (
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

CREATE INDEX idx_cards_name   ON cards(name);

CREATE INDEX idx_cards_rarity ON cards(rarity);

CREATE INDEX idx_cards_set    ON cards(set_id);

CREATE INDEX idx_graded_card ON graded_items(card_id);
