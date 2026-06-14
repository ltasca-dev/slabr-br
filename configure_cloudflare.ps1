# SLABR - Cloudflare Tunnel Configuration Script (PowerShell)
# Execute: .\configure_cloudflare.ps1

Write-Output ""
Write-Output "======================================================================"
Write-Output "  SLABR - CLOUDFLARE TUNNEL CONFIGURATION"
Write-Output "======================================================================"
Write-Output ""

# Variáveis
$tunnelName = "slabr"
$localUrl = "http://localhost:5000"
$cloudflaredPath = "C:\Users\ltasca\Documents\Slab\slabr-br\cloudflared.exe"
$cloudflaredDir = "C:\Users\ltasca\.cloudflared"

# Verificar se cloudflared existe
if (-not (Test-Path $cloudflaredPath)) {
    Write-Output "[ERRO] cloudflared.exe nao encontrado!"
    Write-Output "Instale via: npm install -g @cloudflare/wrangler"
    exit 1
}

Write-Output "[*] cloudflared encontrado: $cloudflaredPath"
Write-Output ""

# STEP 1: Login
Write-Output "====== STEP 1: Autorizar no Cloudflare ======"
Write-Output ""
Write-Output "Uma janela do navegador vai abrir."
Write-Output "Clique em 'Authorize' para permitir que cloudflared acesse sua conta."
Write-Output ""
Write-Output "Pressione ENTER quando a autorizacao estiver completa..."
Read-Host

Write-Output ""
Write-Output "[*] Executando: cloudflared tunnel login"
& $cloudflaredPath tunnel login

if ($LASTEXITCODE -ne 0) {
    Write-Output "[ERRO] Login falhou!"
    exit 1
}

Write-Output "[OK] Login concluido!"
Start-Sleep -Seconds 2

# STEP 2: Criar tunnel
Write-Output ""
Write-Output "====== STEP 2: Criar Named Tunnel ======"
Write-Output "[*] Criando tunnel '$tunnelName'..."
& $cloudflaredPath tunnel create $tunnelName

if ($LASTEXITCODE -ne 0) {
    Write-Output "[WARN] Tunnel pode ja existir. Continuando..."
}

Start-Sleep -Seconds 1

# STEP 3: Listar tunnels
Write-Output ""
Write-Output "====== STEP 3: Obter ID do Tunnel ======"
Write-Output "[*] Listando tunnels..."
$tunnelList = & $cloudflaredPath tunnel list
Write-Output $tunnelList

Write-Output ""
Write-Output "[!] Procure pela linha com seu tunnel 'slabr' e anote o ID"
Write-Output ""

# STEP 4: Criar config.yaml
Write-Output "====== STEP 4: Criar Arquivo de Configuracao ======"
Write-Output ""

$domainInput = Read-Host "Digite seu dominio Cloudflare (ex: exemplo.com)"
if (-not $domainInput) {
    $domainInput = "seu-dominio.com"
    Write-Output "[INFO] Usando dominio padrao: $domainInput"
}

# Obter o ID do tunnel
$tunnelListJson = & $cloudflaredPath tunnel list --output json
$tunnels = $tunnelListJson | ConvertFrom-Json
$tunnelId = ($tunnels | Where-Object { $_.name -eq $tunnelName }).id

if (-not $tunnelId) {
    Write-Output "[ERRO] Nao conseguiu obter o ID do tunnel!"
    Write-Output "Por favor, configure manualmente o arquivo config.yaml"
    exit 1
}

Write-Output "[OK] Tunnel ID encontrado: $tunnelId"

# Criar arquivo config.yml
$configContent = @"
tunnel: $tunnelName
credentials-file: $cloudflaredDir\$tunnelId.json

ingress:
  - hostname: slabr.$domainInput
    service: $localUrl
  - service: http_status:404
"@

$configPath = "$cloudflaredDir\config.yml"
$configContent | Out-File -FilePath $configPath -Encoding UTF8 -Force

Write-Output "[OK] Configuracao salva em: $configPath"
Write-Output ""

Write-Output "====== PROXIMOS PASSOS ======"
Write-Output ""
Write-Output "1. Acesse: https://dash.cloudflare.com"
Write-Output "2. Selecione seu dominio: $domainInput"
Write-Output "3. Vá em: Zero Trust > Networks > Tunnels"
Write-Output "4. Clique em '$tunnelName' tunnel"
Write-Output "5. Na seção 'Public hostname', clique em '+ Create public hostname'"
Write-Output "6. Configure:"
Write-Output "   - Subdomain: slabr"
Write-Output "   - Domain: $domainInput"
Write-Output "   - Type: HTTP"
Write-Output "   - URL: $localUrl"
Write-Output "7. Clique em 'Save hostname'"
Write-Output ""

# STEP 5: Instalar como servico
Write-Output "====== STEP 5: Instalar como Servico Windows (24/7) ======"
Write-Output ""
Write-Output "Opcao A: Servico Windows (recomendado)"
Write-Output "  Comando: cloudflared.exe service install"
Write-Output "           cloudflared.exe service start"
Write-Output ""
Write-Output "Opcao B: Terminal aberto"
Write-Output "  Comando: cloudflared.exe tunnel run slabr"
Write-Output ""

$installService = Read-Host "Instalar como servico Windows? (S/N)"
if ($installService -eq "S" -or $installService -eq "s") {
    Write-Output ""
    Write-Output "[*] Instalando servico Windows..."
    & $cloudflaredPath service install

    if ($LASTEXITCODE -eq 0) {
        Write-Output "[OK] Servico instalado!"

        $startService = Read-Host "Iniciar o servico agora? (S/N)"
        if ($startService -eq "S" -or $startService -eq "s") {
            Write-Output "[*] Iniciando servico..."
            & $cloudflaredPath service start
            Write-Output "[OK] Servico iniciado!"
            Write-Output ""
            Write-Output "SLABR agora esta online 24/7!"
            Write-Output "Acesse: https://slabr.$domainInput"
        }
    } else {
        Write-Output "[ERRO] Falha ao instalar servico"
    }
} else {
    Write-Output ""
    Write-Output "Para manter o tunnel ativo, execute manualmente:"
    Write-Output "  cloudflared.exe tunnel run slabr"
    Write-Output ""
    Write-Output "Mantenha a janela terminal aberta!"
}

Write-Output ""
Write-Output "====== CONFIGURACAO CONCLUIDA ======"
Write-Output ""
Write-Output "Teste o acesso em:"
Write-Output "  https://slabr.$domainInput/home-public"
Write-Output ""
