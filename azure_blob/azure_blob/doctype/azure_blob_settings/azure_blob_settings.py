# Copyright (c) 2023, Wahni IT Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document
from azure_blob.utils.blob import AzureBlob


class AzureBlobSettings(Document):
	def validate(self):
		self.validate_connection_string()
		self.sas_validity = cint(self.sas_validity)
	
	def validate_connection_string(self):
		if not self.enabled:
			return

		if not self.connection_string:
			frappe.throw(_("Connection String is required."))
		
		if not self.container_name:
			frappe.throw(_("Container Name is required."))

	def on_update(self):
		if AzureBlob():
			frappe.msgprint(_("Connection Successful"), alert=True)
