import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAQS_PATH = os.path.join(BASE_DIR, 'faqs.json')
PROGRAM_FAQS_PATH = os.path.join(BASE_DIR, 'program_faqs.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'ground_truth.json')

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"File not found: {filepath}")
    return {}

def main():
    faqs_data = load_json(FAQS_PATH)
    program_faqs_data = load_json(PROGRAM_FAQS_PATH)
    
    ground_truth = []
    
    # Process faqs.json
    if isinstance(faqs_data, dict):
        for category, limit in [("Admissions", 5), ("Examinations", 5), ("General", 5)]:
            if category in faqs_data:
                for item in faqs_data[category][:limit]:
                    ground_truth.append({
                        "query": item.get("question", ""),
                        "expected_answer": item.get("answer", "")
                    })
    elif isinstance(faqs_data, list):
        for item in faqs_data[:15]:
            ground_truth.append({
                "query": item.get("question", ""),
                "expected_answer": item.get("answer", "")
            })
                
    # Process program_faqs.json
    if isinstance(program_faqs_data, dict):
        for category in ["Admissions", "Examinations", "General", "Assignments", "MBA & MCA (Special Instructions)"]:
            if category in program_faqs_data:
                for item in program_faqs_data[category][:5]:
                    ground_truth.append({
                        "query": item.get("question", ""),
                        "expected_answer": item.get("answer", "")
                    })
    elif isinstance(program_faqs_data, list):
        for item in program_faqs_data[:15]:
            ground_truth.append({
                "query": item.get("question", ""),
                "expected_answer": item.get("answer", "")
            })

    # Ensure no duplicates
    seen = set()
    unique_ground_truth = []
    for item in ground_truth:
        if item["query"] and item["query"] not in seen:
            seen.add(item["query"])
            unique_ground_truth.append(item)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(unique_ground_truth, f, indent=4)
        
    print(f"Generated {len(unique_ground_truth)} synthetic ground truth Q&A pairs at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
