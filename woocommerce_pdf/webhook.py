from flask import Flask, request, jsonify
from main import generate_pdf
import logging

app = Flask(__name__)

# غیرفعال کردن لاگ‌های اضافی (مثل اسکنرهای اینترنتی که خطای 404 می‌دهند)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods=['GET', 'POST'])
def health_check():
    return "Webhook listener is running!", 200

@app.route('/webhook/order-created', methods=['POST'])
def order_created():
    print("📥 درخواست جدید دریافت شد...")
    
    # دریافت JSON حتی اگر هدر Content-Type دقیقاً تنظیم نشده باشد
    order = request.get_json(force=True, silent=True)
    
    if not order:
        print("❌ خطا: هیچ دیتای JSON ای دریافت نشد.")
        return jsonify({"error": "No JSON payload"}), 400
        
    # ووکامرس در زمان ثبت Webhook یک درخواست Ping می‌فرستد
    if 'webhook_id' in order and 'id' not in order:
        print("✅ درخواست Ping ووکامرس با موفقیت دریافت شد!")
        return jsonify({"status": "success", "message": "Ping received"}), 200
    
    if 'id' not in order:
        print("❌ خطا: دیتای سفارش نامعتبر است (بدون ID).")
        return jsonify({"error": "Invalid order data received"}), 400
    
    print(f"📦 در حال پردازش سفارش شماره {order['id']}...")
    try:
        # Generate PDF for the received order
        pdf_path = generate_pdf(order)
        print(f"✅ فاکتور با موفقیت ساخته شد: {pdf_path}")
        return jsonify({
            "status": "success", 
            "message": f"PDF generated for order {order['id']}",
            "path": pdf_path
        }), 200
    except Exception as e:
        print(f"❌ خطا در ساخت فاکتور: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on port 5000
    print("🚀 Starting WooCommerce Webhook Listener on port 5000...")
    print("👉 آدرس وب‌هوک شما برای ثبت در ووکامرس:")
    print("   http://YOUR_SERVER_IP:5000/webhook/order-created")
    app.run(host='0.0.0.0', port=5000)
