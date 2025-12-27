from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in company_wallet/__init__.py
from company_wallet import __version__ as version

setup(
	name="company_wallet",
	version=version,
	description="This app for make a company wallet make bulk payments",
	author="Fintechsys",
	author_email="info@fintechsys.net",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
