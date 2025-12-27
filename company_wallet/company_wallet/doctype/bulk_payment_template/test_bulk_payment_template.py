import frappe
from frappe.tests.utils import FrappeTestCase
from company_wallet.api.bulk_payment_template import (
	create_or_update_bulk_payment_template,
	retrieve_bulk_payment_template,
	delete_bulk_payment_template,
)
from .bulk_payment_template import BulkPaymentTemplate


class TestBulkPaymentTemplate(FrappeTestCase):

	def test_bulk_payment_template(self):
		# Create a BulkPaymentTemplate document
		details = {
			"posting_date": "2024-02-12",
			"payment_channel": "Wallet",
			"wallet_company": "5",
			"currency": "USD",
			"bulk_payment_detail": [{"full_name": "John Doe", "amount": 1500, "phone_number": "777888999"}]
		}

		template_name = create_or_update_bulk_payment_template(**details)

		self.assertIsNotNone(template_name)
		self.assertDocumentEqual(details, template_name)

		self.assertEqual(template_name.docstatus, 1)

		# Retrieve the BulkPaymentTemplate document using the API function
		retrieved_data = retrieve_bulk_payment_template(template_name.name)
		self.assertIsNotNone(retrieved_data)

		# Check if the retrieved data matches the expected values
		
		self.assertDocumentEqual(template_name, retrieved_data)

		# Delete the BulkPaymentTemplate document
		delete_bulk_payment_template(template_name.name)
		
		# Check if the document is deleted
		with self.assertRaises(frappe.exceptions.DoesNotExistError):
			frappe.get_doc("Bulk Payment Template", template_name.name)

	def test_set_amount_field(self):
		details = {
				"posting_date": "2024-02-12",
				"payment_channel": "Wallet",
				"wallet_company": 5,
				"currency": "USD",
				"bulk_payment_detail": [
					{"full_name": "John Doe", "amount": 1500, "phone_number": "777888999"},
					{"full_name": "Ted", "amount": 2000, "phone_number": "777755222"}
							]
			}

		template_name = create_or_update_bulk_payment_template(**details)

		BulkPaymentTemplate.set_amount_field(template_name)

		expected_total_amount = 3500
		self.assertEqual(template_name.total_amount, expected_total_amount, "Total amount should be calculated correctly")
	