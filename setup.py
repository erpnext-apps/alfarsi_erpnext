from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in alfarsi_erpnext/__init__.py
from alfarsi_erpnext import __version__ as version

setup(
	name="alfarsi_erpnext",
	version=version,
	description="A custom app for Alfarsi International",
	author="Frappe Technologies Pvt. Ltd.",
	author_email="developers@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
