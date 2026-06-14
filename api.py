#!/usr/bin/env python3
"""
API SLABR.br - app + endpoints + CONTAS (cadastro/login) lendo/gravando no pokemon_catalog.db.
Rodar:
    pip install flask --break-system-packages
    python3 ingest_catalog.py     # (uma vez) constroi o catalogo, se ainda nao fez
    python3 api.py                # http://localhost:5000

Contas demo (senha: demo123): raf10, marina.sp, joao_v, ana.bea, lucas_rs, tcg_bsb
"""
import sqlite3, json, os, re, datetime
from flask import Flask, jsonify, request, g, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from scraper_bynx import BynxScraperSync

DB   = os.environ.get("SLABR_DB", "pokemon_catalog.db")
HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slabr_app.html")
app  = Flask(__name__)
app.secret_key = os.environ.get("SLABR_SECRET", "troque-este-segredo-em-producao")

# Fase 0: Integração Bynx.gg
_bynx_scraper = BynxScraperSync()
_price_cache = {}
_cache_ttl = 3600  # 1 hora

_SEED_JSON   = r"""[["5295-D71H", "swsh4-171", "TCG", 7, 0, 7, 7.5, 7, 7, null, "lucas_rs", 276000, "2026-03-01T12:00:00Z"], ["6445-F86E", "base1-4", "TCG", 7, 0, 7, 7, 7, 7, null, "joao_v", 336000, "2026-01-01T12:00:00Z"], ["3726-M65D", "swsh4-171", "TCG", 7, 0, 7, 7.5, 7, 7, null, "raf10", 259000, "2026-03-01T12:00:00Z"], ["3393-C71A", "base1-6", "TCG", 9.5, 0, 9.5, 10, 9.5, 9.5, null, "joao_v", 1384000, "2026-02-01T12:00:00Z"], ["3604-M73A", "base1-4", "TCG", 8.5, 0, 8.5, 9.0, 8.5, 8.5, null, "raf10", 690000, "2026-01-01T12:00:00Z"], ["1167-G97C", "base1-6", "TCG", 8, 0, 8, 8, 8, 8, null, "tcg_bsb", 488000, "2026-03-01T12:00:00Z"], ["1320-H30J", "base1-2", "TCG", 7, 0, 7, 7.5, 7, 7, null, "raf10", 394000, "2026-04-01T12:00:00Z"], ["9326-K51J", "base2-11", "TCG", 10, 1, 10, 10, 10, 10, null, "raf10", 2612000, "2026-03-01T12:00:00Z"], ["4812-M15G", "base1-1", "TCG", 9.5, 0, 9.5, 10, 9.5, 9.5, null, "marina.sp", 1522000, "2026-05-01T12:00:00Z"], ["8109-A41E", "base5-3", "TCG", 9.5, 0, 9.5, 10, 9.5, 9.5, null, "tcg_bsb", 1256000, "2026-06-01T12:00:00Z"], ["2108-C75B", "sv1-121", "TCG", 7, 0, 7, 7, 7, 7, null, "raf10", 11000, "2026-03-01T12:00:00Z"], ["4589-D74A", "sv1-121", "TCG", 8, 0, 8, 8.5, 8, 8, null, "joao_v", 14000, "2026-05-01T12:00:00Z"], ["6069-M47P", "base2-11", "TCG", 10, 1, 10, 10, 10, 10, null, "marina.sp", 2422000, "2026-05-01T12:00:00Z"], ["4105-B88P", "base2-11", "TCG", 7, 0, 7, 7.5, 7, 7, null, "lucas_rs", 377000, "2026-02-01T12:00:00Z"], ["3831-H57M", "base5-3", "TCG", 7, 0, 7, 7, 7, 7, null, "ana.bea", 329000, "2026-04-01T12:00:00Z"], ["5226-L47A", "base1-6", "TCG", 10, 1, 10, 10, 10, 10, null, "raf10", 2795000, "2026-02-01T12:00:00Z"], ["4637-K87F", "base1-4", "TCG", 8, 0, 8, 8, 8, 8, null, "lucas_rs", 529000, "2026-02-01T12:00:00Z"], ["5981-J51G", "base1-16", "TCG", 10, 1, 10, 10, 10, 10, null, "marina.sp", 2681000, "2026-02-01T12:00:00Z"], ["1563-F90P", "cel25-2", "TCG", 10, 1, 10, 10, 10, 10, null, "marina.sp", 511000, "2026-01-01T12:00:00Z"], ["2162-B81H", "base1-2", "TCG", 7, 0, 7, 7.5, 7, 7, null, "tcg_bsb", 408000, "2026-02-01T12:00:00Z"], ["5274-B13F", "swsh4-171", "TCG", 7, 0, 7, 7.5, 7, 7, null, "marina.sp", 267000, "2026-02-01T12:00:00Z"], ["7536-G51H", "base5-3", "TCG", 8.5, 0, 8.5, 8.5, 8.5, 8.5, null, "marina.sp", 724000, "2026-06-01T12:00:00Z"], ["9823-E62D", "sv1-121", "TCG", 10, 1, 10, 10, 10, 10, null, "joao_v", 67000, "2026-06-01T12:00:00Z"], ["3852-A57H", "sv1-121", "TCG", 8, 0, 8, 8.5, 8, 8, null, "tcg_bsb", 15000, "2026-02-01T12:00:00Z"], ["1608-H40B", "base1-2", "TCG", 8.5, 0, 8.5, 8.5, 8.5, 8.5, null, "tcg_bsb", 670000, "2026-02-01T12:00:00Z"], ["3872-B76E", "swsh4-171", "TCG", 7, 0, 7, 7.5, 7, 7, null, "lucas_rs", 239000, "2026-06-01T12:00:00Z"], ["1414-L67N", "base1-16", "TCG", 10, 1, 10, 10, 10, 10, null, "marina.sp", 2518000, "2026-01-01T12:00:00Z"], ["7668-C85A", "base1-4", "TCG", 8, 0, 8, 8.5, 8, 8, null, "marina.sp", 567000, "2026-04-01T12:00:00Z"], ["4688-K84H", "cel25-2", "TCG", 8.5, 0, 8.5, 8.5, 8.5, 8.5, null, "marina.sp", 171000, "2026-06-01T12:00:00Z"], ["2548-E34H", "cel25-2", "TCG", 10, 1, 10, 10, 10, 10, null, "marina.sp", 613000, "2026-01-01T12:00:00Z"], ["4085-C17H", "sv1-121", "TCG", 10, 1, 10, 10, 10, 10, null, "tcg_bsb", 66000, "2026-04-01T12:00:00Z"], ["8849-A37P", "base1-6", "TCG", 7, 0, 7, 7.5, 7, 7, null, "tcg_bsb", 368000, "2026-02-01T12:00:00Z"], ["8024-F30L", "base1-4", "TCG", 9.5, 0, 9.5, 9.5, 9.5, 9.5, null, "marina.sp", 1270000, "2026-06-01T12:00:00Z"], ["7190-D80N", "base1-16", "TCG", 8, 0, 8, 8, 8, 8, null, "marina.sp", 475000, "2026-05-01T12:00:00Z"], ["5608-H37N", "base1-1", "TCG", 8.5, 0, 8.5, 9.0, 8.5, 8.5, null, "tcg_bsb", 766000, "2026-05-01T12:00:00Z"], ["1928-N11G", "base1-16", "TCG", 7, 0, 7, 7.5, 7, 7, null, "tcg_bsb", 366000, "2026-01-01T12:00:00Z"], ["8252-H76J", "base2-11", "TCG", 8.5, 0, 8.5, 9.0, 8.5, 8.5, null, "raf10", 733000, "2026-04-01T12:00:00Z"], ["3501-E29F", "sv1-121", "TCG", 7, 0, 7, 7.5, 7, 7, null, "joao_v", 11000, "2026-03-01T12:00:00Z"], ["4822-E99K", "base2-11", "TCG", 8, 0, 8, 8.5, 8, 8, null, "tcg_bsb", 476000, "2026-06-01T12:00:00Z"], ["7899-E97G", "base1-6", "TCG", 8, 0, 8, 8, 8, 8, null, "marina.sp", 495000, "2026-02-01T12:00:00Z"], ["7710-E56H", "base1-2", "TCG", 9, 0, 9, 9.5, 9, 9, null, "lucas_rs", 1045000, "2026-03-01T12:00:00Z"], ["5545-M58C", "swsh4-171", "TCG", 7, 0, 7, 7.5, 7, 7, null, "marina.sp", 262000, "2026-04-01T12:00:00Z"], ["1104-C50D", "swsh4-171", "TCG", 8, 0, 8, 8.5, 8, 8, null, "lucas_rs", 358000, "2026-04-01T12:00:00Z"], ["5597-L32L", "swsh4-171", "TCG", 8.5, 0, 8.5, 9.0, 8.5, 8.5, null, "lucas_rs", 515000, "2026-05-01T12:00:00Z"], ["7523-K66M", "cel25-2", "TCG", 10, 1, 10, 10, 10, 10, null, "raf10", 554000, "2026-02-01T12:00:00Z"], ["1608-K73E", "sv1-121", "TCG", 9, 0, 9, 9.5, 9, 9, null, "marina.sp", 26000, "2026-02-01T12:00:00Z"], ["5028-C81B", "base1-4", "TCG", 8, 0, 8, 8.5, 8, 8, null, "marina.sp", 501000, "2026-04-01T12:00:00Z"], ["9849-H98B", "base1-1", "TCG", 8.5, 0, 8.5, 9.0, 8.5, 8.5, null, "joao_v", 649000, "2026-01-01T12:00:00Z"], ["8080-J16E", "cel25-2", "TCG", 9, 0, 9, 9, 9, 9, null, "lucas_rs", 186000, "2026-04-01T12:00:00Z"], ["8937-K71E", "base1-6", "TCG", 9, 0, 9, 9, 9, 9, null, "ana.bea", 971000, "2026-05-01T12:00:00Z"], ["1052-A57K", "base1-1", "TCG", 9.5, 0, 9.5, 10, 9.5, 9.5, null, "marina.sp", 1422000, "2026-01-01T12:00:00Z"], ["7885-B19L", "base2-11", "TCG", 9, 0, 9, 9, 9, 9, null, "tcg_bsb", 847000, "2026-06-01T12:00:00Z"]]"""
_OWNERS_JSON = r"""{"raf10": "Belo Horizonte, MG", "marina.sp": "São Paulo, SP", "joao_v": "Curitiba, PR", "ana.bea": "Recife, PE", "lucas_rs": "Porto Alegre, RS", "tcg_bsb": "Brasília, DF"}"""
SEED       = json.loads(_SEED_JSON)
OWNER_CITY = json.loads(_OWNERS_JSON)
DEMO_PW    = "demo123"
# Câmbio de referência (ajustável por env) — converte preço internacional p/ R$ APENAS como âncora
USD_BRL    = float(os.environ.get("SLABR_USD_BRL", "5.40"))
EUR_BRL    = float(os.environ.get("SLABR_EUR_BRL", "5.90"))

