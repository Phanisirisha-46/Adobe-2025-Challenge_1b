
## 📄 Persona-Driven Document Intelligence

**Adobe Hackathon 2025 — Round 1B**
*“Connect What Matters — For the User Who Matters”*

---

### 🧠 Challenge Summary

Build an intelligent system that reads a collection of PDF documents and extracts the most relevant sections and subsections based on:

* A **persona** (e.g., student, researcher, analyst)
* A **job to be done** (e.g., literature review, exam preparation, financial summary)

The solution must generalize across domains and work offline, with strict resource limits.

---

### 📁 Folder Structure

```
.
├── Collection 1/
│   ├── challenge1b_input.json
│   └── PDFs/
│       ├── file01.pdf
│       └── file02.pdf
├── Collection 2/
│   └── ...
├── output/
│   ├── Collection 1_file01.json
│   └── Collection 1_file02.json
├── main.py
├── requirements.txt
├── Dockerfile
├── README.md
```

---

### 🚀 How to Build & Run

> Your solution will be evaluated via a Docker container run on CPU with no internet access.

#### 🧱 Build Docker Image

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

#### ▶️ Run the Solution

```bash
docker run --rm \
  -v $(pwd):/app \
  --network none \
  mysolutionname:somerandomidentifier
```

> ✅ All output `.json` files will be saved to the `./output/` folder.

---

### 📥 Input Format

Each `Collection N/` folder contains:

* `challenge1b_input.json` with:

  ```json
  {
    "persona": { "role": "PhD Researcher in Computational Biology" },
    "job_to_be_done": { "task": "Prepare a comprehensive literature review..." },
    "documents": [
      { "filename": "file01.pdf" },
      { "filename": "file02.pdf" }
    ]
  }
  ```
* A `PDFs/` folder with matching `.pdf` files

---

### 📤 Output Format

Each `.pdf` will produce one `.json` named:

```
Collection 1_file01.json
```

Each output contains:

* `metadata`: input info, timestamp
* `extracted_sections`: title + importance\_rank + page
* `subsection_analysis`: refined key lines from each section

---

### ✅ Constraints Met

* ✅ Model size < **1GB**
* ✅ CPU-only
* ✅ Processing time < **60s** for 3–5 PDFs
* ✅ No internet access during runtime
* ✅ Output in specified JSON format

---

### 📦 Dependencies

```txt
pymupdf==1.23.7
sentence-transformers==2.2.2
torch==2.0.1
```

---

