from damage_quantification import quantify_damage

# Type Weight assigned per damage type (0-100 scale)
# Based on real-world road safety hazard level
TYPE_WEIGHTS = {
    "Pothole": 100,
    "AlligatorCrack": 80,
    "LongitudinalCrack": 55,
    "TransverseCrack": 40
}


def calculate_wsi(damage_type, confidence, area_pct):
    """
    Calculates the Weighted Severity Index (WSI) for a single detection.

    WSI = (Type Weight x 0.40) + (Confidence x 0.35) + (Area% x 0.25)

    Confidence is scaled 0-1 -> 0-100 to match the other inputs.
    Area% is capped at 100 since it's already a percentage.
    """
    type_weight = TYPE_WEIGHTS.get(damage_type, 50)  # default 50 if unknown type
    confidence_scaled = confidence * 100
    area_scaled = min(area_pct, 100)

    wsi = (type_weight * 0.40) + (confidence_scaled * 0.35) + (area_scaled * 0.25)
    return round(wsi, 2)


def get_severity_label(wsi_score):
    """
    Maps a WSI score (0-100) to a severity label and recommended action.
    """
    if wsi_score >= 75:
        return "CRITICAL", "Repair within 48 hours"
    elif wsi_score >= 50:
        return "HIGH", "Repair within 2 weeks"
    elif wsi_score >= 25:
        return "MEDIUM", "Schedule for next month"
    else:
        return "LOW", "Monitor only, no immediate action needed"


def analyze_image_severity(image_path, conf_threshold=0.10):
    """
    Runs detection + quantification, then calculates WSI for each
    detection and an overall image-level WSI (based on worst detection).
    """
    output = quantify_damage(image_path, conf_threshold)

    scored_detections = []
    for d in output["detections"]:
        wsi = calculate_wsi(d["type"], d["confidence"], d["area_pct"])
        label, action = get_severity_label(wsi)
        scored_detections.append({
            **d,
            "wsi": wsi,
            "severity": label,
            "action": action
        })

    # Overall image severity = highest WSI among all detections
    if scored_detections:
        worst = max(scored_detections, key=lambda x: x["wsi"])
        overall_wsi = worst["wsi"]
        overall_label, overall_action = get_severity_label(overall_wsi)
    else:
        overall_wsi = 0.0
        overall_label, overall_action = get_severity_label(0.0)

    return {
        "image": image_path,
        "detections": scored_detections,
        "overall_wsi": overall_wsi,
        "overall_severity": overall_label,
        "overall_action": overall_action
    }


if __name__ == "__main__":
    result = analyze_image_severity("images/test1.png")

    print(f"\nImage: {result['image']}\n")
    print("Per-detection scores:")
    for d in result["detections"]:
        print(f"  → {d['type']:<20} WSI: {d['wsi']:<6} {d['severity']:<8} ({d['action']})")

    print(f"\nOVERALL SEVERITY: {result['overall_severity']}")
    print(f"OVERALL WSI SCORE: {result['overall_wsi']}/100")
    print(f"RECOMMENDED ACTION: {result['overall_action']}")