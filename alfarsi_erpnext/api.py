import frappe, json
from datetime import datetime


failed_to_scan = []
# result = {}
ai = ["17","15","11"]
# ai_batch_or_serial_or_ref_no = ["10","21","240"]
original_barcode = ""

def get_ai_details(barcode, result):
	try:
		process_string = barcode[2:8]
		if barcode[2:8].endswith("00"):
			process_string = barcode[2:8].replace("00","01")
		result[barcode[:2]] = str(datetime.strptime(process_string ,'%y%m%d')).split(" ")[0]
		barcode = barcode[8:]
		if len(barcode) >= 8 and barcode[:2] in ai:
			barcode = get_ai_details(barcode, result)

		return barcode

	except Exception as e:
		failed_to_scan.append(original_barcode)


def get_gs1_details(barcode):
	result = {}
	original_barcode = ""

	try:
		if barcode.startswith("01"):
			original_barcode = barcode
			result["01"] = barcode[2:16]
			barcode = barcode[16:]



		if barcode and barcode[:2] in ["10"]:
			for ai_value in ai:
				if ai_value in barcode[2:]:
					if len(barcode[2:].split(ai_value)) > 2:
						#same ai value repeated
						raise
					
					#two values in the second string
					if len(barcode[2:].split(ai_value)[1]) == 6:
						result[barcode[:2]] = barcode[2:].split(ai_value)[0]
						result[ai_value] = str(datetime.strptime(barcode[2:].split(ai_value)[1],'%y%m%d')).split(" ")[0]
						if result.get("10") and result["10"].endswith("0029"):
							result["10"] = result["10"].replace("0029","")
						return result
					
					#more than two values in the second string
					result[barcode[:2]] = barcode[2:].split(ai_value)[0]
					barcode = barcode[2:].split(ai_value)[1]
					if barcode[6:8] in ai:
						result[ai_value] = str(datetime.strptime(barcode[:6],'%y%m%d')).split(" ")[0]
						barcode = get_ai_details(barcode[6:], result)
						if not barcode:
							if result.get("10") and result["10"].endswith("0029"):
								result["10"] = result["10"].replace("0029","")
							return result
				else:
					result["10"] = barcode[2:]

		if barcode[:2] in ai:
			barcode = get_ai_details(barcode, result)


		if barcode and barcode[:2] in ["21"]:
			result["21"] = barcode[2:]
			if "0029" not in result["21"]:
				barcode = ""
			else:
				#21 in the middle case
				raise


		
		if barcode and barcode[:2] in ai:
			barcode = get_ai_details(barcode, result)


		if barcode and barcode[:2] in ["10"]:
			if "0029240" in barcode[2:]:
				result[barcode[:2]] = barcode.split("0029240")[0][2:]
				result["240"] = barcode.split("0029240")[1]

			if "002921" in barcode[2:]:
				result[barcode[:2]] = barcode.split("002921")[0][2:]
				result["21"] = barcode.split("002921")[1]


			if "240" in barcode[2:] and "0029240" not in barcode[2:]:
				if len(barcode[2:].split("240")[1]) > 2:
					result['240'] = barcode[2:].split("240")[1]
					result[barcode[0:2]] = barcode[2:].split("240")[0]
				else:
					result[barcode[0:2]] = barcode[2:]

			if "21" in barcode[2:] and "002921" not in barcode[2:]:
				if len(barcode[2:].split("21")[1]) > 2:
					result['21'] = barcode[2:].split("21")[1]
					result[barcode[0:2]] = barcode[2:].split("21")[0]
				else:
					result[barcode[0:2]] = barcode[2:]

			elif "10" not in result:
				result[barcode[0:2]] = barcode[2:]

		if result.get("10") and result["10"].endswith("0029"):
			result["10"] = result["10"].replace("0029","")

		return result

	except Exception as e:
		failed_to_scan.append(original_barcode)
		return {}



def hibc_uid(barcode):
	gtin = barcode.split("1/")[0][5:]
	batch_no = barcode.split("1/")[1][9:][:-1]
	expiry_date = str(datetime.strptime(barcode.split("1/")[1][:9][3:],'%y%m%d')).split(" ")[0]

	return gtin,batch_no,expiry_date


