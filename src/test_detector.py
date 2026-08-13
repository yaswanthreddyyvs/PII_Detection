from detection.engine import DetectionEngine


def main() -> None:
    text = """
    Rashi Patil works at ABC Technologies.
    Email: rashi.patil@gmail.com
    Phone: +91 9876543210
    DOB: 15/08/1998
    IP: 192.168.1.10
    SSN: 123-45-6789
    """

    engine = DetectionEngine()

    detections = engine.detect(text)

    for detection in detections:
        print(
            f"{detection.entity_type:<20} "
            f"{detection.value:<30} "
            f"score={detection.score:.2f}"
        )


if __name__ == "__main__":
    main()