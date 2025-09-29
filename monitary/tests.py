import requests

DEV_KEY = "7vqrbckrr4fvplcmt5ox3uqyhfxlaiwwqde3jjvt3gn1oo9ni4yyn0utxlb6e9yk"
PAYMENT_ID = "PuSpisofQ8k9VxsT5lBWiKD28DwU"
HEADERS = {"Authorization": f"key {DEV_KEY}", "Content-Type": "application/json"}

# GET
r = requests.get(f"https://api.minepi.com/v2/payments/{PAYMENT_ID}", headers=HEADERS, timeout=15)
print("GET", r.status_code)
print(r.text)

# If GET shows transaction.txid and verified==true, POST complete:
txid ="035730edbf45ad9f8f98bbf3806543a45bfcbd1dd59c968b728fe42fec060f60"# from GET
r2 = requests.post(f"https://api.minepi.com/v2/payments/{PAYMENT_ID}/complete", headers=HEADERS, json={"txid": txid}, timeout=15)
print("POST complete", r2.status_code)
print(r2.text)
