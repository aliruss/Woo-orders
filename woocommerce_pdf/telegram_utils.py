import os
import requests
import json

def format_currency(value):
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return value

def send_to_telegram(order, pdf_path):
    """Send the generated PDF to a Telegram group and the specific sales expert."""
    token = os.getenv('TG_BOT_TOKEN')
    group_id = os.getenv('TG_GROUP_ID')
    
    if not token:
        return

    order_id = order.get('id')
    first_name = order.get('billing', {}).get('first_name', '')
    last_name = order.get('billing', {}).get('last_name', '')
    total = format_currency(order.get('total', '0'))
    payment_method = order.get('payment_method_title', 'نامشخص')
    issuer = order.get('admin_issuer', 'مشتری (خرید آنلاین)')
    
    # Format line items
    items = []
    for item in order.get('line_items', []):
        items.append(f"▪️ {item.get('name')} (تعداد: {item.get('quantity')})")
    items_str = "\n".join(items)
    
    caption = (
        f"📄 فاکتور جدید صادر شد\n"
        f"🛍 شماره سفارش: {order_id}\n"
        f"👤 مشتری: {first_name} {last_name}\n"
        f"💳 شیوه پرداخت: {payment_method}\n"
        f"👨‍💻 صادرکننده: {issuer}\n"
        f"💰 مبلغ کل: {total} تومان\n\n"
        f"📦 محصولات:\n{items_str}"
    )
    
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
        if meta.get('key') == 'issuer_id':
            issuer_id = str(meta.get('value'))
        elif meta.get('key') == '_edit_last' and not issuer_id:
            issuer_id = str(meta.get('value'))
    
    if issuer_id:
        try:
            if os.path.exists('telegram_users.json'):
                with open('telegram_users.json', 'r', encoding='utf-8') as f:
                    users_map = json.load(f)
                
                expert_chat_id = users_map.get(issuer_id)
                if expert_chat_id:
                    with open(pdf_path, 'rb') as f:
                        res = requests.post(url, data={'chat_id': expert_chat_id, 'caption': caption}, files={'document': f})
                        
                        if res.status_code == 403:
                            print(f"❌ خطا: ربات اجازه ارسال پیام به کارشناس (ID: {issuer_id}) را ندارد. کارشناس باید ابتدا ربات را در تلگرام Start کند.")
                        else:
                            res.raise_for_status()
                            print(f"✅ فاکتور به کارشناس فروش (ID: {issuer_id}) ارسال شد.")
                else:
                    print(f"⚠️ آیدی تلگرام برای کارشناس فروش (ID: {issuer_id}) در فایل telegram_users.json یافت نشد.")
        except Exception as e:
            print(f"❌ خطا در ارسال به کارشناس فروش: {e}")