def gen_id(prefix):
    import random
    a="ABCDEFGHJKLMNP"; d=lambda: str(random.randint(1,9))
    return f"{prefix}{d()}{d()}{d()}{d()}-{random.choice(a)}{d()}{d()}{random.choice(a)}"

# ---------------- infra ----------------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db
@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d: d.close()

@app.after_request
def cors(resp):
    # servido na mesma origem; CORS permissivo so para conveniencia de leitura
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin","*")
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

def ctype(tj):
    if not tj: return "Colorless"
    try:
        a=json.loads(tj); return a[0] if a else "Colorless"
    except Exception: return "Colorless"

def card_row(r):
    return {"id":r["id"],"name":r["name"],"set":r["set_name"],"setId":r["set_id"],
            "num":r["number"],"rar":r["rarity"] or "Common","type":ctype(r["types"]),
            "y":(r["release_date"] or "")[:4]}

def graded_row(r):
    k=r.keys()
    return {"cert":r["cert_id"],"cardId":r["card_id"],"grade":r["grade"],"gem":bool(r["gem"]),
            "subs":{"cen":r["sub_centering"],"cor":r["sub_corners"],"edg":r["sub_edges"],"sur":r["sub_surface"]},
            "owner":r["owner_handle"],"value":(r["declared_value_cents"] or 0)/100,
            "scan":r["scan_url_front"],"public":bool(r["public"]) if "public" in k else True,
            "condition":(r["condition"] if "condition" in k else None),
            "qty":(r["qty"] if "qty" in k else 1) or 1,
            "graded":bool(r["graded"]) if "graded" in k else True,
            "forSale":bool(r["for_sale"]) if "for_sale" in k else False,
            "date":(r["graded_at"] or "")[:7]}

