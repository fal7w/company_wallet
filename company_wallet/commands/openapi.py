import importlib
import os.path

import frappe
import click
from company_wallet.hooks import CW_OPENAPI_OUTPUT_FILE

from company_wallet.generate_swagger import write_openapi_spec


@click.command("generate-cw-openapi-spec", help="Generate a static openapi in json file if this file doesn't exist it will generate them on fly when view")
def generate_cw_openapi_spec():
    api_directory = frappe.get_app_path("company_wallet", "api")
    output_file = get_output_file()
    write_openapi_spec(api_directory, output_file)


def get_output_file():
    output_file = frappe.get_app_path("company_wallet", *CW_OPENAPI_OUTPUT_FILE)
    return output_file


@click.command("remove-cw-openapi-spec", help="remove static file")
def remove_cw_openapi_spec(app=None):
    output_file = get_output_file()
    try:
        os.remove(output_file)
    except FileNotFoundError:
        pass


commands = [generate_cw_openapi_spec, remove_cw_openapi_spec]
