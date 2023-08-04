from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in azure_blob/__init__.py
from azure_blob import __version__ as version

setup(
	name="azure_blob",
	version=version,
	description="Blob sync for attachments",
	author="Wahni IT Solutions",
	author_email="info@wahni.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