def current_user():
    return session.get("handle")
def auth_required():
    h=current_user()
    if not h: return None
    return h

# ---------------- migracao + seed ----------------
def migrate_and_seed():
    con=sqlite3.connect(DB)
    # coluna public em graded_items
    cols=[c[1] for c in con.execute("PRAGMA table_info(graded_items)")]
    if "public" not in cols:
        con.execute("ALTER TABLE graded_items ADD COLUMN public INTEGER DEFAULT 1")
        con.execute("UPDATE graded_items SET public=1 WHERE public IS NULL")
        print("[migra] coluna public adicionada em graded_items")
    # colunas de biblioteca (item da coleção do usuário, graduado ou não)
    if "condition" not in cols:
        con.execute("ALTER TABLE graded_items ADD COLUMN condition TEXT")
    if "qty" not in cols:
        con.execute("ALTER TABLE graded_items ADD COLUMN qty INTEGER DEFAULT 1")
    if "graded" not in cols:
        con.execute("ALTER TABLE graded_items ADD COLUMN graded INTEGER DEFAULT 1")
        con.execute("UPDATE graded_items SET graded=1 WHERE graded IS NULL")
        print("[migra] colunas condition/qty/graded adicionadas")
    if "for_sale" not in cols:
        con.execute("ALTER TABLE graded_items ADD COLUMN for_sale INTEGER DEFAULT 0")
        con.execute("UPDATE graded_items SET for_sale=1 WHERE for_sale IS NULL")  # seed antigo = à venda
        print("[migra] coluna for_sale adicionada")
    # pedidos de graduação (colecionador solicita autenticação de uma carta da biblioteca)
    con.execute("""CREATE TABLE IF NOT EXISTS grading_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT, protocol TEXT, owner_handle TEXT,
        item_cert TEXT, card_id TEXT, status TEXT, checklist TEXT,
        declared_value_cents INTEGER, service TEXT, notes TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")
    # tabela users
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        handle TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, city TEXT,
        collection TEXT, pw_hash TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))""")
    # tabela card_prices (preço de referência externo)
    con.execute("""CREATE TABLE IF NOT EXISTS card_prices(
        card_id TEXT PRIMARY KEY, source TEXT, currency TEXT,
        market REAL, low REAL, high REAL, url TEXT,
        updated_at TEXT DEFAULT (datetime('now')))""")
    # histórico de preço de referência (série temporal p/ o gráfico)
    con.execute("""CREATE TABLE IF NOT EXISTS price_history(
        card_id TEXT, d TEXT, price REAL, currency TEXT,
        PRIMARY KEY(card_id, d))""")
    # seed graded (se vazio)
    n=con.execute("SELECT COUNT(*) FROM graded_items").fetchone()[0]
    if n < 10:
        con.executemany("""INSERT OR IGNORE INTO graded_items
          (cert_id,card_id,vertical,grade,gem,sub_centering,sub_corners,sub_edges,sub_surface,
           scan_url_front,owner_handle,declared_value_cents,graded_at,public)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,1)""", SEED)
        print(f"[seed] {len(SEED)} itens graduados de demonstracao")
    # seed users demo
    created=0
    for h,city in OWNER_CITY.items():
        ex=con.execute("SELECT 1 FROM users WHERE handle=?",(h,)).fetchone()
        if not ex:
            con.execute("INSERT INTO users(handle,name,email,city,collection,pw_hash) VALUES (?,?,?,?,?,?)",
                        (h,h,f"{h}@demo.slabr.br",city,"Figurinhas de futebol",generate_password_hash(DEMO_PW)))
            created+=1
    if created: print(f"[seed] {created} contas demo (senha: {DEMO_PW})")
    con.commit(); con.close()

