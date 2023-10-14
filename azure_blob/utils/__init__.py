# Copyright (c) 2023, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from azure_blob.utils.blob import AzureBlob


def upload_to_blob(file):
    blob = AzureBlob()
    if not blob.is_enabled():
        return file.save_file_on_filesystem()

    frappe.msgprint(_("Uploading to Azure Blob Storage"), alert=True)
    if isinstance(file._content, str):
        file._content = file._content.encode()

    file_name, url = blob.upload_file(file)
    file.file_url = blob.get_sas_url(file_name)
    file.blob_url = url
    file.file_name = file_name
    frappe.msgprint(_("Uploaded to Azure Blob Storage"), alert=True)


def delete_from_blob(file, only_thumbnail=False):
    file.delete_file_from_filesystem(only_thumbnail=True)

    blob = AzureBlob()
    if not blob.is_enabled():
        return

    frappe.msgprint(_("Deleting from Azure Blob Storage"), alert=True)
    blob.delete_file(file.file_name)
    frappe.msgprint(_("Deleted from Azure Blob Storage"), alert=True)


@frappe.whitelist()
def download_file_from_blob():
    file_name = frappe.local.form_dict.file_name
    if not file_name:
        frappe.throw("File name is required.")
    
    file = frappe.get_value("File", {"file_name": file_name})
    if not file:
        frappe.throw("File not found.", exc=frappe.DoesNotExistError)
    
    file = frappe.get_doc("File", file)
    if not file.is_downloadable():
        frappe.throw("File not found.", exc=frappe.PermissionError)

    blob = AzureBlob()
    blob.get_file(file.file_name)


@frappe.whitelist()
def get_sas_url():
    file_name = frappe.local.form_dict.file_name
    if not file_name:
        frappe.throw("File name is required.")
    
    file = frappe.get_value("File", {"file_name": file_name})
    if not file:
        frappe.throw("File not found.", exc=frappe.DoesNotExistError)
    
    file = frappe.get_doc("File", file)
    if not file.is_downloadable():
        frappe.throw("File not found.", exc=frappe.PermissionError)

    validity = cint(frappe.local.form_dict.validity)
    blob = AzureBlob()
    return blob.get_sas_url(file.file_name, validity)
