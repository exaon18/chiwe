import requests
import json

url = "https://mjz8t6vq-8000.euw.devtunnels.ms/monitary/payment-weebhook/"

payload = {
    "payment_id": "1234567890",
    "payment_status": "finished",
    "order_id": "ORD-USER74-20250716111443"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

print(response.status_code)
print(response.text)
