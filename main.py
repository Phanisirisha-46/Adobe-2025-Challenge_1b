import json
from pathlib import Path
import fitz  # PyMuPDF
from collections import Counter
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

INPUT_ROOT = Path(".")
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_structured_content(pdf_path):
    doc = fitz.open(pdf_path)
    content = []
    for page_number, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    spans = line.get("spans", [])
                    text = " ".join(span["text"] for span in spans).strip()
                    if text:
                        font_size = round(max(span["size"] for span in spans), 1)
                        content.append({
                            "text": text,
                            "font_size": font_size,
                            "page": page_number
                        })
    return content

def tag_headings(content):
    sizes = [item["font_size"] for item in content]
    size_counts = Counter(sizes)
    font_order = [size for size, _ in sorted(size_counts.items(), key=lambda x: (-x[1], -x[0]))]
    size_to_level = {size: f"H{idx+1}" for idx, size in enumerate(font_order)}
    for item in content:
        item["level"] = size_to_level[item["font_size"]]
    return content

def group_sections(content):
    sections = []
    current = None
    for item in content:
        if item["level"] in ["H1", "H2"]:
            if current:
                sections.append(current)
            current = {
                "title": item["text"],
                "page": item["page"],
                "content": []
            }
        elif current:
            current["content"].append(item["text"])
    if current:
        sections.append(current)
    return sections

def get_ranked_sections(sections, query_embedding, top_k=5):
    ranked = []
    for section in sections:
        full_text = section["title"] + " " + " ".join(section["content"][:5])
        embedding = model.encode(full_text, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, embedding).item()
        ranked.append((score, section))
    ranked.sort(reverse=True, key=lambda x: x[0])
    return [item[1] for item in ranked[:top_k]]

# Process all "Collection N/" folders
for collection_dir in INPUT_ROOT.glob("Collection */"):
    if not collection_dir.is_dir():
        continue

    collection_name = collection_dir.name
    input_json_path = collection_dir / "challenge1b_input.json"
    pdfs_dir = collection_dir / "PDFs"

    if not input_json_path.exists() or not pdfs_dir.exists():
        continue

    with open(input_json_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    persona = input_data["persona"]["role"]
    task = input_data["job_to_be_done"]["task"]
    query = f"{persona}: {task}"
    query_embedding = model.encode(query, convert_to_tensor=True)

    for pdf_path in pdfs_dir.glob("*.pdf"):
        print(f"📄 Processing {pdf_path.name} from {collection_name}")

        content = extract_structured_content(pdf_path)
        tagged = tag_headings(content)
        sections = group_sections(tagged)
        top_sections = get_ranked_sections(sections, query_embedding)

        output = {
            "metadata": {
                "document": pdf_path.name,
                "collection": collection_name,
                "persona": persona,
                "job_to_be_done": task,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }

        for idx, section in enumerate(top_sections):
            output["extracted_sections"].append({
                "document": pdf_path.name,
                "section_title": section["title"],
                "importance_rank": idx + 1,
                "page_number": section["page"] + 1
            })
            output["subsection_analysis"].append({
                "document": pdf_path.name,
                "refined_text": section["title"] + " " + " ".join(section["content"][:7]),
                "page_number": section["page"] + 1
            })

        output_path = OUTPUT_DIR / f"{collection_name}_{pdf_path.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ Saved to: {output_path}")
