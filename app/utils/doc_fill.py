from docxtpl import DocxTemplate
import os
import uuid

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_docs')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fill_template(template_name: str, context: dict, output_filename: str) -> str:
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError("Template not found.")

    doc = DocxTemplate(template_path)
    doc.render(context)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    doc.save(output_path)

    return output_path

