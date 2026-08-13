import json
import sys
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from detection.engine import DetectionEngine


GROUND_TRUTH_FILE = (
    PROJECT_ROOT / "evaluation" / "ground_truth.json"
)

REPORT_FILE = (
    PROJECT_ROOT / "evaluation" / "evaluation_report.json"
)


def load_ground_truth() -> Dict:
    """Load the manually labelled evaluation dataset."""

    with GROUND_TRUTH_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize(value: str) -> str:
    """Normalize text for comparison."""

    return " ".join(value.lower().split())


def contains_expected_pii(
    text: str,
    expected_type: str,
    detector: DetectionEngine,
) -> bool:
    """
    Check whether the detector identifies the expected
    PII type in the supplied text.
    """

    detections = detector.detect(text)

    normalized_text = normalize(text)

    for detection in detections:
        if (
            detection.entity_type == expected_type
            and normalize(detection.value) in normalized_text
        ):
            return True

    return False


def evaluate_positive_examples(
    examples: List[Dict[str, str]],
    detector: DetectionEngine,
) -> tuple[int, int]:
    """Evaluate examples that should contain PII."""

    true_positive = 0
    false_negative = 0

    for example in examples:
        detected = contains_expected_pii(
            example["text"],
            example["type"],
            detector,
        )

        if detected:
            true_positive += 1
        else:
            false_negative += 1

    return true_positive, false_negative


def evaluate_negative_examples(
    examples: List[Dict[str, str]],
    detector: DetectionEngine,
) -> tuple[int, int]:
    """Evaluate examples that should not contain target PII."""

    true_negative = 0
    false_positive = 0

    for example in examples:
        detections = detector.detect(example["text"])

        if detections:
            false_positive += 1
        else:
            true_negative += 1

    return true_negative, false_positive


def calculate_metrics(
    true_positive: int,
    false_positive: int,
    false_negative: int,
    true_negative: int,
) -> Dict[str, float]:

    precision = (
        true_positive
        / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    accuracy = (
        (true_positive + true_negative)
        / (
            true_positive
            + true_negative
            + false_positive
            + false_negative
        )
        if (
            true_positive
            + true_negative
            + false_positive
            + false_negative
        )
        else 0.0
    )

    return {
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "accuracy": accuracy,
    }


def main() -> None:
    """Run the evaluation."""

    data = load_ground_truth()

    positive_examples = data["positive_examples"]
    negative_examples = data["negative_examples"]

    detector = DetectionEngine()

    print("Evaluating positive examples...")

    true_positive, false_negative = evaluate_positive_examples(
        positive_examples,
        detector,
    )

    print("Evaluating negative examples...")

    true_negative, false_positive = evaluate_negative_examples(
        negative_examples,
        detector,
    )

    metrics = calculate_metrics(
        true_positive=true_positive,
        true_negative=true_negative,
        false_positive=false_positive,
        false_negative=false_negative,
    )

    report = {
        "evaluation_type": "Representative labelled test set",
        "positive_examples": len(positive_examples),
        "negative_examples": len(negative_examples),
        "total_examples": (
            len(positive_examples)
            + len(negative_examples)
        ),
        "metrics": metrics,
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    print()
    print("=" * 50)
    print("PII REDACTION EVALUATION")
    print("=" * 50)

    print(
        f"Positive examples : {len(positive_examples)}"
    )

    print(
        f"Negative examples : {len(negative_examples)}"
    )

    print()

    print(
        f"True positives    : {true_positive}"
    )

    print(
        f"True negatives    : {true_negative}"
    )

    print(
        f"False positives   : {false_positive}"
    )

    print(
        f"False negatives   : {false_negative}"
    )

    print()

    print(
        f"Accuracy          : {metrics['accuracy']:.4f}"
    )

    print(
        f"Precision         : {metrics['precision']:.4f}"
    )

    print(
        f"Recall            : {metrics['recall']:.4f}"
    )

    print(
        f"F1 Score          : {metrics['f1_score']:.4f}"
    )

    print()

    print(
        f"Report saved to   : {REPORT_FILE}"
    )

    print("=" * 50)


if __name__ == "__main__":
    main()