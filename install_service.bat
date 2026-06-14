@echo off
cd C:\Users\ltasca\Documents\Slab\slabr-br
echo [*] Instalando servi?o cloudflared...
cloudflared.exe service install
if %ERRORLEVEL% EQU 0 (
    echo [OK] Servi?o instalado!
    echo [*] Iniciando servi?o...
    cloudflared.exe service start
    echo [OK] Servi?o iniciado!
) else (
    echo [ERRO] Falha na instala??o
)
pause
