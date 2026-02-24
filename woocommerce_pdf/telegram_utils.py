import os
import requests
import json

def send_to_telegram(order, pdf_path):
    """Send the generated PDF to a Telegram group and the specific sales expert."""
    token = os.getenv('TG_BOT_TOKEN')
    group_id = os.getenv('TG_GROUP_ID')
    
    if not token:
        return

    order_id = order.get('id')
    first_name = order.get('billing', {}).get('first_name', '')
    last_name = order.get('billing', {}).get('last_name', '')
    total = order.get('total', '0')
    
    caption = f"📄 فاکتور جدید صادر شد\n🛍 شماره سفارش: {order_id}\n👤 مشتری: {first_name} {last_name}\n💰 مبلغ: {total} تومان"
    
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    # 1. Send to Managers Group
    if group_id:
        try:
            with open(pdf_path, 'rb') as f:
                res = requests.post(url, data={'chat_id': group_id, 'caption': caption}, files={'document': f})
                res.raise_for_status()
            print("✅ فاکتور به گروه تلگرام مدیران ارسال شد.")
        except Exception as e:
            print(f"❌ خطا در ارسال به گروه تلگرام: {e}")

    # 2. Send to Sales Expert (Private Message)
    issuer_id = None
    for meta in order.get('meta_data', []):
        # WooCommerce stores the user ID of the last editor in _edit_last
        if meta.get('key') == '_edit_last' or meta.get('key') == 'issuer_id':
            issuer_id = str(meta.get('value'))
    
    if issuer_id:
        try:
            if os.path.exists('telegram_users.json'):
                with open('telegram_users.json', 'r', encoding='utf-8') as f:
                    users_map = json.load(f)
                
                expert_chat_id = users_map.get(issuer_id)
                if expert_chat_id:
                    with open(pdf_path, 'rb') as f:
                        requests.post(url, data={'chat_id': expert_chat_id, 'caption': caption}, files={'document': f})
                    print(f"✅ فاکتور به کارشناس فروش (ID: {issuer_id}) ارسال شد.")
        except Exception as e:
            print(f"❌ خطا در ارسال به کارشناس فروش: {e}")
