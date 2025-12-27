### create_wallet_payment
- url: `https://jawali-web.fintechsys.net/api/method/company_wallet.api.payment.create_wallet_payment`
- body:
```json
{
 "amount": 10000.0,
 "currency": "YER",
 "payment_channel": "Remittance",
 "recipient": "Ali Jamal",
 "recipient_phone": "432432",
	"fee_amount": 0,
	"fee_currency": "YER",
	"with_submit": true
}
```
- response:
```json
{
	"status": true,
	"data": {
		"name": "CW-WP-2024-00002",
		"owner": "test@fintechsys.net",
		"creation": "2024-02-24 15:29:34.843791",
		"modified": "2024-02-24 15:29:34.892006",
		"modified_by": "test@fintechsys.net",
		"docstatus": 1,
		"idx": 0,
		"naming_series": "CW-WP-.YYYY.-.",
		"wallet_company": "Test",
		"payment_channel": "Remittance",
		"recipient": "Ali Jamal",
		"recipient_phone": "432432",
		"amount": 10000.0,
		"currency": "YER",
		"fee_amount": 0.0,
		"fee_currency": "YER",
		"doctype": "Wallet Payment"
	},
	"errors": null,
	"messages": [],
	"message": ...
}
```

### submit_wallet_payment
- url: `https://jawali-web.fintechsys.net/api/method/company_wallet.api.payment.create_wallet_payment`
- body:
```json
{
  "name": "CW-WP-2024-00003"
}
```
- response
```json
{
	"status": true,
	"data": {
		"name": "CW-WP-2024-00003",
		"owner": "Administrator",
		"creation": "2024-02-24 11:33:43.292324",
		"modified": "2024-02-24 16:00:45.552183",
		"modified_by": "4255524@test.test",
		"docstatus": 1,
		"idx": 0,
		"naming_series": "CW-WP-.YYYY.-.",
		"wallet_company": "Test Wallet Company",
		"payment_channel": "Remittance",
		"recipient": "Ali Jamal",
		"recipient_phone": "432432",
		"amount": 10000.0,
		"currency": "YER",
		"fee_amount": 0.0,
		"fee_currency": "YER",
		"doctype": "Wallet Payment"
	},
	"errors": null,
	"messages": [],
	"message": ...
}
```

### update_wallet_payment
- url: `https://jawali-web.fintechsys.net/api/method/company_wallet.api.payment.update_wallet_payment`
- body:
```json
{
	"name": "CW-WP-2024-00003",
	"amount": 344
}
```
- response:
```json
{
	"status": true,
	"data": {
		"name": "CW-WP-2024-00005",
		"owner": "4255524@test.test",
		"creation": "2024-02-24 12:31:08.271874",
		"modified": "2024-02-24 16:05:40.175094",
		"modified_by": "4255524@test.test",
		"docstatus": 0,
		"idx": 0,
		"naming_series": "CW-WP-.YYYY.-.",
		"wallet_company": "EEE",
		"payment_channel": "Remittance",
		"recipient": "Ali Jamal",
		"recipient_phone": "432432",
		"amount": 344.0,
		"currency": "YER",
		"fee_amount": 0.0,
		"fee_currency": "YER",
		"doctype": "Wallet Payment"
	},
	"errors": null,
	"messages": [],
	"message": ...
}
```

### get_wallet_payment
- url: `https://jawali-web.fintechsys.net/api/method/company_wallet.api.payment.create_wallet_payment`
- body:
```json
{
 "name": "CW-WP-2024-00003"
}
```
- response:
```json
{
	"status": true,
	"data": {
		"name": "CW-WP-2024-00003",
		"owner": "Administrator",
		"creation": "2024-02-24 11:33:43.292324",
		"modified": "2024-02-24 16:06:29.762728",
		"modified_by": "4255524@test.test",
		"docstatus": 1,
		"idx": 0,
		"naming_series": "CW-WP-.YYYY.-.",
		"wallet_company": "Test Wallet Company",
		"payment_channel": "Remittance",
		"recipient": "Ali Jamal",
		"recipient_phone": "432432",
		"amount": 10000.0,
		"currency": "YER",
		"fee_amount": 0.0,
		"fee_currency": "YER",
		"doctype": "Wallet Payment"
	},
	"errors": null,
	"messages": [],
	"message": ...
}
```

