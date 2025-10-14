import requests
import base64

image_path = "../SSR/data/ad.png"
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode('utf-8')

payload = {
    "image": base64_image,
    "demographic_profile": {
        "age": 30,
        "gender": "female",
        "location": "USA",
        "income": "$50k",
        "interests": ["yoga", "running", "health", "dance"]
    },
}

response = requests.post("http://localhost:8787/evaluate", json=payload)
print(response.json())