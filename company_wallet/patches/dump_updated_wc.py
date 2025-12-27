import frappe


def execute():
    starting_value = 123
    frappe.db.sql("SET @org_id := %(starting_value)s", {"starting_value": starting_value})  # nosemgrep
    frappe.db.sql("""
        UPDATE `tabWallet Company`
        SET organization_id = (@org_id := @org_id + 1) WHERE organization_id IS NULL
    """) # nosemgrep