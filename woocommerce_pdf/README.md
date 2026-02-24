# WooCommerce PDF Generator (Production Ready)

A Python script to generate PDF invoices and packing slips from WooCommerce order JSON. It focuses on minimizing paper usage by intelligently placing the packing slip on the same page as the invoice if there is enough space.

## Features
- **Smart Layout**: Calculates invoice height and places the packing slip on the same page if it takes less than 65% of the A4 height.
- **RTL Persian Typography**: Embeds custom Persian fonts.
- **Webhook Listener**: Automatically receive orders from WooCommerce and generate PDFs.
- **Bulk Backup**: Fetch all orders from your site via API, generate invoices (without packing slips), and zip them.
- **Admin Issuer**: Automatically shows the issuer name if the order was created by an admin.
- **Product Links**: Clicking on a product name in the PDF opens the product page on your site.

## Prerequisites
- Python 3.8+
- System dependencies for WeasyPrint (see [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for your OS).
  - **Ubuntu/Debian**: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`
  - **macOS**: `brew install pango`

## Setup Instructions

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd woocommerce_pdf
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy the example environment file and edit it:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to match your store details, font path, and API credentials:
   ```env
   FONT_PATH=./fonts/Vazirmatn-Regular.ttf
   STORE_NAME=نام فروشگاه شما
   STORE_PHONE=۰۲۱-۱۲۳۴۵۶۷۸
   STORE_ADDRESS=تهران، خیابان ولیعصر، کوچه نمونه، پلاک ۱
   SITE_URL=https://yoursite.com

   # For Bulk Backup (WooCommerce API)
   WC_URL=https://yoursite.com
   WC_KEY=ck_your_consumer_key
   WC_SECRET=cs_your_consumer_secret
   ```

5. **Add your Font:**
   Create a `fonts` directory and place your `.ttf` font file there.

## Usage

### 1. Manual Test
Run the script by passing a sample WooCommerce order JSON:
```bash
python main.py
```

### 2. Webhook Listener (Auto-fetch)
Start the Flask server to listen for WooCommerce webhooks:
```bash
python webhook.py
```
*Configure this in WooCommerce > Settings > Advanced > Webhooks. Set the Delivery URL to `http://your-server-ip:5000/webhook/order-created`.*

### 3. Bulk Backup (Invoices Only)
Fetch all orders from your site, generate invoices (no packing slips), and zip them into a single file:
```bash
python backup.py
```
*This script uses pagination and a 2-second delay between requests to avoid overloading your server.*
