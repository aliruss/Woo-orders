from flask import Flask, request, jsonify
from main import generate_pdf

app = Flask(__name__)

@app.route('/webhook/order-created', methods=['POST'])
def order_created():
    """
    Webhook endpoint to receive WooCommerce 'Order Created' events.
    Configure this URL in WooCommerce > Settings > Advanced > Webhooks.
    """
    order = request.json
    
    if not order or 'id' not in order:
        return jsonify({"error": "Invalid order data received"}), 400
    
    try:
        # Generate PDF for the received order
        pdf_path = generate_pdf(order)
        return jsonify({
            "status": "success", 
            "message": f"PDF generated for order {order['id']}",
            "path": pdf_path
        }), 200
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on port 5000
    print("Starting WooCommerce Webhook Listener on port 5000...")
    app.run(host='0.0.0.0', port=5000)
