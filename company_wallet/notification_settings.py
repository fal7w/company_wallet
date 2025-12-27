import frappe
from fcm_notification.send_notification import send_notification
from frappe.utils import nowdate


def send_fcm_notification(doc, method=None):
	has_notification_setup = check_doctype_notifications(doc.doctype)
	if has_notification_setup:
		get_context({"doc": doc})


def check_doctype_notifications(doctype_name):
	notifications = frappe.get_all("Notification",
							filters={
								"document_type": doctype_name,
								"enabled": 1,
								"custom_firebase_notification": 1
							},
							fields=["name", "channel", "subject"])
	return notifications


def get_context(context):
	doc = context["doc"]
	send_notification(doc)


def process_offers_notifications():
	today = nowdate()
	offers = frappe.get_all('Offer Detail',
			filters={
				'from_date': ['<=', today],
				'to_date': ['>=', today],
				'published': 0,
				'docstatus': 1,
			},
			fields=['name', 'from_date', 'to_date'])
	frappe.db.set_value('Offer Detail', {
					'from_date': ['<=', today],
					'to_date': ['>=', today],
					'published': 0,
					'docstatus': 1,
				},
				"published", 1)
	for offer in offers:
		doc = frappe.get_doc('Offer Detail', offer.name)
		doc.run_method("on_change")
		# get_context({"doc": doc})
