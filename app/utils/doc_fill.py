from docxtpl import DocxTemplate, InlineImage, RichText
from docx.shared import Mm
import base64
from io import BytesIO
from PIL import Image
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_docs')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fill_template(template_name: str, context: dict, output_filename: str) -> str:
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
        context["signature"] = InlineImage(doc, buffer, width=Mm(50))  # Adjust width as needed
    elif isinstance(signature, str) and signature.strip():
        rt = RichText()
        rt.add(signature, color="0000FF", font="Segoe Script")  # Blue cursive
        context["signature"] = rt
    else:
        context["signature"] = ""  # ✅ Prevent template crash if signature is empty

    doc.render(context)

    output_path = os.path.abspath(os.path.join(OUTPUT_DIR, output_filename))
    doc.save(output_path)

    return output_path