# ---------------- app ----------------
@app.get("/")
def index():
    return Response(open(HTML, encoding="utf-8").read(), mimetype="text/html")

@app.get("/api/stats")
def stats():
    c=db()
    tot=c.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    n=c.execute("SELECT COUNT(*) FROM graded_items").fetchone()[0]
    val=c.execute("SELECT COALESCE(SUM(declared_value_cents),0) FROM graded_items").fetchone()[0]/100
    col=c.execute("SELECT COUNT(DISTINCT owner_handle) FROM graded_items").fetchone()[0]
    return jsonify({"catalog_total":tot,"graded":n,"value":val,"collectors":col})

@app.get("/api/cards")
def cards():
    q=request.args.get("q","").strip(); limit=min(int(request.args.get("limit",30)),60)
    sql="""SELECT c.id,c.name,s.name set_name,c.set_id,c.number,c.rarity,c.types,c.release_date,
                  (SELECT COUNT(*) FROM graded_items g WHERE g.card_id=c.id AND g.public=1) graded
           FROM cards c JOIN sets s ON s.id=c.set_id WHERE 1=1"""
    p=[]
    if q: sql+=" AND c.name LIKE ?"; p.append(f"%{q}%")
    sql+=" ORDER BY s.release_date, CAST(c.number AS INTEGER) LIMIT ?"; p.append(limit)
    out=[]
    for r in db().execute(sql,p):
        d=card_row(r); d["graded"]=r["graded"]; out.append(d)
    return jsonify(out)

@app.get("/api/cards/<cid>")
def card(cid):
    r=db().execute("""SELECT c.id,c.name,s.name set_name,c.set_id,c.number,c.rarity,c.types,c.release_date
                      FROM cards c JOIN sets s ON s.id=c.set_id WHERE c.id=?""",(cid,)).fetchone()
    return jsonify(card_row(r)) if r else (jsonify({"error":"not found"}),404)

@app.get("/api/offers/<cid>")
def offers(cid):
    rows=db().execute("SELECT * FROM graded_items WHERE card_id=? AND public=1 AND COALESCE(for_sale,0)=1 ORDER BY declared_value_cents",(cid,)).fetchall()
    return jsonify([graded_row(r) for r in rows])

@app.get("/api/all-copies/<cid>")
def all_copies(cid):
    rows=db().execute("SELECT * FROM graded_items WHERE card_id=? AND public=1 ORDER BY declared_value_cents DESC",(cid,)).fetchall()
    return jsonify([graded_row(r) for r in rows])

@app.get("/api/pop/<cid>")
def pop(cid):
    p={"10":0,"9":0,"8":0,"<=7":0}
    for r in db().execute("SELECT grade FROM graded_items WHERE card_id=? AND COALESCE(graded,1)=1",(cid,)):
        gv=r["grade"]; k="10" if gv==10 else ("9" if gv>=9 else ("8" if gv>=8 else "<=7"))
        p[k]+=1
    return jsonify(p)

@app.get("/api/collectors")
def collectors():
    rows=db().execute("""SELECT owner_handle owner, COUNT(*) n, COALESCE(SUM(declared_value_cents),0)/100.0 val
                         FROM graded_items WHERE public=1 GROUP BY owner_handle ORDER BY val DESC""").fetchall()
    return jsonify([{"owner":r["owner"],"city":OWNER_CITY.get(r["owner"],"Brasil"),"n":r["n"],"val":r["val"]} for r in rows])