@frappe.whitelist()
def fetch_item_table(doc):
	no_item_gtin = []
	items = []
	failed_to_scan = []

	self = frappe._dict(json.loads(doc))

	for row in self['items']:
		if "item_code" in row.keys():
			items.append(row)

	scanned_values = self.scan.split("\n")
	for barcode in scanned_values:
		barcode_details = {}
		flag = False
		gtin = batch_no = expiry_date = ""
		if barcode.startswith("+"): ## test for another hibc
			gtin = barcode.split("1/")[0][5:]
			batch_no = barcode.split("1/")[1][9:][:-1]
			expiry_date = str(datetime.strptime(barcode.split("1/")[1][:9][3:],'%y%m%d')).split(" ")[0]
			
			if not gtin:
				continue

			for row in range(0,len(items)):
				item = frappe._dict(items[row])
				if frappe.db.get_value("Item",item.item_code,"gtin_number") == gtin and item.supplier_batch_no == batch_no:
					flag = True
					items[row]["qty"] += 1

			if not flag:
				if not frappe.db.get_value("Item",{"gtin_number":gtin}):
					no_item_gtin.append(barcode)
					continue
				items.append({"item_code":frappe.db.get_value("Item",{"gtin_number":gtin}),"qty":1,"supplier_batch_no":batch_no, "expiry_date": expiry_date})


		if barcode.startswith("01"):
			barcode_details = get_gs1_details(barcode)
			gtin = barcode_details.get("01") or ""
			batch_no = barcode_details.get("10") or ""
			production_date = barcode_details.get("11") or ""
			best_before_date = barcode_details.get("15") or ""
			expiry_date = barcode_details.get("17") or ""
			s_no = barcode_details.get("21") or ""

			if not gtin:
				continue

			if not frappe.db.get_value("Item",{"gtin_number":gtin}):
				no_item_gtin.append(barcode)
				continue
			
			item_details = frappe.db.get_list("Item",{"gtin_number":gtin},["*"])[0]
			for row in range(0,len(items)):
				item = frappe._dict(items[row])
				if batch_no and s_no:
					if item_details.gtin_number == gtin and item.supplier_batch_no == batch_no and item.custom_serial_number:
						flag = True
						items[row]["qty"] += 1
						items[row]["custom_serial_number"] += "\n"+s_no

				if batch_no and not s_no:
					if item_details.gtin_number == gtin and item.supplier_batch_no == batch_no:
						flag = True
						items[row]["qty"] += 1

				if s_no and not batch_no:
					if item_details.gtin_number == gtin and item.serial_no:
						flag = True
						items[row]["qty"] += 1
						items[row]["serial_no"] += "\n"+s_no

			if not flag:
				if s_no and not batch_no:
					items.append({"item_code":item_details.name ,"item_name": item_details.item_name ,"description":item_details.description,"uom":item_details.uom, "qty":1,"serial_no": s_no+"\n", "expiry_date": expiry_date})
				
				if batch_no and not s_no:
					items.append({"item_code":item_details.name ,"item_name": item_details.item_name,"description":item_details.description,"uom":item_details.uom, "qty":1,"supplier_batch_no":batch_no, "expiry_date": expiry_date})

				if batch_no and s_no:
					items.append({"item_code":item_details.name ,"item_name": item_details.item_name,"description":item_details.description,"uom":item_details.uom, "qty":1,"supplier_batch_no":batch_no, "custom_serial_number": s_no ,"expiry_date": expiry_date})

	if no_item_gtin:
		frappe.msgprint("<b>No Item GSTIN present in Item Doctype for</b><br><br>"+'<br>'.join(no_item_gtin))
		if failed_to_scan:
			frappe.msgprint("<b>Failed to scan</b><br><br>"+'<br>'.join(failed_to_scan))

	return {"items":items, "failed_to_process": '\n'.join(no_item_gtin) + '\n' + '\n'.join(failed_to_scan)}

