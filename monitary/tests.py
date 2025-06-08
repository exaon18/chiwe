import re

def extract_ebirr_info(message: str):
    pattern = r"Ref:(\d+)\s+Confirmed\.\s+(ETB\d+)"
    match = re.search(pattern, message, re.DOTALL)
    if match:
        trx_id = match.group(1)
        amount = match.group(2)
        return trx_id, amount
    return None, None
msg = """[-EBIRR-COOPay-] 
Ref:1343803723 Confirmed. ETB300 Received from tigst kassahun kidane (904091151),Date: 25/05/25 11:47:48, your new A/C balance is ETB301.42
https://transactioninfo.ebirr.com/coopay-Ebirr/receipt/1343803723"""

trx_id, amount = extract_ebirr_info(msg)

print("Transaction ID:", trx_id)
print("Amount:", amount[3:])