@app.get("/api/collector/<handle>")
def collector(handle):
    rows=db().execute("""SELECT g.*, c.name cname, c.number cnum, c.types ctypes, c.rarity crar, s.name sname
                         FROM graded_items g JOIN cards c ON c.id=g.card_id JOIN sets s ON s.id=c.set_id
                         WHERE g.owner_handle=? AND g.public=1 ORDER BY g.declared_value_cents DESC""",(handle,)).fetchall()
    items=[]
    for r in rows:
        d=graded_row(r); d["card"]={"id":r["card_id"],"name":r["cname"],"num":r["cnum"],
                                    "type":ctype(r["ctypes"]),"rar":r["crar"] or "Common","set":r["sname"]}
        items.append(d)
    val=sum(i["value"] for i in items); gems=sum(1 for i in items if i["gem"])
    ranks=[r["owner"] for r in db().execute("""SELECT owner_handle owner FROM graded_items WHERE public=1
              GROUP BY owner_handle ORDER BY SUM(declared_value_cents) DESC""")]
    rank=(ranks.index(handle)+1) if handle in ranks else 0
    return jsonify({"handle":handle,"city":OWNER_CITY.get(handle,"Brasil"),"items":items,
                    "val":val,"gems":gems,"n":len(items),"rank":rank})

@app.get("/api/verify/<cert>")
def verify(cert):
    r=db().execute("""SELECT g.*, c.name cname, c.number cnum, c.types ctypes, c.rarity crar,
                             s.name sname, c.release_date crel
                      FROM graded_items g JOIN cards c ON c.id=g.card_id JOIN sets s ON s.id=c.set_id
                      WHERE UPPER(g.cert_id)=UPPER(?) AND COALESCE(g.graded,1)=1""",(cert,)).fetchone()
    if not r: return jsonify({"found":False})
    d=graded_row(r); d["found"]=True
    d["card"]={"id":r["card_id"],"name":r["cname"],"num":r["cnum"],"type":ctype(r["ctypes"]),
               "rar":r["crar"] or "Common","set":r["sname"],"y":(r["crel"] or "")[:4]}
    return jsonify(d)

# ---------------- contas ----------------
HANDLE_RE=re.compile(r"^[a-zA-Z0-9._-]{3,24}$")

@app.route("/api/signup", methods=["POST","OPTIONS"])
def signup():
    if request.method=="OPTIONS": return ("",204)
    b=request.get_json(force=True) or {}
    handle=(b.get("handle") or "").strip().lstrip("@")
    name=(b.get("name") or "").strip()
    email=(b.get("email") or "").strip().lower()
    city=(b.get("city") or "Brasil").strip()
    pw=b.get("password") or ""
    col=(b.get("collection") or "Vários").strip()
    if not HANDLE_RE.match(handle): return jsonify({"ok":False,"error":"@usuário inválido (3–24, letras/números/._-)"}),400
    if len(pw)<6: return jsonify({"ok":False,"error":"senha precisa de ao menos 6 caracteres"}),400
    if not email or "@" not in email: return jsonify({"ok":False,"error":"e-mail inválido"}),400
    c=db()
    if c.execute("SELECT 1 FROM users WHERE handle=?",(handle,)).fetchone():
        return jsonify({"ok":False,"error":"esse @usuário já existe"}),409
    if c.execute("SELECT 1 FROM users WHERE email=?",(email,)).fetchone():
        return jsonify({"ok":False,"error":"e-mail já cadastrado"}),409
    c.execute("INSERT INTO users(handle,name,email,city,collection,pw_hash) VALUES (?,?,?,?,?,?)",
              (handle,name or handle,email,city,col,generate_password_hash(pw)))
    c.commit()
    session["handle"]=handle
    return jsonify({"ok":True,"user":{"handle":handle,"name":name or handle,"city":city,"collection":col}})

@app.route("/api/login", methods=["POST","OPTIONS"])
def login():
    if request.method=="OPTIONS": return ("",204)
    b=request.get_json(force=True) or {}
    ident=(b.get("id") or "").strip().lstrip("@").lower()
    pw=b.get("password") or ""
    r=db().execute("SELECT * FROM users WHERE lower(handle)=? OR lower(email)=?",(ident,ident)).fetchone()
    if not r or not check_password_hash(r["pw_hash"], pw):
        return jsonify({"ok":False,"error":"usuário ou senha incorretos"}),401
    session["handle"]=r["handle"]
    return jsonify({"ok":True,"user":{"handle":r["handle"],"name":r["name"],"city":r["city"],"collection":r["collection"]}})

@app.route("/api/logout", methods=["POST","OPTIONS"])
def logout():
    if request.method=="OPTIONS": return ("",204)
    session.clear(); return jsonify({"ok":True})

@app.get("/api/me")
def me():
    h=current_user()
    if not h: return jsonify({"user":None})
    r=db().execute("SELECT handle,name,city,collection FROM users WHERE handle=?",(h,)).fetchone()
    if not r: session.clear(); return jsonify({"user":None})
    return jsonify({"user":{"handle":r["handle"],"name":r["name"],"city":r["city"],"collection":r["collection"]}})

@app.get("/api/me/cards")
def my_cards():
    h=auth_required()
    if not h: return jsonify({"error":"auth"}),401
    rows=db().execute("""SELECT g.*, c.name cname, c.number cnum, c.types ctypes, c.rarity crar, s.name sname
                         FROM graded_items g JOIN cards c ON c.id=g.card_id JOIN sets s ON s.id=c.set_id
                         WHERE g.owner_handle=? ORDER BY g.public DESC, g.declared_value_cents DESC""",(h,)).fetchall()
    items=[]
    for r in rows:
        d=graded_row(r); d["card"]={"id":r["card_id"],"name":r["cname"],"num":r["cnum"],
                                    "type":ctype(r["ctypes"]),"rar":r["crar"] or "Common","set":r["sname"]}
        items.append(d)
    return jsonify({"handle":h,"items":items,"n":len(items),"public_n":sum(1 for i in items if i["public"])})

