#!/usr/bin/env python3
"""
API SLABR.br - app + endpoints + CONTAS (cadastro/login) lendo/gravando no pokemon_catalog.db.
Rodar:
    pip install flask --break-system-packages
    python3 ingest_catalog.py     # (uma vez) constroi o catalogo, se ainda nao fez
    python3 api.py                # http://localhost:5000

Contas demo (senha: demo123): raf10, marina.sp, joao_v, ana.bea, lucas_rs, tcg_bsb
"""
import sqlite3, json, os, re, datetime, threading
from flask import Flask, jsonify, request, g, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

DB   = os.environ.get("SLABR_DB", "pokemon_catalog.db")
HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slabr_app.html")
app  = Flask(__name__)
app.secret_key = os.environ.get("SLABR_SECRET", "troque-este-segredo-em-producao")

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
    r=db().execute("""SELECT c.id,c.name,s.name set_name,c.set_id,c.number,c.rarity,c.types,c.release_date,
                             c.official_image_small,c.official_image_large
                      FROM cards c JOIN sets s ON s.id=c.set_id WHERE c.id=?""",(cid,)).fetchone()
    if not r:
        return (jsonify({"error":"not found"}),404)
    d=card_row(r)
    d["official_image_small"]=r["official_image_small"]
    d["official_image_large"]=r["official_image_large"]
    return jsonify({"ok":True,"card":d})

@app.get("/api/offers/<cid>")
def offers(cid):
    rows=db().execute("SELECT * FROM graded_items WHERE card_id=? AND public=1 AND COALESCE(for_sale,0)=1 ORDER BY declared_value_cents",(cid,)).fetchall()
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

# ========== PERFIS PUBLICOS ==========
@app.get("/api/perfil/<handle>")
def perfil_publico(handle):
    """Retorna dados publicos do perfil de um colecionador"""
    user = db().execute("SELECT handle, name, email, city, created_at FROM users WHERE LOWER(handle)=LOWER(?)", (handle,)).fetchone()
    if not user:
        return jsonify({"ok":False, "error":"Colecionador nao encontrado"}), 404

    # Stats do portfolio
    stats = db().execute(
        "SELECT total_cards, total_value FROM portfolio_stats WHERE LOWER(user_id)=LOWER(?)",
        (handle,)
    ).fetchone()

    # Cartas graduadas publicas
    graded = db().execute(
        "SELECT COUNT(*) as count FROM graded_items WHERE LOWER(owner_handle)=LOWER(?) AND public=1",
        (handle,)
    ).fetchone()

    return jsonify({
        "ok": True,
        "handle": user["handle"],
        "name": user["name"] or user["handle"],
        "city": user["city"] or "Brasil",
        "joined": (user["created_at"] or "")[:10],
        "stats": {
            "total_cards": stats["total_cards"] if stats else 0,
            "total_value": float(stats["total_value"] or 0) if stats else 0,
            "graded_public": graded["count"] if graded else 0
        },
        "whatsapp": None  # Campo para futuro
    })

@app.get("/api/perfil/<handle>/cartas")
def perfil_cartas(handle):
    """Retorna cartas do colecionador (publicas)"""
    # Verificar que o usuario existe
    user = db().execute("SELECT handle FROM users WHERE LOWER(handle)=LOWER(?)", (handle,)).fetchone()
    if not user:
        return jsonify({"ok":False, "error":"Colecionador nao encontrado"}), 404

    # Cartas da colecao
    cartas = db().execute("""
        SELECT id, card_id, card_name, quantity, condition, purchase_price, created_at
        FROM user_collections
        WHERE LOWER(user_id)=LOWER(?)
        ORDER BY created_at DESC
        LIMIT 50
    """, (handle,)).fetchall()

    # Cartas graduadas publicas
    graded = db().execute("""
        SELECT cert_id, card_id, grade, gem, declared_value_cents, condition, public
        FROM graded_items
        WHERE LOWER(owner_handle)=LOWER(?) AND public=1
        ORDER BY graded_at DESC
        LIMIT 50
    """, (handle,)).fetchall()

    return jsonify({
        "ok": True,
        "handle": handle,
        "colecao": [
            {
                "id": c["id"],
                "card_id": c["card_id"],
                "card_name": c["card_name"],
                "quantity": c["quantity"],
                "condition": c["condition"],
                "price": float(c["purchase_price"] or 0),
                "added": (c["created_at"] or "")[:10]
            } for c in cartas
        ],
        "graded_public": [
            {
                "cert_id": g["cert_id"],
                "card_id": g["card_id"],
                "grade": g["grade"],
                "gem": bool(g["gem"]),
                "value": (g["declared_value_cents"] or 0) / 100,
                "condition": g["condition"],
                "public": bool(g["public"])
            } for g in graded
        ]
    })

@app.get("/api/perfil/<handle>/galeria")
def perfil_galeria(handle):
    """Retorna cartas com imagens para galeria visual"""
    graded = db().execute("""
        SELECT g.cert_id, g.card_id, g.grade, g.gem, g.declared_value_cents, g.condition,
               c.name card_name, c.official_image_large, c.official_image_small
        FROM graded_items g
        JOIN cards c ON c.id = g.card_id
        WHERE LOWER(g.owner_handle)=LOWER(?) AND g.public=1
        ORDER BY g.declared_value_cents DESC
        LIMIT 100
    """, (handle,)).fetchall()

    return jsonify({
        "ok": True,
        "handle": handle,
        "cartas": [
            {
                "cert": g["cert_id"],
                "cardId": g["card_id"],
                "cardName": g["card_name"],
                "grade": g["grade"],
                "gem": bool(g["gem"]),
                "value": (g["declared_value_cents"] or 0) / 100,
                "condition": g["condition"],
                "image": g["official_image_large"],
                "imageMini": g["official_image_small"]
            } for g in graded
        ]
    })

@app.get("/api/colecionadores")
def listar_colecionadores():
    """Lista todos os colecionadores (TOP por patrimonio)"""
    rows = db().execute("""
        SELECT
            u.handle,
            u.name,
            u.city,
            COUNT(DISTINCT gi.cert_id) as total_cards,
            SUM(gi.declared_value_cents) / 100.0 as total_value
        FROM users u
        LEFT JOIN graded_items gi ON LOWER(gi.owner_handle) = LOWER(u.handle) AND gi.public = 1
        GROUP BY u.handle, u.name, u.city
        ORDER BY total_value DESC NULLS LAST
        LIMIT 50
    """).fetchall()

    return jsonify({
        "ok": True,
        "colecionadores": [
            {
                "handle": r["handle"],
                "name": r["name"] or r["handle"],
                "city": r["city"] or "Brasil",
                "total_cards": r["total_cards"] or 0,
                "total_value": float(r["total_value"] or 0)
            } for r in rows
        ]
    })

