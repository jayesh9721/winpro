@echo off
echo.
echo  ==========================================
echo   CampaignIQ - MATRIX Hackathon 2026
echo   AI Campaign Intelligence Platform
echo  ==========================================
echo.
echo  [1/2] Installing dependencies...
pip install -r requirements.txt
echo.
echo  [2/2] Launching app...
echo  Opening: http://localhost:8501
echo.
streamlit run app.py
pause