@app.route("/api/graded/<cert>/visibility", methods=["POST","OPTIONS"])
def visibility(cert):
    if request.method=="OPTIONS": return ("",204)
    h=auth_required()
    if not h: return jsonify({"error":"auth"}),401
    row=db().execute("SELECT owner_handle FROM graded_items WHERE UPPER(cert_id)=UPPER(?)",(cert,)).fetchone()
    if not row: return jsonify({"ok":False,"error":"cert não encontrado"}),404
    if row["owner_handle"]!=h: return jsonify({"ok":False,"error":"esse card não é seu"}),403
    pub=1 if (request.get_json(force=True) or {}).get("public") else 0
    db().execute("UPDATE graded_items SET public=? WHERE UPPER(cert_id)=UPPER(?)",(pub,cert)); db().commit()
    return jsonify({"ok":True,"public":bool(pub)})

@app.route("/api/graded", methods=["POST","OPTIONS"])
def create_graded():
    if request.method=="OPTIONS": return ("",204)
    b=request.get_json(force=True) or {}
    gnum=float(b["grade"]); subs=b.get("subs",{})
    owner=(b.get("owner") or current_user() or "").strip().lstrip("@")
    if not owner: return jsonify({"ok":False,"error":"sem dono (faça login ou informe owner)"}),400
    pub=1 if b.get("public",True) else 0
    db().execute("""INSERT OR REPLACE INTO graded_items
        (cert_id,card_id,vertical,grade,gem,sub_centering,sub_corners,sub_edges,sub_surface,
         scan_url_front,owner_handle,declared_value_cents,graded_at,public)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),?)""",
        (b["cert"].upper(), b["cardId"], b.get("vertical","TCG"), gnum, 1 if gnum==10 else 0,
         subs.get("cen"),subs.get("cor"),subs.get("edg"),subs.get("sur"),
         b.get("scan"), owner, int(round(float(b["value"])*100)), pub))
    db().commit()
    return jsonify({"ok":True,"cert":b["cert"].upper(),"owner":owner,"public":bool(pub)})

@app.get("/api/price-history/<cid>")
def price_history(cid):
    rows=db().execute("SELECT d,price,currency FROM price_history WHERE card_id=? ORDER BY d",(cid,)).fetchall()
    if not rows: return jsonify({"found":False})
    cur=rows[-1]["currency"] or "EUR"
    rate=EUR_BRL if cur=="EUR" else USD_BRL
    pts=[{"d":r["d"],"v":round((r["price"] or 0)*rate,2)} for r in rows]
    last=datetime.date.fromisoformat(pts[-1]["d"])
    def win(n):
        cut=last - datetime.timedelta(days=n-1)
        s=[p["v"] for p in pts if datetime.date.fromisoformat(p["d"])>=cut]
        return round(sum(s)/len(s),2) if s else None
    vals=[p["v"] for p in pts]
    off=db().execute("SELECT declared_value_cents FROM graded_items WHERE card_id=? AND public=1 ORDER BY declared_value_cents",(cid,)).fetchall()
    return jsonify({"found":True,"currency":cur,"rate":rate,"points":pts,
                    "trend":vals[-1],"avg30":win(30),"avg7":win(7),"avg1":win(1),
                    "min":min(vals),"max":max(vals),
                    "offers_count":len(off),
                    "offers_from":(off[0]["declared_value_cents"]/100) if off else None})

@app.get("/api/price/<cid>")
def price(cid):
    r=db().execute("SELECT * FROM card_prices WHERE card_id=?",(cid,)).fetchone()
    if not r or r["market"] is None: return jsonify({"found":False})
    rate=EUR_BRL if (r["currency"]=="EUR") else USD_BRL
    def brl(v): return round(v*rate,2) if v is not None else None
    return jsonify({"found":True,"source":r["source"],"currency":r["currency"],
                    "market":r["market"],"low":r["low"],"high":r["high"],
                    "market_brl":brl(r["market"]),"low_brl":brl(r["low"]),"high_brl":brl(r["high"]),
                    "rate":rate,"url":r["url"],"updated_at":(r["updated_at"] or "")[:10]})

