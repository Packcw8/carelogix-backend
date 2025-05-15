import os
import subprocess
from datetime import datetime
from uuid import uuid4
from docxtpl import DocxTemplate

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_docs")

def fill_template(template_name: str, context: dict) -> tuple[str, str]:
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(template_path)

    # Fill the template with the provided context
    doc.render(context)

    # Create a unique filename
    filename_prefix = f"{context.get('case_name', 'note')}_{datetime.now().strftime('%b_%d__%Y')}".lower().replace(" ", "_")
    output_filename = f"{filename_prefix}.docx"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Save the .docx
    doc.save(output_path)

    # Try to convert to PDF using LibreOffice (optional)
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
    except FileNotFoundError:
        print("⚠️ LibreOffice not found — skipping PDF conversion.")
    except subprocess.CalledProcessError:
        print("⚠️ LibreOffice failed to convert to PDF.")

    return output_path, pdf_path
