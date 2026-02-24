# WooCommerce PDF Generator (Production Ready)

A Python script to generate PDF invoices and packing slips from WooCommerce order JSON. It focuses on minimizing paper usage by intelligently placing the packing slip on the same page as the invoice if there is enough space.

## Features
- Generates A4 PDF invoices and packing slips.
- Right-to-Left (RTL) Persian typography.
- Smart layout: Calculates invoice height and places the packing slip on the same page if it takes less than 70% of the A4 height.
- Embeds custom Persian fonts.
- Minimalist, print-friendly, black-and-white design.

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
   *(Note: The `requirements.txt` uses `WeasyPrint>=63.0` to avoid the `pydyf` transform error.)*

4. **Configure Environment Variables:**
   Copy the example environment file and edit it:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to match your store details and font path:
   ```env
   FONT_PATH=./fonts/Vazirmatn-Regular.ttf
   STORE_NAME=نام فروشگاه شما
   STORE_PHONE=۰۲۱-۱۲۳۴۵۶۷۸
   STORE_ADDRESS=تهران، خیابان ولیعصر، کوچه نمونه، پلاک ۱
   ```

5. **Add your Font:**
   Create a `fonts` directory and place your `.ttf` font file there (e.g., `Vazirmatn-Regular.ttf`).
   ```bash
   mkdir fonts
   # Copy your font into the fonts directory
   ```

## Usage

Run the script by passing a sample WooCommerce order JSON. A sample `sample_order.json` is provided.

```bash
python main.py
```

The generated PDF will be saved in the `output/YYYY/MM/` directory based on the Jalali date of the order.

## Troubleshooting

- **`AttributeError: 'super' object has no attribute 'transform'`**: This is caused by an incompatibility between WeasyPrint 62.1 and newer versions of `pydyf`. It is fixed by upgrading to `WeasyPrint>=63.0`. Run `pip install -U -r requirements.txt` to fix this.
- **Missing fonts or squares instead of text**: Ensure the `FONT_PATH` in your `.env` file is correct and points to a valid `.ttf` file.
