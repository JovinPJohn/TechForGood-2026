from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO("model/rdd_india_best.pt")

# Class names mapped to readable labels
class_names = {
    0: "LongitudinalCrack",
    1: "TransverseCrack",
    2: "AlligatorCrack",
    3: "Pothole"
}

def quantify_damage(image_path, conf_threshold=0.10):
    """
    Runs detection on an image and calculates damage area percentage.
    """
    # Run inference
    results = model(image_path, conf=conf_threshold)[0]

    # Get image dimensions
    img = cv2.imread(image_path)
    img_h, img_w = img.shape[:2]
    total_pixels = img_h * img_w

    detections = []
    total_damage_pixels = 0

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        box_area = (x2 - x1) * (y2 - y1)
        total_damage_pixels += box_area

        detections.append({
            "type": class_names[cls_id],
            "confidence": round(conf, 3),
            "area_px": round(box_area, 1),
            "area_pct": round((box_area / total_pixels) * 100, 2)
        })

    total_damage_pct = round((total_damage_pixels / total_pixels) * 100, 2)

    return {
        "image": image_path,
        "image_size": f"{img_w}x{img_h}",
        "total_pixels": total_pixels,
        "detections": detections,
        "total_damage_pct": total_damage_pct,
        "results_object": results  # keep for visualization later
    }


if __name__ == "__main__":
    test_image = "images/test1.png"
    output = quantify_damage(test_image)

    print(f"\nImage: {output['image']}")
    print(f"Size: {output['image_size']} ({output['total_pixels']} total pixels)")
    print(f"Detections found: {len(output['detections'])}\n")

    for d in output['detections']:
        print(f"  → {d['type']:<20} conf: {d['confidence']:.2f}  area: {d['area_pct']}% of image")

    print(f"\nTotal damage area: {output['total_damage_pct']}% of road surface")