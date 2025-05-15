import os
import subprocess
from datetime import datetime
from docxtpl import DocxTemplate

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_docs")

def fill_template(template_name: str, context: dict, output_filename: str = None) -> tuple[str, str]:
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(template_path)
    doc.render(context)

    # 🧠 Use service_date in filename if provided
    if not output_filename:
        service_date = context.get("service_date")
        try:
            date_obj = datetime.strptime(service_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%b_%d__%Y")
        except Exception:
            formatted_date = datetime.now().strftime("%b_%d__%Y")

        filename_prefix = f"{context.get('case_name', 'note')}_{formatted_date}".lower().replace(" ", "_")
        output_filename = f"{filename_prefix}.docx"

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    doc.save(output_path)

    # Try to convert to PDF using LibreOffice
    pdf_path = ""
    try:
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", OUTPUT_DIR,
            output_path
        ], check=True)
        pdf_path = os.path.abspath(os.path.join(OUTPUT_DIR, output_filename.replace(".docx", ".pdf")))
    except Exception:
        pass  # Silently skip if LibreOffice not available or fails

    return output_path, pdf_path
