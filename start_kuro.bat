@echo off
setlocal
title Kuro AI Launcher

:: Define colors
set "RESET= [0m"
set "CYAN= [36m"
set "GREEN= [32m"
set "RED= [31m"

cls

echo.
echo  %CYAN%=====================================================================%RESET%
echo  %CYAN%   __ __                    _______  __     %RESET%
echo  %CYAN%  |  |  |.--.--.----.----. |   _   ||  |    %RESET%
echo  %CYAN%  |  |  ||  |  |   _|  __| |       ||  |    %RESET%
echo  %CYAN%  |__|__||_____|__| |____| |___|___||__|    %RESET%
echo  %CYAN%                                            %RESET%
echo  %CYAN%      SYSTEM INITIALIZATION PROTOCOL        %RESET%
echo  %CYAN%=====================================================================%RESET%
echo.

:: Check for .env file
if not exist "backend\.env" (
    echo  %RED%[!] WARNING: backend\.env file not found.%RESET%
    echo  %RED%    Please ensure you have configured your API keys.%RESET%
    echo.
    timeout /t 3 >nul
)

echo  %GREEN%[*] Starting Kuro Backend Server...%RESET%
start "Kuro Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a bit for backend to initialize
timeout /t 2 >nul

echo  %GREEN%[*] Starting Kuro Frontend Interface...%RESET%
start "Kuro Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  %CYAN%=====================================================================%RESET%
echo  %GREEN%   SYSTEMS ONLINE. ACCESS TERMINALS FOR LOGS.   %RESET%
echo  %CYAN%=====================================================================%RESET%
echo.
pause
