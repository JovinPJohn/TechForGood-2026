from damage_quantification import quantify_damage

output = quantify_damage('images/test1.png', conf_threshold=0.05)
print(f"Detections at low threshold: {len(output['detections'])}")
for d in output['detections']:
    print(f"  -> {d['type']} conf:{d['confidence']}")