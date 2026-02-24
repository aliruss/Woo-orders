import os
import json
from datetime import datetime
import jdatetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FONT_PATH = os.getenv('FONT_PATH', '')
STORE_NAME = os.getenv('STORE_NAME', 'نام فروشگاه')
STORE_PHONE = os.getenv('STORE_PHONE', 'تلفن فروشگاه')
STORE_ADDRESS = os.getenv('STORE_ADDRESS', 'آدرس فروشگاه')

# A4 dimensions in mm
A4_HEIGHT_MM = 297
A4_WIDTH_MM = 210

def parse_order_date(date_str):
    """Convert WooCommerce date string to Jalali date."""
    try:
        # WooCommerce date format: 2023-10-25T14:30:00
        dt = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
        jalali_date = jdatetime.date.fromgregorian(date=dt)
        return jalali_date
    except Exception:
        return jdatetime.date.today()

def format_currency(value):
    """Format numbers with commas."""
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return value

def render_template(template_name, context):
    """Render a Jinja2 template with the given context."""
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['currency'] = format_currency
    template = env.get_template(template_name)
    return template.render(context)

def calculate_html_height(html_content, base_url='.'):
    """
    Calculate the height of the rendered HTML content in mm.
    WeasyPrint renders to pages. We can check the height of the main box.
    """
    doc = HTML(string=html_content, base_url=base_url).render()
    
    # If it creates more than 1 page, it's definitely > 70% of A4.
    if len(doc.pages) > 1:
        return A4_HEIGHT_MM
    
    # Get the height of the content on the first page
    # WeasyPrint page size is in pixels (at 96 dpi). 1 mm = 3.7795 px
    px_to_mm = 25.4 / 96.0
    
    max_bottom = 0
    for page in doc.pages:
        def traverse(box):
            nonlocal max_bottom
            if hasattr(box, 'position_y') and hasattr(box, 'height'):
                bottom = box.position_y + box.height
                if bottom > max_bottom:
                    max_bottom = bottom
            if hasattr(box, 'children'):
                for child in box.children:
                    traverse(child)
        traverse(page._page_box)
        
    height_mm = max_bottom * px_to_mm
    return height_mm

def generate_pdf(order_json_path):
    """Generate the final PDF from order JSON."""
    with open(order_json_path, 'r', encoding='utf-8') as f:
        order = json.load(f)
        
    # Prepare data
    jalali_date = parse_order_date(order.get('date_created', ''))
    order['jalali_date'] = jalali_date.strftime('%Y/%m/%d')
    
    total_items = sum(item.get('quantity', 0) for item in order.get('line_items', []))
    
    store_info = {
        'name': STORE_NAME,
        'phone': STORE_PHONE,
        'address': STORE_ADDRESS
    }
    
    # Render CSS
    css_context = {'font_path': os.path.abspath(FONT_PATH) if FONT_PATH else ''}
    css_content = render_template('style.css', css_context)
    
    # 1. Render Invoice only to calculate height
    invoice_context = {
        'order': order,
        'store': store_info
    }
    invoice_html = render_template('invoice.html', invoice_context)
    
    # Wrap in basic HTML structure with CSS for height calculation
    full_invoice_html = f"<html><head><style>{css_content}</style></head><body>{invoice_html}</body></html>"
    
    invoice_height_mm = calculate_html_height(full_invoice_html, base_url=os.path.abspath('.'))
    
    # 2. Decide Layout
    # 65% of A4 height (297mm) is approx 193mm. Adjusted to prevent unnecessary page breaks.
    force_page_break = invoice_height_mm > (A4_HEIGHT_MM * 0.65)
    
    # 3. Render Packing Slip
    packing_context = {
        'order': order,
        'store': store_info,
        'total_items': total_items,
        'force_page_break': force_page_break
    }
    packing_html = render_template('packing_slip.html', packing_context)
    
    # 4. Combine HTML
    final_html = f"<html><head><style>{css_content}</style></head><body>{invoice_html}{packing_html}</body></html>"
    
    # 5. Determine Output Path
    year = jalali_date.strftime('%Y')
    month = jalali_date.strftime('%m')
    day = jalali_date.strftime('%d')
    order_id = order.get('id', 'UNKNOWN')
    
    output_dir = os.path.join('output', year, month)
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{year}-{month}-{day}_{order_id}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # 6. Generate Final PDF
    HTML(string=final_html, base_url=os.path.abspath('.')).write_pdf(output_path)
    print(f"PDF generated successfully: {output_path}")
    return output_path

if __name__ == '__main__':
    # Example usage
    generate_pdf('sample_order.json')
