# RAG System Evaluation Report

**Overall Accuracy:** 84.0%

## Performance By State
* **CONSENSUS**: 60.0% (out of 5)
* **UNANSWERABLE**: 94.1% (out of 17)
* **CONTRADICTION**: 66.7% (out of 3)

## Confusion Matrix
| Expected \ Predicted | CONSENSUS | UNANSWERABLE | CONTRADICTION |
|---|---|---|---|
| CONSENSUS | 3 | 1 | 1 |
| UNANSWERABLE | 0 | 16 | 1 |
| CONTRADICTION | 1 | 0 | 2 |

## Failed Tests Log
**Query:** What is the penalty if I pay my hostel fee on September 5th?
- **Expected:** `CONSENSUS`
- **Predicted:** `CONTRADICTION`
- **System Reasoning:** Passage 0 states a fixed late penalty for Hostel/Dorm fees ($100 after Sept 1st), while Passage 3 (Clause 4.2) states that the Appeals Committee has supreme discretionary authority to waive any financial late penalties if extenuating circumstances exist, creating a conflict regarding whether the penalty is strictly enforced or waivable.

**Query:** Can the Student Union President keep their job if their GPA drops to 1.8?
- **Expected:** `CONTRADICTION`
- **Predicted:** `CONSENSUS`
- **System Reasoning:** Passage 0 explicitly states that the Student Union President maintains their executive status and office regardless of academic standing, even if their GPA falls below 2.0 and results in probation.

**Query:** Can the Appeals Committee waive the rule about library fines preventing class registration?
- **Expected:** `CONSENSUS`
- **Predicted:** `UNANSWERABLE`
- **System Reasoning:** The text states that library fines prevent registration (Clause 5.3) and that the Appeals Committee can waive academic requirements including financial late penalties (Clause 4.2), but it does not explicitly state whether the Appeals Committee can waive the specific rule regarding library fines preventing class registration.

**Query:** Is there a grace period for the tuition fee before the late penalty applies?
- **Expected:** `UNANSWERABLE`
- **Predicted:** `CONTRADICTION`
- **System Reasoning:** Passage 0 states that no committee has the authority to waive late tuition penalties, whereas Passage 2 states that the Appeals Committee has supreme discretionary authority to waive any financial late penalties.

