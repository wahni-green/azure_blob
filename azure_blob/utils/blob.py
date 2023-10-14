# Copyright (c) 2023, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import mimetypes
from datetime import datetime, timedelta
import re
# from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings


class AzureBlob():
	def __init__(self) -> None:
		self.settings = frappe.get_cached_doc("Azure Blob Settings")

		self.client = BlobServiceClient.from_connection_string(
			self.settings.get_password("connection_string")
		)

		# Can't get this to work, prolly my config issue.
		# self.credential = ClientSecretCredential(
		# 	tenant_id=self.settings.tenant_id,
		# 	client_id=self.settings.client_id,
		# 	client_secret=self.settings.client_secret
		# )
		# self.client = BlobServiceClient(
		# 	account_url=self.account_url,
		# 	credential=self.credential
		# )

		self.container_client = self.client.get_container_client(
			self.settings.container_name
		)

		if not self.container_client.exists():
			self.container_client.create_container()

	def is_enabled(self):
		return self.settings.enabled

	def strip_special_chars(self, file_name):
		"""
		Strips file charachters which doesnt match the regex.
		"""
		file_name = file_name.replace(' ', '_')
		regex = re.compile('[^0-9a-zA-Z._-]')
		file_name = regex.sub('', file_name)
		return file_name

	def validate_filename(self, file_name, extenstion=""):
		"""
		Renames file if file already exists.
		"""
		blob_client = self.container_client.get_blob_client(
			f"{file_name}.{extenstion}"
		)
		if blob_client.exists():
			file_name = f"{file_name}{frappe.generate_hash(length=5)}"
			file_name = self.validate_filename(file_name, extenstion)
		return f"{file_name}.{extenstion}"

	def upload_file(self, file):
		"""
		Uploads file to blob storage.
		"""
		file_name = file.file_name
		# remove extension from file name
		extenstion = file_name.split(".")[-1] or ""
		if extenstion:
			file_name = file.file_name.replace(f".{extenstion}", "")

		file_name = self.strip_special_chars(file_name)
		file_name = self.validate_filename(file_name, extenstion)
		blob_client = self.container_client.get_blob_client(file_name)
		blob_client.upload_blob(
			file._content,
			blob_type="BlockBlob",
			content_settings=ContentSettings(content_type=mimetypes.guess_type(file.file_name)[0])
		)
		return file_name, blob_client.url
	
	def delete_file(self, file_name):
		"""
		Deletes file from blob storage.
		"""
		blob_client = self.container_client.get_blob_client(file_name)
		blob_client.delete_blob()
		return True
	
	def get_file(self, file_name):
		"""
		Returns file from blob storage.
		"""
		blob_client = self.container_client.get_blob_client(file_name)
		file = blob_client.download_blob()
		# return file.readall()
		frappe.local.response.filename = file_name
		frappe.local.response.filecontent = file.readall()
		frappe.local.response.type = "download"
	
	def get_file_url(self, file_name):
		"""
		Returns file url from blob storage.
		"""
		blob_client = self.container_client.get_blob_client(file_name)
		return blob_client.url

	def get_sas_url(self, file_name, validity=None):
		"""
		Returns SAS url from blob storage.
		"""
		if not validity:
			validity = self.settings.sas_validity

		sas_token = generate_blob_sas(
			account_name=self.client.account_name,
			container_name=self.settings.container_name,
			blob_name=file_name,
			# Only required if not using Azure AD
			account_key=self.client.credential.account_key,
			permission=BlobSasPermissions(read=True, list=True),
			expiry=datetime.utcnow() + timedelta(hours=validity)
		)
		return f"{self.container_client.get_blob_client(file_name).url}?{sas_token}"
