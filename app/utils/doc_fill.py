from docxtpl import DocxTemplate, InlineImage, RichText
from docx.shared import Mm
import base64
from io import BytesIO
from PIL import Image
import os
import subprocess  # ✅ For LibreOffice conversion

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_docs')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fill_template(template_name: str, context: dict, output_filename: str) -> tuple[str, str]:
    template_path = os.path.abspath(os.path.join(TEMPLATE_DIR, template_name))
    print("🧩 Looking for template at:", template_path)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(template_path)

    signature = context.get("signature", "")
    if signature.startswith("data:image"):
        image_data = signature.split(",")[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        context["signature"] = InlineImage(doc, buffer, width=Mm(50))
    elif isinstance(signature, str) and signature.strip():
        rt = RichText()
        rt.add(signature, color="0000FF", font="Segoe Script")
        context["signature"] = rt
    else:
        context["signature"] = ""

    doc.render(context)

    # Save DOCX
    output_path = os.path.abspath(os.path.join(OUTPUT_DIR, output_filename))
    doc.save(output_path)

    # ✅ Convert to PDF using LibreOffice
    pdf_filename = output_filename.replace(".docx", ".pdf")
    pdf_path = os.path.abspath(os.path.join(OUTPUT_DIR, pdf_filename))

    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", OUTPUT_DIR,
        output_path
    ], check=True)

    return output_path, pdf_path