@app.route("/api/library", methods=["POST","OPTIONS"])
def add_library():
    if request.method=="OPTIONS": return ("",204)
    h=auth_required()
    if not h: return jsonify({"ok":False,"error":"faça login"}),401
    b=request.get_json(force=True) or {}
    cid=b.get("cardId")
    if not cid: return jsonify({"ok":False,"error":"escolha uma carta"}),400
    if not db().execute("SELECT 1 FROM cards WHERE id=?",(cid,)).fetchone():
        return jsonify({"ok":False,"error":"carta não encontrada no catálogo"}),404
    graded=1 if b.get("graded") else 0
    grade=float(b["grade"]) if (graded and b.get("grade")) else 0
    cert=(b.get("cert") or "").strip().upper() or gen_id("SLABR-" if graded else "LIB-")
    condition=(b.get("condition") or ("Graduada" if graded else "NM")).strip()
    qty=max(1,int(b.get("qty") or 1))
    value=int(round(float(b.get("value") or 0)*100))
    pub=1 if b.get("public",True) else 0
    sale=1 if b.get("forSale") else 0
    scan=b.get("scan") or None
    db().execute("""INSERT OR REPLACE INTO graded_items
        (cert_id,card_id,vertical,grade,gem,sub_centering,sub_corners,sub_edges,sub_surface,
         scan_url_front,owner_handle,declared_value_cents,graded_at,public,condition,qty,graded,for_sale)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),?,?,?,?,?)""",
        (cert, cid, "TCG", grade, 1 if grade==10 else 0, None,None,None,None,
         scan, h, value, pub, condition, qty, graded, sale))
    db().commit()
    return jsonify({"ok":True,"cert":cert,"graded":bool(graded),"condition":condition,"forSale":bool(sale)})

@app.route("/api/graded/<cert>/sale", methods=["POST","OPTIONS"])
def set_sale(cert):
    if request.method=="OPTIONS": return ("",204)
    h=auth_required()
    if not h: return jsonify({"ok":False,"error":"auth"}),401
    row=db().execute("SELECT owner_handle FROM graded_items WHERE UPPER(cert_id)=UPPER(?)",(cert,)).fetchone()
    if not row: return jsonify({"ok":False,"error":"item não encontrado"}),404
    if row["owner_handle"]!=h: return jsonify({"ok":False,"error":"esse item não é seu"}),403
    sale=1 if (request.get_json(force=True) or {}).get("forSale") else 0
    db().execute("UPDATE graded_items SET for_sale=? WHERE UPPER(cert_id)=UPPER(?)",(sale,cert)); db().commit()
    return jsonify({"ok":True,"forSale":bool(sale)})

