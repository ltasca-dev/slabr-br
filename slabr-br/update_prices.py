#!/usr/bin/env python3
"""
Atualiza preços de REFERÊNCIA (TCGplayer USD / Cardmarket EUR) no banco, via pokemontcg.io,
e mantém um HISTÓRICO diário (price_history) para o gráfico de mercado de preços.

Uso (na sua máquina, com internet):
    python3 update_prices.py                 # cartas do mercado (graded_items); grava 1 ponto/dia
    python3 update_prices.py --ids base1-4,base1-2
    python3 update_prices.py --limit 200
    POKEMONTCG_API_KEY=xxxx python3 update_prices.py

Demonstração (sem internet — semeia preço atual + série histórica com pico):
    python3 update_prices.py --demo

IMPORTANTE: é REFERÊNCIA INTERNACIONAL (US$/€), não preço de venda no Brasil.
A conversão p/ R$ (âncora) acontece na API (SLABR_USD_BRL / SLABR_EUR_BRL).
Confira a licença/termos da fonte antes de usar num produto comercial.
"""
import sqlite3, os, json, time, argparse, datetime, urllib.request, urllib.error

DB = os.environ.get("SLABR_DB", "pokemon_catalog.db")
API = "https://api.pokemontcg.io/v2/cards/"
KEY = os.environ.get("POKEMONTCG_API_KEY")
VARIANTS = ["holofoil","reverseHolofoil","1stEditionHolofoil","unlimitedHolofoil","normal","1stEdition"]

def ensure_tables(con):
    con.execute("""CREATE TABLE IF NOT EXISTS card_prices(
        card_id TEXT PRIMARY KEY, source TEXT, currency TEXT,
        market REAL, low REAL, high REAL, url TEXT,
        updated_at TEXT DEFAULT (datetime('now')))""")
    con.execute("""CREATE TABLE IF NOT EXISTS price_history(
        card_id TEXT, d TEXT, price REAL, currency TEXT,
        PRIMARY KEY(card_id, d))""")

def target_ids(con, args):
    if args.ids:
        return [x.strip() for x in args.ids.split(",") if x.strip()]
    ids = [r[0] for r in con.execute("SELECT DISTINCT card_id FROM graded_items")]
    return ids[:args.limit] if args.limit else ids

def fetch_card(cid):
    req = urllib.request.Request(API + cid)
    if KEY: req.add_header("X-Api-Key", KEY)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8")).get("data", {})

def extract_price(card):
    tp = (card.get("tcgplayer") or {}).get("prices") or {}
    for v in VARIANTS + list(tp.keys()):
        p = tp.get(v)
        if p and (p.get("market") or p.get("mid")):
            return ("TCGplayer","USD", p.get("market") or p.get("mid"),
                    p.get("low"), p.get("high"), (card.get("tcgplayer") or {}).get("url"))
    cm = (card.get("cardmarket") or {}).get("prices") or {}
    if cm.get("averageSellPrice") or cm.get("trendPrice"):
        return ("Cardmarket","EUR", cm.get("averageSellPrice") or cm.get("trendPrice"),
                cm.get("lowPrice"), cm.get("trendPrice"), (card.get("cardmarket") or {}).get("url"))
    return None

def upsert_current(con, cid, src, cur, market, low, high, url):
    con.execute("""INSERT INTO card_prices(card_id,source,currency,market,low,high,url,updated_at)
                   VALUES (?,?,?,?,?,?,?,datetime('now'))
                   ON CONFLICT(card_id) DO UPDATE SET
                     source=excluded.source,currency=excluded.currency,market=excluded.market,
                     low=excluded.low,high=excluded.high,url=excluded.url,updated_at=datetime('now')""",
                (cid,src,cur,market,low,high,url))

def add_history(con, cid, price, currency, d=None):
    d = d or datetime.date.today().isoformat()
    con.execute("""INSERT INTO price_history(card_id,d,price,currency) VALUES (?,?,?,?)
                   ON CONFLICT(card_id,d) DO UPDATE SET price=excluded.price,currency=excluded.currency""",
                (cid, d, price, currency))

def run_live(args):
    con = sqlite3.connect(DB); ensure_tables(con)
    ids = target_ids(con, args)
    print(f"Atualizando {len(ids)} carta(s) via pokemontcg.io" + (" (com API key)" if KEY else " (sem key)"))
    ok=miss=err=0
    for i,cid in enumerate(ids,1):
        try:
            card=fetch_card(cid); pr=extract_price(card)
            if pr:
                upsert_current(con,cid,*pr); add_history(con,cid,pr[2],pr[1]); ok+=1
                print(f"  [{i}/{len(ids)}] {cid}: {pr[1]} {pr[2]} ({pr[0]})")
            else:
                miss+=1; print(f"  [{i}/{len(ids)}] {cid}: sem preço")
        except urllib.error.HTTPError as e:
            err+=1; print(f"  [{i}/{len(ids)}] {cid}: HTTP {e.code}")
            if e.code==429: time.sleep(10)
        except Exception as e:
            err+=1; print(f"  [{i}/{len(ids)}] {cid}: {e}")
        if i%20==0: con.commit()
        time.sleep(0.0 if KEY else 0.25)
    con.commit(); con.close()
    print(f"Pronto. ok={ok} sem_preço={miss} erros={err}")

def run_demo(args):
    import random
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; ensure_tables(con)
    rows=con.execute("SELECT DISTINCT c.id,c.rarity FROM graded_items g JOIN cards c ON c.id=g.card_id").fetchall()
    def base(rar):
        r=(rar or "").lower()
        if "secret" in r or "illustration" in r: return random.uniform(8,16)
        if "ultra" in r or "hyper" in r: return random.uniform(5,11)
        if "holo" in r or "rare" in r: return random.uniform(3,8)
        if "uncommon" in r: return random.uniform(1,3)
        return random.uniform(0.4,1.5)
    N=42; today=datetime.date.today(); n=0
    for r in rows:
        b=base(r["rarity"]); spike=random.randint(8,26)  # índice (a partir do fim) do pico
        series=[]
        for i in range(N):
            d=today - datetime.timedelta(days=(N-1-i)*2)   # 1 ponto a cada 2 dias (~84 dias)
            v=b*random.uniform(0.8,1.2)
            dist=abs((N-1-i)-spike)
            if dist==0: v=b*random.uniform(8,13)
            elif dist==1: v=b*random.uniform(2.5,4.5)
            series.append((d.isoformat(), round(max(0.1,v),2)))
        for d,v in series:
            add_history(con, r["id"], v, "EUR", d)
        last=series[-1][1]
        lows=min(x[1] for x in series); highs=max(x[1] for x in series)
        upsert_current(con, r["id"], "demo (placeholder)", "EUR", last, round(lows,2), round(highs,2), "https://www.cardmarket.com/")
        n+=1
    con.commit(); con.close()
    print(f"[demo] série histórica + preço atual semeados p/ {n} carta(s) (€, com pico). Troque rodando sem --demo.")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--demo",action="store_true")
    ap.add_argument("--ids")
    ap.add_argument("--limit",type=int)
    args=ap.parse_args()
    (run_demo if args.demo else run_live)(args)