### get_list_wallet_payment
- url: `https://jawali-web.fintechsys.net/api/method/company_wallet.api.payment.get_list_wallet_payment`
- body:
```json
{
	"fields": ["name", "amount", "currency"],
	"filters": {
		"docstatus": 1,
		"amount": [">", 1000]
	},
	"limit_start": 0,
	"limit": 20,
	"order_by": "modified asc",
	"or_filters": [["currency", "=", "YER"], ["currency", "=", "USD"]]
}
```
- response:
```json
{
	"status": true,
	"data": {
		"count": 5,
		"result": [
			{
				"name": "c6375718b8",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00001",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00002",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00004",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00003",
				"amount": 10000.0,
				"currency": "YER"
			}
		]
	},
	"errors": null,
	"messages": [],
	"message": {
		"count": 5,
		"result": [
			{
				"name": "c6375718b8",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00001",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00002",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00004",
				"amount": 10000.0,
				"currency": "YER"
			},
			{
				"name": "CW-WP-2024-00003",
				"amount": 10000.0,
				"currency": "YER"
			}
		]
	}
}
```

### create_wallet_bulk_payment
- url: `http://v15.localhost:8209/api/method/company_wallet.api.payment.create_wallet_bulk_payment`
- body:
```json
{
  "payment_channel": "Remittance",
  "wallet_bulk_payment_transactions": [
   {
    "amount": 1200.0,
    "currency": "YER",
    "fee_amount": 0.0,
    "fee_currency": "YER",
    "recipient": "Ali Mohammed",
    "recipient_phone": "77777"
   },
   {
    "amount": 2000.0,
    "currency": "YER",
    "fee_amount": 0.0,
    "fee_currency": "YER",
    "recipient": "Hamed Ali",
    "recipient_phone": "887122"
   }
  ]
}
```
- response:
```json
{
	"status": true,
	"data": {
		"name": "CW-WBP-2024-00003",
		"owner": "4255524@test.test",
		"creation": "2024-02-24 16:08:00.848492",
		"modified": "2024-02-24 16:08:00.848492",
		"modified_by": "4255524@test.test",
		"docstatus": 0,
		"idx": 0,
		"naming_series": "CW-WBP-.YYYY.-.",
		"wallet_company": "EEE",
		"payment_channel": "Remittance",
		"doctype": "Wallet Bulk Payment",
		"wallet_bulk_payment_transactions": [
			{
				"name": "f43610def9",
				"owner": "4255524@test.test",
				"creation": "2024-02-24 16:08:00.848492",
				"modified": "2024-02-24 16:08:00.848492",
				"modified_by": "4255524@test.test",
				"docstatus": 0,
				"idx": 1,
				"recipient": "Ali Mohammed",
				"recipient_phone": "77777",
				"amount": 1200.0,
				"currency": "YER",
				"fee_amount": 0.0,
				"fee_currency": "YER",
				"parent": "CW-WBP-2024-00003",
				"parentfield": "wallet_bulk_payment_transactions",
				"parenttype": "Wallet Bulk Payment",
				"doctype": "Wallet Bulk Payment Transaction",
				"__unsaved": 1
			},
			{
				"name": "7ae201a270",
				"owner": "4255524@test.test",
				"creation": "2024-02-24 16:08:00.848492",
				"modified": "2024-02-24 16:08:00.848492",
				"modified_by": "4255524@test.test",
				"docstatus": 0,
				"idx": 2,
				"recipient": "Hamed Ali",
				"recipient_phone": "887122",
				"amount": 2000.0,
				"currency": "YER",
				"fee_amount": 0.0,
				"fee_currency": "YER",
				"parent": "CW-WBP-2024-00003",
				"parentfield": "wallet_bulk_payment_transactions",
				"parenttype": "Wallet Bulk Payment",
				"doctype": "Wallet Bulk Payment Transaction",
				"__unsaved": 1
			}
		]
	},
	"errors": null,
	"messages": [],
	"message": ...
```
