# SLABR 2.0 - Setup Cloudflare Tunnel

## Status Atual

✓ **Servidor Local Rodando:**
- URL: `http://localhost:5000`
- Porta: 5000
- Status: Online
- Arquivo: `server.py` (servidor HTTP simples)

---

## Setup Cloudflare Tunnel (5 minutos)

### Passo 1: Baixar cloudflared

**Windows:**
```powershell
# Download
$url = "https://github.com/cloudflare/cloudflared/releases/download/2024.6.1/cloudflared-windows-amd64.exe"
Invoke-WebRequest -Uri $url -OutFile "C:\Users\ltasca\cloudflared.exe"

# Ou use chocolatey:
choco install cloudflared
```

**Alternativa (direto):**
Baixar em: https://github.com/cloudflare/cloudflared/releases
Procurar por: `cloudflared-windows-amd64.exe`

### Passo 2: Login com Cloudflare

```powershell
# Navegar até o diretório
cd "C:\Users\ltasca\Documents\Slab\slabr-br"

# Fazer login (abrirá navegador)
cloudflared tunnel login

# Selecionar seu domínio no navegador
# Autorizar o acesso
```

### Passo 3: Criar Tunnel

```powershell
# Criar tunnel chamado "slabr"
cloudflared tunnel create slabr

# Output será algo como:
# Tunnel ID: abc123def456...
# Credentials file saved to: C:\Users\ltasca\.cloudflared\abc123def456...json
```

### Passo 4: Configurar

Criar arquivo `C:\Users\ltasca\Documents\Slab\slabr-br\config.yml`:

```yaml
tunnel: slabr
credentials-file: C:\Users\ltasca\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: slabr.seudominio.com.br
    service: http://localhost:5000
  - hostname: api.slabr.seudominio.com.br
    service: http://localhost:5000
  - service: http_status:404
```

**Substitua:**
- `slabr.seudominio.com.br` → seu domínio real
- `<TUNNEL_ID>` → ID do tunnel criado (veja no ~/.cloudflared/)

### Passo 5: Rodar Tunnel

```powershell
# Iniciar tunnel
cloudflared tunnel run slabr

# Output:
# 2024-06-14T14:30:00Z inf Tunnel running
# 2024-06-14T14:30:01Z inf Connected to Cloudflare
```

### Passo 6: Configurar DNS no Cloudflare

1. Acesse: https://dash.cloudflare.com/
2. Selecione seu domínio
3. Vá para: DNS Records
4. Adicione CNAME records:

```
Name: slabr              Type: CNAME    Content: <TUNNEL_ID>.cfargotunnel.com
Name: api.slabr          Type: CNAME    Content: <TUNNEL_ID>.cfargotunnel.com
```

---

## URLs Públicas (após setup)

| Recurso | URL |
|---------|-----|
| **Home** | https://slabr.seudominio.com.br |
| **API** | https://api.slabr.seudominio.com.br/api/* |
| **Local** | http://localhost:5000 |

---

## Alternativa: Usando ngrok (Mais Simples)

Se não tem Cloudflare ou quer mais rápido:

### 1. Instalar ngrok
```powershell
choco install ngrok
# ou baixar em: https://ngrok.com/download
```

### 2. Autenticar
```powershell
ngrok config add-authtoken <seu-token-ngrok>
```

### 3. Criar Tunnel
```powershell
ngrok http 5000
```

**Resultado:**
```
Session Status                online
Account                       seu-email@example.com
Version                       3.0.0
Region                        us (United States)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040

Forwarding                    https://abc-123-456.ngrok.io -> http://localhost:5000
```

### URL Pública:
`https://abc-123-456.ngrok.io` (muda a cada execução)

---

## Verificar Setup

```bash
# Testar localhost
curl http://localhost:5000

# Testar Cloudflare (após setup)
curl https://slabr.seudominio.com.br

# Ver logs
cloudflared tunnel logs slabr
```

---

## Para Produção

**Recomendações:**
1. ✓ Usar Cloudflare (domínio próprio, HTTPS automático)
2. ✓ Configurar ratelimit no Cloudflare
3. ✓ Ativar WAF (Web Application Firewall)
4. ✓ Setup backup tunnel com outra máquina
5. ✓ Monitorar com Cloudflare Analytics

**Cloudflare Settings:**
- SSL/TLS: Full (Strict)
- HTTP → HTTPS: Always
- Minify: CSS, JavaScript, HTML
- Caching: Standard
- Browser Cache TTL: 4 hours

---

## Troubleshooting

**"Connection refused"**
- Verifique se `python server.py` está rodando
- Confira porta 5000: `netstat -ano | findstr :5000`

**"Tunnel unreachable"**
- Reinicie cloudflared
- Verifique firewall/antivírus

**"DNS not resolving"**
- Aguarde propagação DNS (5-30 min)
- Force refresh: `ipconfig /flushdns`

---

## Status Dashboard

- **Local:** http://localhost:5000
- **Cloudflare:** https://dash.cloudflare.com/ → Seu Domínio → Analytics
- **Tunnel Status:** https://dash.cloudflare.com/ → Cron Jobs → Tunnel "slabr"

---

*Setup Cloudflare Tunnel para SLABR 2.0*