@app.get("/api/buscar-colecionadores")
def buscar_colecionadores():
    """Buscar colecionadores por nome, handle ou cidade"""
    query = request.args.get("q", "").strip()
    city_filter = request.args.get("city", "").strip()
    min_value = float(request.args.get("min_value", 0))

    if not query and not city_filter:
        return jsonify({"ok": False, "error": "Informe um termo de busca"}), 400

    sql = """
        SELECT
            u.handle,
            u.name,
            u.city,
            COUNT(DISTINCT gi.cert_id) as total_cards,
            SUM(gi.declared_value_cents) / 100.0 as total_value
        FROM users u
        LEFT JOIN graded_items gi ON LOWER(gi.owner_handle) = LOWER(u.handle) AND gi.public = 1
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (LOWER(u.handle) LIKE ? OR LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ?)"
        search_term = f"%{query.lower()}%"
        params.extend([search_term, search_term, search_term])

    if city_filter:
        sql += " AND LOWER(u.city) LIKE ?"
        params.append(f"%{city_filter.lower()}%")

    if min_value > 0:
        sql += " AND (SUM(gi.declared_value_cents) / 100.0) >= ?"
        params.append(min_value)

    sql += " GROUP BY u.handle, u.name, u.city ORDER BY total_value DESC NULLS LAST LIMIT 100"

    rows = db().execute(sql, params).fetchall()

    return jsonify({
        "ok": True,
        "query": query,
        "results": len(rows),
        "colecionadores": [
            {
                "handle": r["handle"],
                "name": r["name"] or r["handle"],
                "city": r["city"] or "Brasil",
                "total_cards": r["total_cards"] or 0,
                "total_value": float(r["total_value"] or 0)
            } for r in rows
        ]
    })

@app.get("/home-public")
def home_publico():
    """Pagina publica com marketplace e ranking"""
    with open("slabr-home.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/dashboard/<handle>/patrimonio")
def dashboard_patrimonio(handle):
    """Evolucao do patrimonio ao longo do tempo"""
    # Calcular patrimonio a partir de graded_items
    graded = db().execute(
        "SELECT COUNT(*) as count, SUM(declared_value_cents) as total FROM graded_items WHERE LOWER(owner_handle)=LOWER(?)",
        (handle,)
    ).fetchone()

    if not graded or graded["count"] == 0:
        return jsonify({"ok": False, "error": "Colecionador nao encontrado"}), 404

    total_value = float(graded["total"] or 0) / 100  # Converter cents para reais
    # Simular crescimento de 30 dias (5% ao dia em media)
    days = []
    values = []
    for day in range(30, -1, -1):
        growth = 1 + (0.03 * (30 - day))  # Crescimento progressivo
        value = total_value * growth * (0.95 + (day % 5) * 0.02)  # Com variacao
        days.append(f"-{day}d")
        values.append(round(value, 2))

    return jsonify({
        "ok": True,
        "handle": handle,
        "current_value": total_value,
        "evolution": {
            "labels": days,
            "values": values,
            "change_percent": round(((values[-1] - values[0]) / values[0] * 100), 2) if values[0] > 0 else 0
        }
    })

@app.get("/api/dashboard/<handle>/roi")
def dashboard_roi(handle):
    """ROI (ganho/perda) por carta"""
    cartas = db().execute("""
        SELECT uc.card_id, uc.card_name, uc.quantity, uc.purchase_price,
               (SELECT market * 5.4 FROM card_prices WHERE card_id=uc.card_id LIMIT 1) as current_price,
               c.official_image_large, c.official_image_small
        FROM user_collections uc
        LEFT JOIN cards c ON c.id = uc.card_id
        WHERE LOWER(uc.user_id)=LOWER(?)
        ORDER BY ((current_price - purchase_price) * quantity) DESC
        LIMIT 20
    """, (handle,)).fetchall()

    if not cartas:
        return jsonify({"ok": True, "cartas": [], "total_gain": 0, "total_loss": 0})

    total_gain = 0
    total_loss = 0
    roi_list = []

    for c in cartas:
        cost = float(c["purchase_price"] or 0) * c["quantity"]
        current = float(c["current_price"] or 0) * c["quantity"]
        gain = current - cost
        roi_percent = ((gain / cost) * 100) if cost > 0 else 0

        if gain > 0:
            total_gain += gain
        else:
            total_loss += abs(gain)

        roi_list.append({
            "card_id": c["card_id"],
            "card_name": c["card_name"],
            "quantity": c["quantity"],
            "purchase_price": float(c["purchase_price"] or 0),
            "current_price": float(c["current_price"] or 0),
            "cost": round(cost, 2),
            "current_value": round(current, 2),
            "gain": round(gain, 2),
            "roi_percent": round(roi_percent, 2),
            "image": c["official_image_large"],
            "imageMini": c["official_image_small"]
        })

    return jsonify({
        "ok": True,
        "handle": handle,
        "total_gain": round(total_gain, 2),
        "total_loss": round(total_loss, 2),
        "net_roi": round(total_gain - total_loss, 2),
        "roi_percent": round(((total_gain - total_loss) / (total_gain + total_loss) * 100), 2) if (total_gain + total_loss) > 0 else 0,
        "cartas": roi_list
    })

@app.get("/api/dashboard/<handle>/performance")
def dashboard_performance(handle):
    """Performance mensal"""
    # Simular dados mensais
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    values = [
        10000, 10500, 11200, 11800, 13200, 14500  # Crescimento progressivo
    ]

    return jsonify({
        "ok": True,
        "handle": handle,
        "monthly": {
            "labels": months,
            "values": values,
            "average": round(sum(values) / len(values), 2),
            "highest_month": max(months, key=lambda x: values[months.index(x)]),
            "highest_value": max(values)
        }
    })

# ========== MARKETPLACE P2P ==========
@app.route("/api/marketplace/criar-listagem", methods=["POST","OPTIONS"])
def criar_listagem():
    """Criar nova listagem (usuario marca carta a venda)"""
    if request.method == "OPTIONS":
        return ("", 204)

    h = auth_required()
    if not h:
        return jsonify({"ok": False, "error": "Faca login"}), 401

    data = request.get_json(force=True) or {}
    card_id = (data.get("card_id") or "").strip()
    card_name = (data.get("card_name") or "").strip()
    price = float(data.get("price") or 0)
    condition = (data.get("condition") or "NM").strip()
    description = (data.get("description") or "").strip()

    if not card_id or not card_name or price <= 0:
        return jsonify({"ok": False, "error": "Informe card_id, card_name e preco"}), 400

    listing_id = gen_id("LST")
    db().execute("""
        INSERT INTO marketplace_listings
        (id, seller_id, card_id, card_name, price, condition, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    """, (listing_id, h, card_id, card_name, price, condition, description))
    db().commit()

    return jsonify({
        "ok": True,
        "listing_id": listing_id,
        "message": "Carta listada com sucesso!"
    }), 201

@app.get("/api/marketplace/listagens")
def listar_marketplace():
    """Listar todas as cartas a venda (marketplace publico)"""
    query = request.args.get("q", "").strip()
    condition = request.args.get("condition", "").strip()
    min_price = float(request.args.get("min_price", 0))
    max_price = float(request.args.get("max_price", 999999))
    seller = request.args.get("seller", "").strip()

    sql = """
        SELECT id, seller_id, card_id, card_name, price, condition, description, created_at
        FROM marketplace_listings
        WHERE status = 'active'
    """
    params = []

    if query:
        sql += " AND (LOWER(card_name) LIKE ? OR LOWER(card_id) LIKE ?)"
        search = f"%{query.lower()}%"
        params.extend([search, search])

    if condition:
        sql += " AND condition = ?"
        params.append(condition)

    if seller:
        sql += " AND LOWER(seller_id) = LOWER(?)"
        params.append(seller)

    sql += " AND price BETWEEN ? AND ?"
    params.extend([min_price, max_price])

    sql += " ORDER BY created_at DESC LIMIT 100"

    rows = db().execute(sql, params).fetchall()

    return jsonify({
        "ok": True,
        "total": len(rows),
        "listagens": [
            {
                "id": r["id"],
                "seller_id": r["seller_id"],
                "card_id": r["card_id"],
                "card_name": r["card_name"],
                "price": r["price"],
                "condition": r["condition"],
                "description": r["description"],
                "created_at": r["created_at"]
            } for r in rows
        ]
    })

@app.route("/api/marketplace/remover-listagem", methods=["POST","OPTIONS"])
def remover_listagem():
    """Remover listagem (vendedor remove sua carta)"""
    if request.method == "OPTIONS":
        return ("", 204)

    h = auth_required()
    if not h:
        return jsonify({"ok": False, "error": "Faca login"}), 401

    listing_id = (request.get_json(force=True) or {}).get("listing_id")

    # Verificar ownership
    row = db().execute("SELECT seller_id FROM marketplace_listings WHERE id=?", (listing_id,)).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Listagem nao encontrada"}), 404

    if row["seller_id"] != h:
        return jsonify({"ok": False, "error": "Essa listagem nao e sua"}), 403

    db().execute("UPDATE marketplace_listings SET status='removed' WHERE id=?", (listing_id,))
    db().commit()

    return jsonify({"ok": True, "message": "Listagem removida"})

@app.route("/api/marketplace/fazer-oferta", methods=["POST","OPTIONS"])
def fazer_oferta():
    """Buyer faz oferta para carta"""
    if request.method == "OPTIONS":
        return ("", 204)

    h = auth_required()
    if not h:
        return jsonify({"ok": False, "error": "Faca login"}), 401

    data = request.get_json(force=True) or {}
    listing_id = data.get("listing_id")
    offered_price = float(data.get("offered_price") or 0)
    message = (data.get("message") or "").strip()

    if not listing_id or offered_price <= 0:
        return jsonify({"ok": False, "error": "Informe listing_id e offered_price"}), 400

    listing = db().execute("SELECT seller_id, card_name, price FROM marketplace_listings WHERE id=?", (listing_id,)).fetchone()
    if not listing:
        return jsonify({"ok": False, "error": "Listagem nao encontrada"}), 404

    if listing["seller_id"] == h:
        return jsonify({"ok": False, "error": "Nao pode fazer oferta na sua propria carta"}), 400

    offer_id = gen_id("OFR")
    db().execute("""
        INSERT INTO marketplace_trades
        (id, listing_id, buyer_id, seller_id, offered_price, message, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (offer_id, listing_id, h, listing["seller_id"], offered_price, message))
    db().commit()

    return jsonify({
        "ok": True,
        "offer_id": offer_id,
        "whatsapp_link": f"https://wa.me/?text=Oi%20{listing['seller_id']}%20fiz%20uma%20oferta%20por%20{listing['card_name']}%20no%20SLABR"
    }), 201

@app.get("/marketplace")
def pagina_marketplace():
    """Página pública de marketplace P2P"""
    with open("marketplace.html", encoding="utf-8") as f:
        return f.read()

# ========== GAMIFICACAO ==========
@app.get("/api/ranking-mensal")
def ranking_mensal():
    """Top 3 ranking mensal com prêmios (R$ 200/100/50)"""
    from datetime import datetime, timedelta

    # Pega data atual (mês)
    hoje = datetime.now()
    inicio_mes = datetime(hoje.year, hoje.month, 1)

    # Calcula ranking por: cartas adicionadas + patrimônio
    sql = """
        SELECT
            owner_handle,
            COUNT(*) as cartas_adicionadas,
            SUM(declared_value_cents) / 100 as patrimonio_total
        FROM graded_items
        WHERE graded_at >= ? AND public = 1
        GROUP BY owner_handle
        ORDER BY cartas_adicionadas DESC, patrimonio_total DESC
        LIMIT 3
    """

    rows = db().execute(sql, (inicio_mes.isoformat(),)).fetchall()
    premios = [200, 100, 50]

    ranking = []
    for i, r in enumerate(rows):
        ranking.append({
            "posicao": i + 1,
            "usuario": r["owner_handle"],
            "cartas": r["cartas_adicionadas"],
            "patrimonio": round(r["patrimonio_total"] or 0, 2),
            "premio": premios[i] if i < len(premios) else 0,
            "badge": ["🥇 Ouro", "🥈 Prata", "🥉 Bronze"][i] if i < 3 else ""
        })

    return jsonify({"ok": True, "mes": f"{hoje.year}-{hoje.month:02d}", "ranking": ranking})

@app.get("/api/badges/<handle>")
def get_badges(handle):
    """Badges e achievements do usuário"""

    # Calcular badges baseado em dados
    badges = []

    # Badge: Iniciante (primeira carta)
    first = db().execute("SELECT COUNT(*) as c FROM graded_items WHERE owner_handle=?", (handle,)).fetchone()
    if first["c"] >= 1:
        badges.append({"id": "iniciante", "nome": "Colecionador Iniciante", "icon": "🎯", "earned": True})

    # Badge: Pro (50+ cartas ou assinatura)
    if first["c"] >= 50:
        badges.append({"id": "pro", "nome": "PRO", "icon": "⭐", "earned": True})

    # Badge: Investidor (patrimônio > R$ 10k)
    total_value = db().execute("SELECT SUM(declared_value_cents)/100 as v FROM graded_items WHERE owner_handle=?", (handle,)).fetchone()
    if (total_value["v"] or 0) > 10000:
        badges.append({"id": "investidor", "nome": "Investidor", "icon": "💎", "earned": True})

    # Badge: Graduador (10+ cartas graduadas)
    graded = db().execute("SELECT COUNT(*) as c FROM graded_items WHERE owner_handle=? AND graded=1", (handle,)).fetchone()
    if graded["c"] >= 10:
        badges.append({"id": "graduador", "nome": "Graduador", "icon": "📊", "earned": True})

    # Badge: Marketplace Ativo (3+ listings)
    listings = db().execute("SELECT COUNT(*) as c FROM marketplace_listings WHERE seller_id=? AND status='active'", (handle,)).fetchone()
    if listings["c"] >= 3:
        badges.append({"id": "marketplace", "nome": "Marketplace Ativo", "icon": "🛒", "earned": True})

    return jsonify({"ok": True, "usuario": handle, "badges": badges})

@app.get("/api/lojas")
def listar_lojas():
    """Guia de lojas brasileiras (física/online)"""

    lojas = [
        {
            "id": "loja1",
            "nome": "TCG Brasil",
            "tipo": "Online",
            "cidade": "São Paulo, SP",
            "whatsapp": "11999999999",
            "instagram": "@tcgbrasil",
            "rating": 4.8,
            "descricao": "Maior marketplace de TCG do Brasil"
        },
        {
            "id": "loja2",
            "nome": "Card Shop SP",
            "tipo": "Física",
            "cidade": "São Paulo, SP",
            "endereco": "Rua 25 de Março, 123",
            "telefone": "1133334444",
            "rating": 4.6,
            "descricao": "Loja física especializada em Pokémon"
        },
        {
            "id": "loja3",
            "nome": "Carta Rara",
            "tipo": "Online",
            "cidade": "Belo Horizonte, MG",
            "whatsapp": "31988888888",
            "instagram": "@cartarara_mg",
            "rating": 4.7,
            "descricao": "Cards raros e colecionáveis"
        },
        {
            "id": "loja4",
            "nome": "Pokémon House",
            "tipo": "Física",
            "cidade": "Rio de Janeiro, RJ",
            "endereco": "Avenida Rio Branco, 456",
            "telefone": "2133335555",
            "rating": 4.5,
            "descricao": "Pioneira em venda de cards raros"
        },
        {
            "id": "loja5",
            "nome": "TCG Curitiba",
            "tipo": "Física",
            "cidade": "Curitiba, PR",
            "endereco": "Rua XV de Novembro, 789",
            "telefone": "4133336666",
            "rating": 4.9,
            "descricao": "Melhor avaliação em atendimento"
        },
        {
            "id": "loja6",
            "nome": "Card Market Brasil",
            "tipo": "Online",
            "cidade": "Porto Alegre, RS",
            "whatsapp": "51987777777",
            "instagram": "@cardmarket_br",
            "rating": 4.6,
            "descricao": "Entrega rápida para sul do Brasil"
        }
    ]

    # Filtros
    cidade = request.args.get("cidade", "").strip()
    tipo = request.args.get("tipo", "").strip()

    if cidade:
        lojas = [l for l in lojas if cidade.lower() in l["cidade"].lower()]

    if tipo:
        lojas = [l for l in lojas if l["tipo"].upper() == tipo.upper()]

    return jsonify({"ok": True, "total": len(lojas), "lojas": lojas})

@app.get("/ranking-mensal")
def pagina_ranking_mensal():
    """Página visual de ranking mensal com prêmios"""
    with open("ranking-mensal.html", encoding="utf-8") as f:
        return f.read()

@app.get("/lojas")
def pagina_lojas():
    """Página de guia de lojas brasileiras"""
    with open("lojas.html", encoding="utf-8") as f:
        return f.read()

@app.get("/buscar")
def pagina_buscar():
    """Pagina de busca de colecionadores"""
    html = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Buscar Colecionadores - SLABR</title>
<style>
:root{--vault:#0c0f13;--vault-2:#13171e;--ice:#eef2f7;--mist:#97a1b0;--champagne:#e7c47a;--line:rgba(255,255,255,.07)}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;color:var(--ice);background:linear-gradient(135deg,var(--vault) 0%,#0f1535 100%);min-height:100vh}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
header{position:sticky;top:0;z-index:40;backdrop-filter:blur(16px);background:linear-gradient(to bottom,rgba(12,15,19,.94),rgba(12,15,19,.66));border-bottom:1px solid var(--line)}
.bar{display:flex;align-items:center;gap:26px;height:66px}
.brand{font-family:'Bricolage Grotesque';font-weight:800;font-size:19px;cursor:pointer}
nav a{color:var(--mist);font-size:14px;font-weight:500;padding:4px 0;border-bottom:2px solid transparent;cursor:pointer;margin-left:20px}
nav a:hover{color:var(--ice);border-bottom-color:var(--champagne)}
.hero{padding:60px 0;text-align:center;background:linear-gradient(135deg,rgba(231,196,122,.05) 0%,rgba(231,196,122,.02) 100%);border-bottom:1px solid var(--line)}
.hero h1{font-size:48px;margin-bottom:10px;font-weight:800;color:var(--champagne)}
.search-box{background:var(--vault-2);border:1px solid var(--line);border-radius:12px;padding:30px;margin:40px 0;max-width:600px;margin-left:auto;margin-right:auto}
.search-box input{width:100%;padding:12px 16px;background:var(--vault);border:1px solid var(--line);border-radius:8px;color:var(--ice);font-size:14px;margin-bottom:15px}
.search-box input:focus{outline:none;border-color:var(--champagne)}
.search-box button{width:100%;padding:12px;background:var(--champagne);color:var(--vault);border:none;border-radius:8px;font-weight:600;cursor:pointer}
.results{margin-top:40px}
.collector-card{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;padding:20px;margin-bottom:15px;cursor:pointer;transition:all 0.3s}
.collector-card:hover{border-color:var(--champagne);transform:translateY(-3px)}
.collector-name{font-size:18px;font-weight:600;color:var(--ice);margin-bottom:5px}
.collector-city{font-size:14px;color:var(--mist);margin-bottom:10px}
.collector-stats{display:flex;gap:20px;font-size:13px;color:var(--mist)}
.stat{background:var(--vault);padding:6px 12px;border-radius:6px}
.loading{text-align:center;padding:40px;color:var(--mist)}
.empty{text-align:center;padding:40px;color:var(--mist)}
footer{border-top:1px solid var(--line);padding:30px 0;text-align:center;color:var(--mist);font-size:12px;margin-top:60px}
</style>
</head><body>
<header><div class="bar"><div class="brand" onclick="location.href='/home-public'">SLABR</div><nav><a onclick="location.href='/home-public'">Home</a><a onclick="location.href='/colecionadores'">Ranking</a></nav></div></header>

<div class="hero"><div class="wrap"><h1>🔍 Buscar Colecionadores</h1><p>Encontre colecionadores por nome, usuário ou localização</p></div></div>

<div class="wrap">
    <div class="search-box">
        <input type="text" id="search-input" placeholder="Buscar por nome, usuário ou cidade..." onkeyup="if(event.key==='Enter') buscar()">
        <button onclick="buscar()">Buscar</button>
    </div>

    <div id="results" class="results"></div>
</div>

<footer><p>SLABR - Marketplace de Trading Cards | Busca de Colecionadores</p></footer>

<script>
const API_BASE = 'http://localhost:5000';

async function buscar() {
    const query = document.getElementById('search-input').value.trim();
    const results = document.getElementById('results');

    if (!query) {
        results.innerHTML = '<div class="empty">Digite um termo para buscar</div>';
        return;
    }

    results.innerHTML = '<div class="loading"><div style="margin-bottom:10px">⏳</div>Buscando...</div>';

    try {
        const res = await fetch(`${API_BASE}/api/buscar-colecionadores?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (!data.ok || data.results === 0) {
            results.innerHTML = '<div class="empty">Nenhum colecionador encontrado para "<strong>' + query + '</strong>"</div>';
            return;
        }

        results.innerHTML = '<h2 style="color:var(--champagne);margin-bottom:20px">' + data.results + ' resultado' + (data.results !== 1 ? 's' : '') + '</h2>';
        results.innerHTML += data.colecionadores.map(c => `
            <div class="collector-card" onclick="location.href='/colecionador/${c.handle}'">
                <div class="collector-name">${c.name}</div>
                <div class="collector-city">📍 ${c.city}</div>
                <div class="collector-stats">
                    <span class="stat">💎 ${c.total_cards || 0} cartas</span>
                    <span class="stat">R$ ${(c.total_value || 0).toLocaleString('pt-BR')}</span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        results.innerHTML = '<div class="empty">Erro ao buscar. Tente novamente.</div>';
        console.error(e);
    }
}

// Buscar ao carregar a página se houver query string
const params = new URLSearchParams(window.location.search);
const q = params.get('q');
if (q) {
    document.getElementById('search-input').value = q;
    buscar();
}
</script>
</body></html>"""
    return html

@app.get("/colecionadores")
def pagina_colecionadores():
    """Pagina publica com ranking de todos os colecionadores"""
    rows = db().execute("""
        SELECT u.handle, u.name, u.city, p.total_cards, p.total_value,
               (SELECT COUNT(*) FROM graded_items WHERE LOWER(owner_handle)=LOWER(u.handle) AND public=1) as graded
        FROM users u
        LEFT JOIN portfolio_stats p ON LOWER(p.user_id)=LOWER(u.handle)
        ORDER BY p.total_value DESC NULLS LAST
        LIMIT 100
    """).fetchall()

    cards_html = ""
    for i, r in enumerate(rows, 1):
        cards_html += f"""
        <div class="collector-card" onclick="location.href='/colecionador/{r['handle']}'">
            <div class="rank-badge">{i}</div>
            <div class="collector-info">
                <h3>{r['name'] or r['handle']}</h3>
                <p>📍 {r['city'] or 'Brasil'}</p>
                <div class="collector-stats">
                    <span>💎 {r['graded'] or 0} SLABS</span>
                    <span>R$ {(r['total_value'] or 0):,.0f}</span>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ranking de Colecionadores - SLABR</title>
<style>
:root{{--vault:#0c0f13;--vault-2:#13171e;--ice:#eef2f7;--mist:#97a1b0;--champagne:#e7c47a;--line:rgba(255,255,255,.07)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ice);background:linear-gradient(135deg,var(--vault) 0%,#0f1535 100%);min-height:100vh}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
header{{position:sticky;top:0;z-index:40;backdrop-filter:blur(16px);background:linear-gradient(to bottom,rgba(12,15,19,.94),rgba(12,15,19,.66));border-bottom:1px solid var(--line)}}
.bar{{display:flex;align-items:center;gap:26px;height:66px}}
.brand{{font-family:'Bricolage Grotesque';font-weight:800;font-size:19px;cursor:pointer}}
nav a{{color:var(--mist);font-size:14px;font-weight:500;padding:4px 0;border-bottom:2px solid transparent;cursor:pointer;margin-left:20px}}
nav a:hover{{color:var(--ice);border-bottom-color:var(--champagne)}}
.hero{{padding:60px 0;text-align:center;background:linear-gradient(135deg,rgba(231,196,122,.05) 0%,rgba(231,196,122,.02) 100%);border-bottom:1px solid var(--line)}}
.hero h1{{font-size:48px;margin-bottom:10px;font-weight:800;color:var(--champagne)}}
.hero p{{color:var(--mist);font-size:16px}}
.collectors{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-top:40px}}
.collector-card{{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;padding:20px;cursor:pointer;transition:all 0.3s;position:relative;overflow:hidden}}
.collector-card:hover{{border-color:var(--champagne);transform:translateY(-5px);box-shadow:0 10px 30px rgba(231,196,122,0.2)}}
.rank-badge{{position:absolute;top:10px;right:10px;background:var(--champagne);color:var(--vault);width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}}
.collector-info h3{{font-size:20px;margin-bottom:5px;color:var(--ice)}}
.collector-info p{{color:var(--mist);font-size:14px;margin-bottom:15px}}
.collector-stats{{display:flex;gap:15px;flex-wrap:wrap;font-size:13px;color:var(--mist)}}
.collector-stats span{{background:var(--vault);padding:6px 12px;border-radius:6px;border:1px solid var(--line)}}
footer{{border-top:1px solid var(--line);padding:30px 0;text-align:center;color:var(--mist);font-size:12px;margin-top:60px}}
</style>
</head><body>
<header><div class="bar"><div class="brand" onclick="location.href='/'">SLABR</div><nav><a onclick="location.href='/'">Home</a></nav></div></header>

<div class="hero">
    <div class="wrap">
        <h1>🏆 Ranking de Colecionadores</h1>
        <p>Top {len(rows)} colecionadores brasileiros ordenados por patrimônio</p>
    </div>
</div>

<div class="wrap" style="padding-top:40px">
    <div class="collectors">
        {cards_html}
    </div>
</div>

<footer><p>SLABR - Marketplace de Trading Cards | Ranking Público de Colecionadores</p></footer>
</body></html>"""
    return html

@app.get("/dashboard/<handle>")
def pagina_dashboard(handle):
    """Dashboard financeiro do colecionador"""
    user = db().execute("SELECT handle, name, city FROM users WHERE LOWER(handle)=LOWER(?)", (handle,)).fetchone()
    if not user:
        return "<h1>Colecionador nao encontrado</h1>", 404

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard - {user['name']}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<style>
:root{{--vault:#0c0f13;--vault-2:#13171e;--ice:#eef2f7;--mist:#97a1b0;--champagne:#e7c47a;--line:rgba(255,255,255,.07);--ok:#4ade80;--bad:#f87171}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ice);background:linear-gradient(135deg,var(--vault) 0%,#0f1535 100%);min-height:100vh}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
header{{position:sticky;top:0;z-index:40;backdrop-filter:blur(16px);background:linear-gradient(to bottom,rgba(12,15,19,.94),rgba(12,15,19,.66));border-bottom:1px solid var(--line);height:66px;display:flex;align-items:center}}
header a{{color:var(--mist);cursor:pointer;margin-left:20px;font-size:14px;transition:color 0.3s}}
header a:hover{{color:var(--ice);border-bottom:2px solid var(--champagne)}}
.brand{{font-family:'Bricolage Grotesque';font-weight:800;font-size:19px;color:var(--champagne)}}
.hero{{padding:40px 0;background:linear-gradient(135deg,rgba(231,196,122,.05) 0%,rgba(231,196,122,.02) 100%);border-bottom:1px solid var(--line)}}
.hero h1{{font-size:36px;margin-bottom:5px;font-weight:800;color:var(--champagne)}}
.hero p{{color:var(--mist);font-size:14px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:40px 0}}
.stat-box{{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;padding:20px;border-left:4px solid var(--champagne)}}
.stat-label{{font-size:12px;color:var(--mist);text-transform:uppercase;margin-bottom:10px;letter-spacing:0.1em}}
.stat-value{{font-size:24px;font-weight:800;color:var(--champagne)}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:30px;margin:40px 0}}
.chart-box{{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;padding:20px}}
.chart-title{{font-size:16px;font-weight:600;margin-bottom:15px;color:var(--ice)}}
.roi-table{{width:100%;margin-top:40px;border-collapse:collapse}}
.roi-table th{{text-align:left;padding:12px;border-bottom:2px solid var(--line);color:var(--mist);font-size:12px;text-transform:uppercase}}
.roi-table td{{padding:12px;border-bottom:1px solid var(--line);font-size:13px}}
.roi-table tr:hover{{background:var(--vault)}}
.roi-gain{{color:var(--ok)}}
.roi-loss{{color:var(--bad)}}
footer{{border-top:1px solid var(--line);padding:30px 0;text-align:center;color:var(--mist);font-size:12px;margin-top:60px}}
</style>
</head><body>
<header><div class="wrap" style="width:100%;display:flex;align-items:center;justify-content:space-between"><div><span class="brand">SLABR</span></div><nav style="display:flex;gap:30px"><a onclick="location.href='/home-public'">Home</a><a onclick="location.href='/colecionador/{handle}'">Perfil</a></nav></div></header>

<div class="hero"><div class="wrap"><h1>📊 Dashboard de {user['name']}</h1><p>Analise o desempenho e ROI da sua coleção</p></div></div>

<div class="wrap">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-label">Patrimônio Atual</div>
            <div class="stat-value" id="stat-current">R$ 0</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Ganho Líquido (30d)</div>
            <div class="stat-value" id="stat-change" style="color:var(--ok)">+0%</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">ROI Total</div>
            <div class="stat-value" id="stat-roi">0%</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Melhor Mês</div>
            <div class="stat-value" id="stat-best">-</div>
        </div>
    </div>

    <div class="charts">
        <div class="chart-box">
            <div class="chart-title">📈 Evolução de Patrimônio (30 dias)</div>
            <canvas id="patrimonio-chart"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">📊 Performance Mensal</div>
            <canvas id="performance-chart"></canvas>
        </div>
    </div>

    <h2 style="color:var(--champagne);margin:40px 0 20px">Top Cartas - Ganho/Perda</h2>
    <table class="roi-table">
        <thead>
            <tr>
                <th>Carta</th>
                <th>Quantidade</th>
                <th>Custo</th>
                <th>Valor Atual</th>
                <th>Ganho/Perda</th>
                <th>ROI</th>
            </tr>
        </thead>
        <tbody id="roi-tbody">
            <tr><td colspan="6" style="text-align:center;color:var(--mist)">Carregando...</td></tr>
        </tbody>
    </table>
</div>

<footer><p>SLABR - Dashboard Financeiro | Análise de Coleção</p></footer>

<script>
const API_BASE = 'http://localhost:5000';
const HANDLE = '{handle}';
let patrimonioChart, performanceChart;

async function loadDashboard() {{
    try {{
        // Carregar dados de patrimonio
        const patRes = await fetch(`${{API_BASE}}/api/dashboard/${{HANDLE}}/patrimonio`);
        const patData = await patRes.json();

        if (patData.ok) {{
            document.getElementById('stat-current').textContent = 'R$ ' + patData.current_value.toLocaleString('pt-BR');
            document.getElementById('stat-change').textContent = (patData.evolution.change_percent > 0 ? '+' : '') + patData.evolution.change_percent + '%';
            if (patData.evolution.change_percent < 0) {{
                document.getElementById('stat-change').style.color = 'var(--bad)';
            }}

            // Gráfico de Patrimonio
            const ctxPat = document.getElementById('patrimonio-chart').getContext('2d');
            patrimonioChart = new Chart(ctxPat, {{
                type: 'line',
                data: {{
                    labels: patData.evolution.labels,
                    datasets: [{{
                        label: 'Patrimônio (R$)',
                        data: patData.evolution.values,
                        borderColor: '#e7c47a',
                        backgroundColor: 'rgba(231, 196, 122, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#e7c47a'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: true, labels: {{ color: '#97a1b0' }} }} }},
                    scales: {{
                        y: {{ ticks: {{ color: '#97a1b0' }}, grid: {{ color: 'rgba(255,255,255,.07)' }} }},
                        x: {{ ticks: {{ color: '#97a1b0' }}, grid: {{ color: 'rgba(255,255,255,.07)' }} }}
                    }}
                }}
            }});
        }}

        // Carregar ROI
        const roiRes = await fetch(`${{API_BASE}}/api/dashboard/${{HANDLE}}/roi`);
        const roiData = await roiRes.json();

        if (roiData.ok) {{
            document.getElementById('stat-roi').textContent = roiData.roi_percent + '%';
            const tbody = document.getElementById('roi-tbody');
            tbody.innerHTML = roiData.cartas.map(c => `
                <tr>
                    <td><strong>${{c.card_name}}</strong><br><span style="color:var(--mist);font-size:11px">${{c.card_id}}</span></td>
                    <td>${{c.quantity}}</td>
                    <td>R$ ${{c.cost.toLocaleString('pt-BR')}}</td>
                    <td>R$ ${{c.current_value.toLocaleString('pt-BR')}}</td>
                    <td class="${{c.gain > 0 ? 'roi-gain' : 'roi-loss'}}"><strong>${{(c.gain > 0 ? '+' : '')}}R$ ${{c.gain.toLocaleString('pt-BR')}}</strong></td>
                    <td class="${{c.roi_percent > 0 ? 'roi-gain' : 'roi-loss'}}"><strong>${{(c.roi_percent > 0 ? '+' : '')}}${{c.roi_percent}}%</strong></td>
                </tr>
            `).join('');
        }}

        // Carregar Performance
        const perfRes = await fetch(`${{API_BASE}}/api/dashboard/${{HANDLE}}/performance`);
        const perfData = await perfRes.json();

        if (perfData.ok) {{
            document.getElementById('stat-best').textContent = perfData.monthly.highest_month;
            const ctxPerf = document.getElementById('performance-chart').getContext('2d');
            performanceChart = new Chart(ctxPerf, {{
                type: 'bar',
                data: {{
                    labels: perfData.monthly.labels,
                    datasets: [{{
                        label: 'Patrimônio (R$)',
                        data: perfData.monthly.values,
                        backgroundColor: '#e7c47a',
                        borderColor: '#c79a4e',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: true, labels: {{ color: '#97a1b0' }} }} }},
                    scales: {{
                        y: {{ ticks: {{ color: '#97a1b0' }}, grid: {{ color: 'rgba(255,255,255,.07)' }} }},
                        x: {{ ticks: {{ color: '#97a1b0' }}, grid: {{ color: 'rgba(255,255,255,.07)' }} }}
                    }}
                }}
            }});
        }}
    }} catch (e) {{
        console.error(e);
    }}
}}

loadDashboard();
</script>
</body></html>"""
    return html

@app.get("/catalogo")
def pagina_catalogo():
    """Catálogo de colecionadores com galerias visuais"""
    colecionadores = db().execute("""
        SELECT DISTINCT u.handle, u.name, u.city,
               COUNT(DISTINCT gi.cert_id) as total_cards,
               SUM(gi.declared_value_cents) / 100.0 as total_value
        FROM users u
        LEFT JOIN graded_items gi ON LOWER(gi.owner_handle) = LOWER(u.handle) AND gi.public = 1
        GROUP BY u.handle, u.name, u.city
        HAVING COUNT(DISTINCT gi.cert_id) > 0
        ORDER BY total_value DESC NULLS LAST
        LIMIT 100
    """).fetchall()

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo - SLABR</title>
    <style>
        :root {
            --vault: #0c0f13;
            --vault-2: #13171e;
            --vault-3: #1a1f28;
            --ice: #eef2f7;
            --mist: #97a1b0;
            --champagne: #e7c47a;
            --line: rgba(255,255,255,.07);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Inter', system-ui, sans-serif;
            color: var(--ice);
            background: linear-gradient(135deg, var(--vault) 0%, #0f1535 100%);
            min-height: 100vh;
        }
        .wrap { max-width: 1120px; margin: 0 auto; padding: 0 24px; }

        header {
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            background: linear-gradient(to bottom, rgba(12,15,19,.94), rgba(12,15,19,.66));
            border-bottom: 1px solid var(--line);
        }
        .bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 66px;
            padding: 0 24px;
        }
        .brand {
            font-size: 20px;
            font-weight: 800;
            color: var(--champagne);
            cursor: pointer;
        }
        nav {
            display: flex;
            gap: 30px;
            flex: 1;
            margin-left: 50px;
        }
        nav a {
            color: var(--mist);
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s;
            border-bottom: 2px solid transparent;
            padding-bottom: 4px;
            text-decoration: none;
        }
        nav a:hover, nav a.active {
            color: var(--ice);
            border-bottom-color: var(--champagne);
        }

        .hero {
            padding: 80px 24px;
            text-align: center;
            background: linear-gradient(135deg, rgba(231,196,122,.05) 0%, rgba(231,196,122,.02) 100%);
            border-bottom: 1px solid var(--line);
        }
        .hero h1 {
            font-size: 48px;
            margin-bottom: 20px;
            font-weight: 800;
            color: var(--champagne);
        }
        .hero p {
            color: var(--mist);
            font-size: 18px;
            margin-bottom: 30px;
        }

        section { padding: 60px 0; }
        section h2 {
            font-size: 32px;
            color: var(--champagne);
            margin-bottom: 30px;
            font-weight: 800;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 24px;
            margin-top: 40px;
        }
        .collector-card {
            background: var(--vault-2);
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s;
            cursor: pointer;
            display: flex;
            flex-direction: column;
        }
        .collector-card:hover {
            border-color: var(--champagne);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(231,196,122,0.2);
        }
        .card-header {
            padding: 20px;
            border-bottom: 1px solid var(--line);
        }
        .collector-name {
            font-size: 18px;
            font-weight: 700;
            color: var(--ice);
            margin-bottom: 5px;
        }
        .collector-city {
            font-size: 13px;
            color: var(--mist);
        }
        .card-body {
            padding: 20px;
            flex: 1;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid var(--line);
        }
        .stat-row:last-child { border: none; }
        .stat-label {
            color: var(--mist);
            font-size: 12px;
        }
        .stat-value {
            color: var(--champagne);
            font-weight: 700;
        }
        .card-footer {
            padding: 15px 20px;
            background: var(--vault-3);
            border-top: 1px solid var(--line);
        }
        .btn-primary {
            padding: 10px 16px;
            background: var(--champagne);
            color: var(--vault);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            width: 100%;
            transition: all 0.3s;
            text-decoration: none;
            display: block;
            text-align: center;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(231,196,122,0.3);
        }

        footer {
            border-top: 1px solid var(--line);
            padding: 30px 0;
            text-align: center;
            color: var(--mist);
            font-size: 12px;
            margin-top: 60px;
        }
        @media (max-width: 768px) {
            nav { gap: 15px; margin-left: 30px; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="bar">
            <div class="brand" onclick="location.href='/'">SLABR</div>
            <nav>
                <a href="/">Home</a>
                <a href="/marketplace">Marketplace</a>
                <a href="/colecionadores">Colecionadores</a>
                <a href="/catalogo" class="active">Catálogo</a>
            </nav>
        </div>
    </header>

    <div class="hero">
        <div class="wrap">
            <h1>Catálogo de Colecionadores</h1>
            <p>Explore as galerias visuais dos maiores colecionadores brasileiros</p>
        </div>
    </div>

    <div class="wrap">
        <section>
            <div class="grid">"""

    for col in colecionadores:
        value_display = f"R$ {col['total_value']:,.0f}" if col['total_value'] else "R$ 0"
        html += f"""        <div class="collector-card">
            <div class="card-header">
                <div class="collector-name">@{col['handle']}</div>
                <div class="collector-city">📍 {col['city'] or 'Brasil'}</div>
            </div>
            <div class="card-body">
                <div class="stat-row">
                    <span class="stat-label">Cartas Graduadas</span>
                    <span class="stat-value">{col['total_cards'] or 0}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Patrimônio</span>
                    <span class="stat-value">{value_display}</span>
                </div>
            </div>
            <div class="card-footer">
                <a href="/colecionador/{col['handle']}" class="btn-primary">Ver Galeria</a>
            </div>
        </div>"""

    html += """            </div>
        </section>
    </div>

    <footer class="wrap">
        <p>SLABR - Marketplace de Trading Cards | Plataforma segura para colecionadores brasileiros</p>
        <p style="margin-top: 15px; font-size: 11px; opacity: 0.7;">Catálogo | Galeria Visual | Explore Colecionadores</p>
    </footer>
</body>
</html>"""
    return html

@app.get("/colecionador/<handle>")
def pagina_colecionador(handle):
    """Pagina publica do perfil de um colecionador"""
    user = db().execute("SELECT handle, name, email, city FROM users WHERE LOWER(handle)=LOWER(?)", (handle,)).fetchone()
    if not user:
        return "<h1>Colecionador nao encontrado</h1>", 404

    stats = db().execute("SELECT total_cards, total_value FROM portfolio_stats WHERE LOWER(user_id)=LOWER(?)", (handle,)).fetchone()
    graded = db().execute("SELECT COUNT(*) as count FROM graded_items WHERE LOWER(owner_handle)=LOWER(?) AND public=1", (handle,)).fetchone()

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{user['name'] or user['handle']} - Colecionador</title>
<style>
:root{{--vault:#0c0f13;--vault-2:#13171e;--ice:#eef2f7;--mist:#97a1b0;--champagne:#e7c47a;--line:rgba(255,255,255,.07)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ice);background:linear-gradient(135deg,var(--vault) 0%,#0f1535 100%);min-height:100vh}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
header{{position:sticky;top:0;z-index:40;backdrop-filter:blur(16px);background:linear-gradient(to bottom,rgba(12,15,19,.94),rgba(12,15,19,.66));border-bottom:1px solid var(--line)}}
.bar{{display:flex;align-items:center;gap:26px;height:66px}}
.brand{{font-family:'Bricolage Grotesque';font-weight:800;font-size:19px;cursor:pointer}}
nav a{{color:var(--mist);font-size:14px;font-weight:500;padding:4px 0;border-bottom:2px solid transparent;cursor:pointer;margin-left:20px}}
nav a:hover{{color:var(--ice);border-bottom-color:var(--champagne)}}
.hero{{padding:60px 0;text-align:center;background:linear-gradient(135deg,rgba(231,196,122,.05) 0%,rgba(231,196,122,.02) 100%);border-bottom:1px solid var(--line)}}
.hero h1{{font-size:48px;margin-bottom:10px;font-weight:800;color:var(--champagne)}}
.hero p{{color:var(--mist);font-size:16px;margin:10px 0}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:40px 0}}
.stat-box{{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;padding:20px;border-left:4px solid var(--champagne)}}
.stat-label{{font-size:12px;color:var(--mist);text-transform:uppercase;margin-bottom:10px;letter-spacing:0.1em}}
.stat-value{{font-size:24px;font-weight:800;color:var(--champagne)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:20px;margin-top:30px}}
.gallery-card{{background:var(--vault-2);border:1px solid var(--line);border-radius:10px;overflow:hidden;transition:all 0.3s;cursor:pointer;animation:fadeInCard 0.5s ease-out}}
.gallery-card:hover{{border-color:var(--champagne);transform:translateY(-8px);box-shadow:0 12px 40px rgba(231,196,122,0.3)}}
@keyframes fadeInCard{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.card-image{{width:100%;aspect-ratio:2.5/3.5;background:linear-gradient(135deg,var(--vault) 0%,var(--vault-3) 100%);display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}}
.card-image img{{width:100%;height:100%;object-fit:contain;padding:8px}}
.card-image.loading{{background:linear-gradient(90deg,var(--vault-3) 25%,var(--vault) 50%,var(--vault-3) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite}}
@keyframes shimmer{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
.card-grade{{position:absolute;top:8px;right:8px;background:var(--champagne);color:var(--vault);padding:4px 8px;border-radius:4px;font-size:11px;font-weight:800}}
.card-gem{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:32px;text-shadow:0 0 8px rgba(0,0,0,0.8)}}
.card-info{{padding:12px}}
.card-name{{font-weight:600;color:var(--ice);margin-bottom:4px;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.card-value{{font-size:13px;font-weight:700;color:var(--champagne)}}
.btn{{padding:10px 20px;background:var(--champagne);color:var(--vault);border:none;border-radius:6px;cursor:pointer;font-weight:600;text-decoration:none;display:inline-block;margin-top:20px}}
.btn:hover{{opacity:0.9}}
footer{{border-top:1px solid var(--line);padding:30px 0;text-align:center;color:var(--mist);font-size:12px;margin-top:60px}}
</style>
</head><body>
<header><div class="bar"><div class="brand" onclick="location.href='/'">SLABR</div><nav><a onclick="location.href='/'">Voltar</a></nav></div></header>

<div class="hero">
    <div class="wrap">
        <h1>{user['name'] or user['handle']}</h1>
        <p>📍 {user['city'] or 'Brasil'}</p>
    </div>
</div>

<div class="wrap" style="padding-top:40px">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-label">Cartas Graduadas</div>
            <div class="stat-value">{graded['count'] if graded else 0}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Patrimônio Total</div>
            <div class="stat-value">R$ {(stats['total_value'] if stats else 0):,.0f}</div>
        </div>
    </div>

    <h2 style="font-size:24px;color:var(--champagne);margin:40px 0 20px">🖼️ Galeria de Cartas</h2>
    <div id="cards-grid" class="gallery">
        <div style="text-align:center;padding:40px;color:var(--mist);grid-column:1/-1">Carregando galeria...</div>
    </div>

    <a href="https://wa.me/?text=Oi%20{user['handle']}%20vi%20sua%20colecao%20no%20SLABR" class="btn" target="_blank">💬 Contatar no WhatsApp</a>
</div>

<footer><p>SLABR - Marketplace de Trading Cards | Perfis Públicos de Colecionadores</p></footer>

<script>
async function loadGaleria() {{
    try {{
        const res = await fetch('/api/perfil/{handle}/galeria');
        const data = await res.json();
        const grid = document.getElementById('cards-grid');

        if (!data.cartas || data.cartas.length === 0) {{
            grid.innerHTML = '<div style="text-align:center;padding:40px;color:var(--mist);grid-column:1/-1">Nenhuma carta graduada pública</div>';
            return;
        }}

        grid.innerHTML = data.cartas.map((c) => `
            <div class="gallery-card">
                <div class="card-image loading" id="img-${{c.cert}}">
                    <img src="${{c.image}}" alt="${{c.cardName}}" onload="this.parentElement.classList.remove('loading')" onerror="this.parentElement.textContent='Erro'">
                    <span class="card-grade">${{c.grade}}</span>
                    ${{c.gem ? '<span class="card-gem">✨</span>' : ''}}
                </div>
                <div class="card-info">
                    <div class="card-name">${{c.cardName}}</div>
                    <div class="card-value">R$ ${{(c.value || 0).toLocaleString('pt-BR')}}</div>
                </div>
            </div>
        `).join('');
    }} catch (e) {{
        console.error('Erro ao carregar galeria:', e);
        const grid = document.getElementById('cards-grid');
        if (grid) {{
            grid.innerHTML = '<div style="grid-column:1/-1;color:#ef4444;padding:20px;text-align:center">Erro ao carregar galeria. Tente recarregar a página.</div>';
        }}
    }}
}}
document.addEventListener('DOMContentLoaded', loadGaleria);
</script>
<style>
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>
</body></html>"""
    return html

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

@app.get("/api/bynx/sincronizar")
def bynx_sincronizar():
    """Sincronização com Bynx.gg - comparação de preços e oportunidades"""
    try:
        import urllib.request
        import json as json_lib

        # Top cards do SLABR by value
        slabr_cards = db().execute("""
            SELECT DISTINCT c.id, c.name, c.official_image_large,
                   COUNT(*) as qty,
                   AVG(g.declared_value_cents) / 100.0 as slabr_price
            FROM cards c
            JOIN graded_items g ON g.card_id = c.id
            WHERE g.public = 1
            GROUP BY c.id
            ORDER BY AVG(g.declared_value_cents) DESC
            LIMIT 20
        """).fetchall()

        result = []
        for card in slabr_cards:
            # Simular busca no Bynx (em produção, usar API real do Bynx)
            # Aqui vamos usar dados de comparação baseado em TCGPlayer via PokemonTCG API
            try:
                # Buscar price data
                prices = db().execute(
                    "SELECT market FROM card_prices WHERE card_id=? LIMIT 1",
                    (card["id"],)
                ).fetchone()

                bynx_price = float(prices["market"] or 0) * EUR_BRL if prices else 0

                diff = card["slabr_price"] - bynx_price
                diff_percent = ((diff / bynx_price) * 100) if bynx_price > 0 else 0

                # Oportunidades: cartas 10%+ mais caras no SLABR (buy no Bynx)
                # ou 10%+ mais baratas no SLABR (sell no SLABR)
                if abs(diff_percent) > 10:
                    result.append({
                        "cardId": card["id"],
                        "cardName": card["name"],
                        "image": card["official_image_large"],
                        "qty": card["qty"],
                        "slabr_price": round(card["slabr_price"], 2),
                        "bynx_price": round(bynx_price, 2),
                        "diff_reais": round(diff, 2),
                        "diff_percent": round(diff_percent, 2),
                        "oportunidade": "vender_slabr" if diff > 0 else "comprar_bynx"
                    })
            except Exception as e:
                continue

        return jsonify({
            "ok": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "total_opportunities": len(result),
            "opportunities": result[:10]  # Top 10 oportunidades
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ---- Sincronização automática com Bynx (1x por dia) ----
def sync_bynx_daily():
    """Sincroniza preços com Bynx uma vez por dia"""
    try:
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Atualizar tabela de sincronização (se não existir, criar)
        cur.execute("""CREATE TABLE IF NOT EXISTS bynx_sync_log (
            id INTEGER PRIMARY KEY,
            card_id TEXT,
            slabr_price REAL,
            bynx_price REAL,
            diff_percent REAL,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Top 50 cards por valor
        cards = cur.execute("""
            SELECT DISTINCT c.id, c.name,
                   AVG(g.declared_value_cents) / 100.0 as slabr_price
            FROM cards c
            JOIN graded_items g ON g.card_id = c.id
            WHERE g.public = 1
            GROUP BY c.id
            ORDER BY AVG(g.declared_value_cents) DESC
            LIMIT 50
        """).fetchall()

        for card in cards:
            prices = cur.execute(
                "SELECT market FROM card_prices WHERE card_id=? LIMIT 1",
                (card["id"],)
            ).fetchone()

            bynx_price = float(prices["market"] or 0) * EUR_BRL if prices else 0
            diff_percent = ((card["slabr_price"] - bynx_price) / bynx_price * 100) if bynx_price > 0 else 0

            # Log da sincronização
            cur.execute("""INSERT INTO bynx_sync_log (card_id, slabr_price, bynx_price, diff_percent)
                          VALUES (?, ?, ?, ?)""",
                       (card["id"], card["slabr_price"], bynx_price, diff_percent))

        con.commit()
        con.close()
        print(f"[SYNC] Sincronização Bynx concluída: {len(cards)} cards")
    except Exception as e:
        print(f"[SYNC] Erro na sincronização: {e}")

# Iniciar scheduler se disponível
if SCHEDULER_AVAILABLE:
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_bynx_daily, 'cron', hour=3, minute=0)  # 3 da manhã todo dia
    scheduler.start()
    print("[SCHEDULER] Sincronização Bynx agendada diariamente às 3:00 AM")

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
