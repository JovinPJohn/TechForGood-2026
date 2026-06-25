import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wsi_calculator import analyze_image_severity

def build_priority_queue(image_location_pairs):
    """
    Takes a list of (image_path, location_name) pairs,
    runs WSI analysis on each, and returns a ranked repair queue.
    """
    results = []

    for image_path, location in image_location_pairs:
        print(f"Analyzing: {location}...")
        result = analyze_image_severity(image_path)
        results.append({
            "location": location,
            "image": image_path,
            "wsi": result["overall_wsi"],
            "severity": result["overall_severity"],
            "action": result["overall_action"],
            "detections": result["detections"]
        })

    # Sort by WSI score, highest first
    results.sort(key=lambda x: x["wsi"], reverse=True)

    return results


def print_priority_queue(queue):
    print("\n" + "="*65)
    print("ROAD DAMAGE PRIORITY REPAIR QUEUE")
    print("="*65)
    print(f"{'Rank':<6}{'Location':<25}{'WSI':<8}{'Severity':<12}Action")
    print("-"*65)

    for i, item in enumerate(queue, 1):
        print(f"{i:<6}{item['location']:<25}{item['wsi']:<8}{item['severity']:<12}{item['action']}")

    print("="*65)
    print(f"\nTotal locations assessed: {len(queue)}")
    critical = sum(1 for r in queue if r["severity"] == "CRITICAL")
    high = sum(1 for r in queue if r["severity"] == "HIGH")
    medium = sum(1 for r in queue if r["severity"] == "MEDIUM")
    low = sum(1 for r in queue if r["severity"] == "LOW")
    print(f"CRITICAL: {critical} | HIGH: {high} | MEDIUM: {medium} | LOW: {low}")


if __name__ == "__main__":
    # Test with our two available images
    image_location_pairs = [
        ("images/test1.png", "MG Road Bangalore"),
        ("images/test2.png", "Anna Nagar Chennai"),
    ]

    queue = build_priority_queue(image_location_pairs)
    print_priority_queue(queue)