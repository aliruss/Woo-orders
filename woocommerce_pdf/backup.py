import os
import time
import shutil
from woocommerce import API
from dotenv import load_dotenv
from main import generate_pdf

# Load environment variables
load_dotenv()

def backup_orders():
    """
    Fetch all orders from WooCommerce API and generate PDFs (Invoice ONLY).
    Saves them in a backup folder and zips the result.
    """
    wc_url = os.getenv("WC_URL")
    wc_key = os.getenv("WC_KEY")
    wc_secret = os.getenv("WC_SECRET")

    if not all([wc_url, wc_key, wc_secret]):
        print("❌ Error: WooCommerce API credentials (WC_URL, WC_KEY, WC_SECRET) are not set in .env")
        return

    # Initialize WooCommerce API Client
    wcapi = API(
        url=wc_url,
        consumer_key=wc_key,
        consumer_secret=wc_secret,
        version="wc/v3",
        timeout=30
    )

    backup_dir = "backup_pdfs"
    os.makedirs(backup_dir, exist_ok=True)

    page = 1
    per_page = 20 # Keep it low to avoid server overload
    total_downloaded = 0

    print("🚀 Starting WooCommerce Order Backup...")
    print(f"Connecting to {wc_url}...")
    
    while True:
        print(f"⏳ Fetching page {page}...")
        try:
            # Fetch orders from API
            res = wcapi.get("orders", params={"per_page": per_page, "page": page})
            res.raise_for_status()
            orders = res.json()
        except Exception as e:
            print(f"❌ Failed to fetch orders: {e}")
            break

        if not orders:
            print("✅ No more orders to fetch.")
            break

        for order in orders:
            try:
                # Generate PDF (skip packing slip)
                generate_pdf(order, output_dir=backup_dir, skip_packing_slip=True)
                total_downloaded += 1
            except Exception as e:
                print(f"⚠️ Failed to generate PDF for order {order.get('id')}: {e}")

        page += 1
        
        # Sleep to prevent overloading the WooCommerce server
        time.sleep(2)

    if total_downloaded > 0:
        print(f"📦 Downloaded {total_downloaded} orders. Creating zip archive...")
        
        # Create zip file
        zip_filename = "woocommerce_backup"
        shutil.make_archive(zip_filename, 'zip', backup_dir)
        
        print(f"🎉 Backup complete! Archive saved as {zip_filename}.zip")
    else:
        print("⚠️ No orders were downloaded.")

if __name__ == "__main__":
    backup_orders()
