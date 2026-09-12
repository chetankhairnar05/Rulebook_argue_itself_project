# RAG System Evaluation Report

**Overall Accuracy:** 86.7%

## Performance By State
* **CONSENSUS**: 83.3% (out of 6)
* **UNANSWERABLE**: 85.7% (out of 7)
* **CONTRADICTION**: 100.0% (out of 2)

## Confusion Matrix
| Expected \ Predicted | CONSENSUS | UNANSWERABLE | CONTRADICTION |
|---|---|---|---|
| CONSENSUS | 5 | 1 | 0 |
| UNANSWERABLE | 0 | 6 | 1 |
| CONTRADICTION | 0 | 0 | 2 |

## Failed Tests Log
**Query:** Can the Appeals Committee waive the rule about library fines preventing class registration?
- **Expected:** `CONSENSUS`
- **Predicted:** `UNANSWERABLE`
- **System Reasoning:** The text states that library fines prevent registration (Clause 5.3) and that the Appeals Committee can waive academic requirements including financial late penalties (Clause 4.2), but it does not explicitly mention whether library fines can be waived by the Appeals Committee.

**Query:** Is there a grace period for the tuition fee before the late penalty applies?
- **Expected:** `UNANSWERABLE`
- **Predicted:** `CONTRADICTION`
- **System Reasoning:** Passage 0 states that no university committee has the authority to waive late tuition penalties, while Passage 2 states that the Appeals Committee has supreme discretionary authority to waive any financial late penalties.

