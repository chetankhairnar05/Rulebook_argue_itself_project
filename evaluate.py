import json
import time
import os
from collections import defaultdict
from core_engine import ingest_rulebook, query_rulebook

# Evaluation config
EVAL_FILE = "eval_set.json"
RULEBOOK_FILE = "data/rulebook.md"
REPORT_FILE = "eval_report.md"

def print_header(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def run_evaluation():
    # 1. Setup: Ensure database is ready
    print_header("System Setup")
    if not os.path.exists(RULEBOOK_FILE):
        print(f"❌ Error: {RULEBOOK_FILE} not found.")
        return
        
    print(f"Ingesting {RULEBOOK_FILE} into ChromaDB...")
    ingest_rulebook(RULEBOOK_FILE)
    
    # 2. Load Evaluation Set
    if not os.path.exists(EVAL_FILE):
        print(f"❌ Error: {EVAL_FILE} not found.")
        return
        
    with open(EVAL_FILE, "r") as f:
        test_cases = json.load(f)
        
    print(f"Loaded {len(test_cases)} test cases.")
    
    # 3. Metrics Tracking
    results = []
    correct_count = 0
    
    # Confusion matrix tracker: state_matrix[expected][predicted]
    states = ["CONSENSUS", "UNANSWERABLE", "CONTRADICTION"]
    matrix = {expected: {predicted: 0 for predicted in states} for expected in states}
    
    # 4. Run the Tests
    print_header("Running Tests")
    start_time = time.time()
    
    for i, tc in enumerate(test_cases):
        query = tc["query"]
        expected = tc["expected_state"].upper()
        
        print(f"[{i+1}/{len(test_cases)}] Query: {query[:50]}...")
        
        # Hit the RAG engine
        response = query_rulebook(query)
        predicted = response["state"].upper()
        
        # Track metrics
        is_correct = (expected == predicted)
        if is_correct:
            correct_count += 1
            
        # Safely increment the matrix (in case LLM outputs something weird)
        if expected in matrix and predicted in matrix[expected]:
            matrix[expected][predicted] += 1
            
        results.append({
            "query": query,
            "expected": expected,
            "predicted": predicted,
            "match": is_correct,
            "reasoning_used": response.get("message", "").replace("\n", " ")
        })
        
        # Slight delay to respect free-tier rate limits
        time.sleep(2) 
        
    execution_time = time.time() - start_time
    
    # 5. Calculate Metrics
    accuracy = (correct_count / len(test_cases)) * 100
    
    # Calculate recall per state
    recall_stats = {}
    for state in states:
        total_expected = sum(matrix[state].values())
        correct_predicted = matrix[state][state]
        recall = (correct_predicted / total_expected * 100) if total_expected > 0 else 0
        recall_stats[state] = {"total": total_expected, "recall": recall}
    
    # 6. Terminal Output
    print_header("Evaluation Results")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"Overall Accuracy: {correct_count}/{len(test_cases)} ({accuracy:.1f}%)\n")
    
    print("--- Accuracy By State (Recall) ---")
    for state in states:
        stats = recall_stats[state]
        print(f"{state.ljust(15)}: {stats['recall']:>5.1f}% (N={stats['total']})")
        
    print("\n--- Confusion Matrix [Expected \\ Predicted] ---")
    header = f"{'':<15} | " + " | ".join([s.ljust(13) for s in states])
    print(header)
    print("-" * len(header))
    for expected in states:
        row_str = f"{expected:<15} | "
        for predicted in states:
            row_str += f"{str(matrix[expected][predicted]).ljust(13)} | "
        print(row_str)

    # 7. Generate Markdown Report
    generate_markdown_report(results, accuracy, recall_stats, matrix, states)

def generate_markdown_report(results, accuracy, recall_stats, matrix, states):
    with open(REPORT_FILE, "w") as f:
        f.write("# RAG System Evaluation Report\n\n")
        f.write(f"**Overall Accuracy:** {accuracy:.1f}%\n\n")
        
        f.write("## Performance By State\n")
        for state, stats in recall_stats.items():
            f.write(f"* **{state}**: {stats['recall']:.1f}% (out of {stats['total']})\n")
            
        f.write("\n## Confusion Matrix\n")
        f.write("| Expected \\ Predicted | " + " | ".join(states) + " |\n")
        f.write("|" + "|".join(["---" for _ in range(len(states) + 1)]) + "|\n")
        for expected in states:
            row = [expected] + [str(matrix[expected][pred]) for pred in states]
            f.write("| " + " | ".join(row) + " |\n")
            
        f.write("\n## Failed Tests Log\n")
        failed = [r for r in results if not r["match"]]
        if not failed:
            f.write("All tests passed!\n")
        else:
            for r in failed:
                f.write(f"**Query:** {r['query']}\n")
                f.write(f"- **Expected:** `{r['expected']}`\n")
                f.write(f"- **Predicted:** `{r['predicted']}`\n")
                f.write(f"- **System Reasoning:** {r['reasoning_used']}\n\n")
                
    print(f"\n✅ Full report written to {REPORT_FILE}")

if __name__ == "__main__":
    run_evaluation()