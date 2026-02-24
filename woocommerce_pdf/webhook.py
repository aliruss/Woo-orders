from flask import Flask, request, jsonify
from main import generate_pdf
from telegram_utils import send_to_telegram
import logging
import hmac
import hashlib
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Disable extra logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

WC_WEBHOOK_SECRET = os.getenv('WC_WEBHOOK_SECRET', '')

@app.route('/', methods=['GET', 'POST'])
def health_check():
    return "Webhook listener is running!", 200

@app.route('/webhook/order-created', methods=['POST'])
def order_created():
    print("📥 New request received...")
    
    # Validate Webhook Signature
    if WC_WEBHOOK_SECRET:
        signature = request.headers.get('X-WC-Webhook-Signature')
        
        # WooCommerce calculates the HMAC-SHA256 hash of the *raw* request body
        payload = request.get_data()
        secret = WC_WEBHOOK_SECRET.encode('utf-8')
        
        expected_sig = base64.b64encode(hmac.new(secret, payload, hashlib.sha256).digest()).decode('utf-8')
        
        if not signature or not hmac.compare_digest(expected_sig, signature):
            print("❌ Error: Invalid Webhook Signature! Secret key mismatch.")
            print(f"   Received Signature: {signature}")
            print(f"   Expected Signature: {expected_sig}")
            return jsonify({"error": "Invalid signature"}), 401
        else:
            print("🔒 Webhook Signature verified successfully.")

    # Try to parse JSON
    order = None
    
    # Method 1: Standard JSON parsing
    if request.is_json:
        order = request.get_json(silent=True)
        
    # Method 2: Force JSON parsing (if content-type is missing)
    if not order:
        order = request.get_json(force=True, silent=True)
        
    # Method 3: Sometimes WooCommerce sends URL-encoded form data or raw bytes
    if not order:
        try:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                # Check if it looks like a URL-encoded string (e.g., action=woocommerce_ping)
                if 'webhook_id=' in raw_data or 'action=' in raw_data:
                    # It's a ping or form data, convert to dict
                    order = request.form.to_dict()
                else:
                    # Try manual JSON parsing
                    order = json.loads(raw_data)
        except Exception as e:
            print(f"⚠️ Failed to parse raw data: {e}")

    if not order:
        print("❌ Error: No valid JSON payload received.")
        print(f"   Raw Data snippet: {request.get_data(as_text=True)[:100]}")
        return jsonify({"error": "No JSON payload"}), 400
        
    # Handle WooCommerce Ping Request
    if 'webhook_id' in order and 'id' not in order:
        print("✅ WooCommerce Ping received successfully!")
        return jsonify({"status": "success", "message": "Ping received"}), 200
    
    if 'id' not in order:
        print("❌ Error: Invalid order data (Missing ID).")
        return jsonify({"error": "Invalid order data received"}), 400
    
    print(f"📦 Processing Order #{order['id']}...")
    try:
        # Generate PDF for the received order
        pdf_path = generate_pdf(order)
        print(f"✅ PDF generated successfully: {pdf_path}")
        
        # Send to Telegram
        send_to_telegram(order, pdf_path)
        
        return jsonify({
            "status": "success", 
            "message": f"PDF generated for order {order['id']}",
            "path": pdf_path
        }), 200
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting WooCommerce Webhook Listener on port 5000...")
    print("👉 Your Webhook URL for WooCommerce:")
    print("   https://orders.sabtic.ir/webhook/order-created")
    app.run(host='0.0.0.0', port=5000)
