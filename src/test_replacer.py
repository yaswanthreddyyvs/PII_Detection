from detection.engine import DetectionEngine
from replacement.replacer import PIIReplacer


def main() -> None:
    text = """
    Rajesh Kushal Hegde can be contacted at
    rajesh@example.com.

    Rajesh Kushal Hegde can also be contacted at
    rajesh@example.com.
    """

    detector = DetectionEngine()
    replacer = PIIReplacer()

    detections = detector.detect(text)

    for detection in detections:
        replacement = replacer.replace(detection)

        print(
            f"{detection.entity_type}: "
            f"{detection.value} -> {replacement}"
        )


if __name__ == "__main__":
    main()