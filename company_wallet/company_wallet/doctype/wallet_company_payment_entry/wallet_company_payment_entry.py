# Copyright (c) 2024, fintechsys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class WalletCompanyPaymentEntry(Document):
    def need_to_background(self):
        need_background = False
        if self.payment_type == 'Remittance':
            if len(self.remittances) > 30:
                need_background = True
        else:
            if len(self.wallet_transfers) > 30:
                need_background = True
        return need_background

    @frappe.whitelist()
    def create_payments(self):
        self.check_permission("write")
        need_background = self.need_to_background()
        if need_background:
            frappe.publish_realtime("create_payments_progres", user=frappe.session.user)
            frappe.enqueue(create_payments_task, payment_entry_name=self.name, publish_progress=True)
        else:
            create_payments_task(self.name)

    @frappe.whitelist()
    def get_beneficiaries_from_template(self):
        beneficiaries = frappe.get_all("Payment Template Beneficiary", filters={"beneficiary_template": "self."})
        receptions = []
        for b in beneficiaries:
            r = {'recipient_name': b.beneficiary_name, 'recipient_account_number': b.beneficiary_name, 'recipient_phone_number': b.beneficiary_phone_number, 'amount': b.amount, 'currency': b.currency}
            receptions.append(r)
        if self.payment_type == 'Remittance':
            self.set('remittances', receptions)
        else:
            self.set('wallet_transfers', receptions)
                
    def submit_payments(self):
        self.check_permission("submit")
        need_background = self.need_to_background()
        if need_background:
            frappe.publish_realtime("submit_payments_progres", user=frappe.session.user)
            frappe.enqueue(submit_payment_entry, payment_entry=self.name, publish_progress=True)
        else:
            submit_payment_entry(self.name)

    def on_submit(self):
        self.submit_payments()


def create_payments_task(payment_entry_name, publish_progress=True):
    payment_entry = frappe.get_doc("Wallet Company Payment Entry", payment_entry_name)
    args = {"doctype": "Company Payment", 'payment_type': payment_entry.payment_type}
    count = 0
    if not payment_entry.is_created_payments:
        if payment_entry.payment_type == 'Remittance':
            length = len(payment_entry.remittances)
            for i in payment_entry.remittances:
                doc = frappe.get_doc(**args)
                doc.payment_entry = payment_entry
                doc.amount = i.amount
                doc.currency = i.currency
                doc.company_payment_provider = payment_entry.company_payment_provider
                doc.company = payment_entry.company
                doc.recipient_name = i.recipient_name
                doc.recipient_phone_number = i.recipient_phone_number
                doc.insert()
                count += 1
                frappe.publish_progress(
                    count * 100 / length,
                    title=_("Creating Payments..."),
                )

        else:
            for i in payment_entry.wallet_transfers:
                length = len(payment_entry.wallet_transfers)
                doc = frappe.get_doc(**args)
                doc.company = payment_entry.company
                doc.payment_entry = payment_entry
                doc.amount = i.amount
                doc.currency = i.currency
                doc.company_payment_provider = payment_entry.company_payment_provider
                doc.recipient_account_number = i.wallet_account_number
                count += 1
                count += 1
                frappe.publish_progress(
                    count * 100 / length,
                    title=_("Creating Payments..."),
                )
        payment_entry.is_created_payments = True
        payment_entry.save()


def submit_payment_entry(payment_entry):
    payments = frappe.get_all("Company Payment", filters={"payment_entry": payment_entry})
    length = len(payments)
    count = 0
    for i in payments:
        doc = frappe.get_doc("Company Payment", i.name)
        doc.submit()
        frappe.publish_progress(
            count * 100 / length,
            title=_("Submit Payments..."),
        )
        count += 1
