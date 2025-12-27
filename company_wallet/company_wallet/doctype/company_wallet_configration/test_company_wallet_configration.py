# Copyright (c) 2024, fintechsys and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import _


class TestCompanyWalletConfigration(FrappeTestCase):
	def test_remove_user_name_on_token(self):
		doc = frappe.get_single("Company Wallet Configration")
		doc.server_url = "http://www.test.com"
		doc.authentication_type = "Token"
		doc.user_name = "test"
		doc.password = "test"
		doc.save()
		self.assertIsNone(doc.user_name)

	def test__user_name_reqd_basic(self):
		doc = frappe.get_single("Company Wallet Configration")
		doc.server_url = "http://www.test.com"
		doc.authentication_type = "Basic"
		doc.user_name = None
		doc.password = "test"
		with self.assertRaises(frappe.MandatoryError) as context:
			doc.save()

		field = str(context.exception).split(":")[-1].strip()
		self.assertEqual(field, _(doc.get_label_from_fieldname("user_name")))