@app.route("/api/grading-request", methods=["POST","OPTIONS"])
def grading_request():
    if request.method=="OPTIONS": return ("",204)
    h=auth_required()
    if not h: return jsonify({"ok":False,"error":"faça login"}),401
    b=request.get_json(force=True) or {}
    cert=(b.get("cert") or "").strip()
    item=db().execute("SELECT owner_handle,card_id,graded FROM graded_items WHERE UPPER(cert_id)=UPPER(?)",(cert,)).fetchone()
    if not item: return jsonify({"ok":False,"error":"carta não encontrada na sua biblioteca"}),404
    if item["owner_handle"]!=h: return jsonify({"ok":False,"error":"essa carta não é sua"}),403
    if item["graded"]: return jsonify({"ok":False,"error":"essa carta já está graduada"}),400
    checklist=b.get("checklist") or {}
    required=["owner","authentic","unaltered","clean","terms","packaging"]
    if not all(checklist.get(k) for k in required):
        return jsonify({"ok":False,"error":"marque todos os itens obrigatórios do checklist"}),400
    dv=int(round(float(b.get("declared_value") or 0)*100))
    if dv<=0: return jsonify({"ok":False,"error":"informe o valor declarado (para seguro)"}),400
    proto="GR-"+gen_id("")[1:]  # protocolo legível
    db().execute("""INSERT INTO grading_requests
        (protocol,owner_handle,item_cert,card_id,status,checklist,declared_value_cents,service,notes,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (proto,h,cert,item["card_id"],"Encaminhado à TAG Grading",
         json.dumps(checklist),dv,b.get("service") or "Padrão",(b.get("notes") or "").strip()))
    db().commit()
    return jsonify({"ok":True,"protocol":proto,"status":"Encaminhado à TAG Grading"})

@app.get("/api/me/grading-requests")
def my_grading_requests():
    h=auth_required()
    if not h: return jsonify({"error":"auth"}),401
    rows=db().execute("""SELECT g.*, c.name cname, c.number cnum, s.name sname
                         FROM grading_requests g JOIN cards c ON c.id=g.card_id JOIN sets s ON s.id=c.set_id
                         WHERE g.owner_handle=? ORDER BY g.created_at DESC""",(h,)).fetchall()
    return jsonify([{"protocol":r["protocol"],"cert":r["item_cert"],"status":r["status"],
                     "value":(r["declared_value_cents"] or 0)/100,"service":r["service"],
                     "date":(r["created_at"] or "")[:10],
                     "card":{"id":r["card_id"],"name":r["cname"],"num":r["cnum"],"set":r["sname"]}} for r in rows])

@app.get("/api/market")
def market():
    limit=min(int(request.args.get("limit",24)),60)
    rows=db().execute("""SELECT g.cert_id,g.grade,g.gem,g.declared_value_cents,g.owner_handle,
                                g.graded,g.condition,g.scan_url_front,
                                c.id cid,c.name cname,c.number cnum,c.types ctypes,c.rarity crar,s.name sname
                         FROM graded_items g JOIN cards c ON c.id=g.card_id JOIN sets s ON s.id=c.set_id
                         WHERE g.public=1 AND COALESCE(g.for_sale,0)=1 ORDER BY g.declared_value_cents DESC LIMIT ?""",(limit,)).fetchall()
    return jsonify([{"cert":r["cert_id"],"grade":r["grade"],"gem":bool(r["gem"]),
                     "graded":bool(r["graded"]) if r["graded"] is not None else True,"condition":r["condition"],
                     "scan":r["scan_url_front"],
                     "value":(r["declared_value_cents"] or 0)/100,"owner":r["owner_handle"],
                     "card":{"id":r["cid"],"name":r["cname"],"num":r["cnum"],"type":ctype(r["ctypes"]),
                             "rar":r["crar"] or "Common","set":r["sname"]}} for r in rows])

# ============================================
# FASE 0: ENDPOINTS BYNX.GG
# ============================================

def _get_cache_key(card_id):
    return f"bynx_price:{card_id}"

def _is_cache_valid(cached_at):
    return (datetime.datetime.now() - cached_at).total_seconds() < _cache_ttl

def _get_cached_price(card_id):
    key = _get_cache_key(card_id)
    if key in _price_cache:
        cached = _price_cache[key]
        if _is_cache_valid(cached['timestamp']):
            return cached['data']
    return None

def _set_cache(card_id, data):
    key = _get_cache_key(card_id)
    _price_cache[key] = {'data': data, 'timestamp': datetime.datetime.now()}

@app.get("/api/prices/bynx/<card_id>")
def get_bynx_price(card_id):
    """Retorna preço de uma carta em Bynx.gg"""
    try:
        cached_price = _get_cached_price(card_id)
        if cached_price:
            cached_price['cached'] = True
            return jsonify(cached_price)

        db_card = db().execute("SELECT id, name FROM cards WHERE id = ?", (card_id,)).fetchone()
        if not db_card:
            return jsonify({"found": False, "error": "Carta não encontrada"}), 404

        bynx_price = _bynx_scraper.search_card(db_card["name"], card_id)
        if not bynx_price:
            return jsonify({"found": False, "card_id": card_id, "error": "Preço não disponível"}), 404

        response_data = {
            "found": True,
            "card_id": card_id,
            "name": bynx_price.get('name'),
            "price_brl": bynx_price.get('price_brl'),
            "source": "bynx.gg",
            "timestamp": bynx_price.get('timestamp'),
            "cached": False
        }
        _set_cache(card_id, response_data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"found": False, "error": str(e)}), 500

@app.get("/api/prices/bynx/compare/<card_id>")
def compare_prices(card_id):
    """Compara preço SLABR vs Bynx.gg"""
    try:
        slabr_offer = db().execute(
            "SELECT declared_value_cents FROM graded_items WHERE card_id = ? AND public = 1 ORDER BY declared_value_cents LIMIT 1",
            (card_id,)
        ).fetchone()
        slabr_price = (slabr_offer['declared_value_cents'] / 100) if slabr_offer else None

        bynx_data = get_bynx_price(card_id)
        bynx_json = bynx_data[0].get_json() if isinstance(bynx_data, tuple) else bynx_data.get_json()
        bynx_price = bynx_json.get('price_brl') if bynx_json.get('found') else None

        card = db().execute("SELECT name FROM cards WHERE id = ?", (card_id,)).fetchone()
        if not card:
            return jsonify({"error": "Carta não encontrada"}), 404

        result = {
            "card_id": card_id,
            "name": card["name"],
            "slabr_price": slabr_price,
            "bynx_price": bynx_price,
            "difference": None,
            "difference_pct": None,
            "more_expensive_in": None
        }

        if slabr_price and bynx_price:
            diff = slabr_price - bynx_price
            diff_pct = (diff / bynx_price) * 100
            result["difference"] = diff
            result["difference_pct"] = round(diff_pct, 2)
            result["more_expensive_in"] = "slabr" if diff > 0 else "bynx"

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/prices/bynx/health")
def bynx_health_check():
    """Health check do scraper Bynx"""
    try:
        test_result = _bynx_scraper.search_card("Charizard", "base1-4")
        if test_result:
            return jsonify({"status": "healthy", "scraper": "online", "test": "OK"})
        return jsonify({"status": "degraded", "scraper": "online_but_no_data"}), 503
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

# roda a migração no import também (deploys com gunicorn não executam o bloco __main__)
migrate_and_seed()

if __name__ == "__main__":
    # PORT é definido pela maioria dos serviços de hospedagem; SLABR_PORT é o override local
    port = int(os.environ.get("PORT", os.environ.get("SLABR_PORT", "5000")))
    deployed = bool(os.environ.get("PORT"))
    host = os.environ.get("SLABR_HOST", "0.0.0.0" if deployed else "127.0.0.1")
    dbg = host == "127.0.0.1"
    print(f"SLABR.br rodando em http://{host}:{port}")
    if host == "0.0.0.0" and not deployed:
        try:
            import socket
            ip = socket.gethostbyname(socket.gethostname())
            print(f"  no celular (mesma rede Wi-Fi): http://{ip}:{port}")
        except Exception:
            print("  no celular: use http://SEU-IP-LOCAL:" + str(port))
        print("  (debugger desligado por estar exposto na rede)")
    app.run(debug=dbg, host=host, port=port)
