import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime

# ============================================
# APNI DETAILS YAHAN BHARO
# ============================================
EMAIL_SENDER = "surajvaidya85@gmail.com"      # tumhari gmail
EMAIL_PASSWORD = "bvnsumkzahcwbceu"         # 16 digit app password
EMAIL_RECEIVER = "surajvaidya85@gmail.com"     # jahan alert chahiye
# ============================================

# NSE F&O Stocks list (top symbols)
FO_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ONGC.NS", "NTPC.NS",
    "POWERGRID.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "TECHM.NS", "HCLTECH.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "BAJAJFINSV.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HEROMOTOCO.NS", "INDUSINDBK.NS", "M&M.NS",
    "CIPLA.NS", "BPCL.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "TATACONSUM.NS"
]

alerted_today = set()

def get_previous_month_high(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo", interval="1mo")
        if len(df) >= 2:
            prev_month_high = df['High'].iloc[-2]
            return round(prev_month_high, 2)
    except:
        pass
    return None

def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m")
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
    except:
        pass
    return None

def send_email(symbol, current_price, prev_high):
    try:
        subject = f"🚀 Breakout Alert: {symbol.replace('.NS', '')}"
        body = f"""
MONTHLY BREAKOUT ALERT!

Stock     : {symbol.replace('.NS', '')}
Prev Month High : ₹{prev_high}
Current Price   : ₹{current_price}
Time      : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

Price has broken above previous monthly high!
        """
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"✅ Email sent for {symbol}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def check_breakouts():
    print(f"\n🔍 Checking breakouts at {datetime.now().strftime('%H:%M:%S')}...")
    for symbol in FO_STOCKS:
        if symbol in alerted_today:
            continue
        prev_high = get_previous_month_high(symbol)
        current_price = get_current_price(symbol)
        if prev_high and current_price:
            if current_price > prev_high:
                print(f"🚀 BREAKOUT: {symbol} | Price: {current_price} | Prev High: {prev_high}")
                send_email(symbol, current_price, prev_high)
                alerted_today.add(symbol)
            else:
                print(f"  {symbol.replace('.NS','')} | {current_price} | High: {prev_high}")

# Reset alerts daily at midnight
def reset_alerts():
    alerted_today.clear()
    print("🔄 Daily reset done")

# Schedule
schedule.every(30).minutes.do(check_breakouts)
schedule.every().day.at("00:01").do(reset_alerts)

print("🤖 Breakout Bot Started!")
print("📧 Alerts will be sent to:", EMAIL_RECEIVER)
check_breakouts()  # Pehli baar turant chalao

while True:
    schedule.run_pending()
    time.sleep(60)