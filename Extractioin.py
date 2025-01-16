import os
import logging
from datetime import datetime
from API_trigger import convertBase64Fun, apiTriggerFun
from DB_operation import insertExtractedData

# Setup logger
logging.basicConfig(level=logging.INFO)

def extract_data_with_retries(base64_file, max_retries=3):
    """
    Attempt to fetch data from the API with retries on failure.
    """
    attempts = 0
    data = None
    
    while attempts < max_retries:
        data = apiTriggerFun(base64_file)
        if data:
            logging.info("Data successfully fetched!")
            return data
        attempts += 1
        logging.warning(f"Attempt {attempts} failed, retrying...")

    logging.error("Failed to fetch data after max retries.")
    return None

def extract_invoice_data(data):
    """
    Extract all necessary fields from the API response data.
    """
    extracted_data = {
        'irn_no': data.get('irnNo', ''),
        'ack_no': data.get('ackNo', ''),
        'ack_date': data.get('ackDate', ''),
        'vendor_name': data.get('vendorName', ''),
        'vendor_gstin': data.get('vendorGSTIN', ''),
        'vendor_pan': data.get('vendorPAN', ''),
        'msme_no': data.get('msmeNo', ''),
        'drug_license_no': data.get('drugLicenseNo', [''])[0] if data.get('drugLicenseNo') else '',
        'invoice_number': data.get('invoiceNo', ''),
        'eway_bill_no': data.get('ewayBillNo', ''),
        'invoice_date': data.get('invoiceDate', ''),
        'term_of_payment': data.get('mode/termsOfPayment', ''),
        'po_number': data.get('purchaseOrderNo', [''])[0] if data.get('purchaseOrderNo') else '',
        'po_date': data.get('purchaseOrderDate', [''])[0] if data.get('purchaseOrderDate') else '',
        'bank_details': {
            'bank_name': data.get('bankDetails', {}).get('bankName', ''),
            'account_no': data.get('bankDetails', {}).get('accountNo', ''),
            'ifsc_no': data.get('bankDetails', {}).get('ifscNo', '')
        },
        'round_off':data.get('roundingOff', ''),
        'freight_term': '',
        'place_of_supply': '',
        'consignee_name': data.get('vendorName', ''),
        'consignee_gstin': data.get('vendorGSTIN', ''),
        'consignee_pan': data.get('vendorPAN', ''),
        'freight': ''
    }

    return extracted_data

def extract_line_items(data):
    """
    Extract all line items from the invoice data.
    """
    line_items = []
    for line_data in data.get('invoiceItems', []):
        line_item = {
            'description': line_data.get('description', ''),
            'quantity': line_data.get('quantity', ''),
            'hsn_code': line_data.get('hsnSac', ''),
            'tax_rate': data.get('taxableAmount', ''),
            'rate': line_data.get('rate', ''),
            'unit': line_data.get('uom', ''),
            'amount': line_data.get('totalAmount', ''),
            'total_tax': data.get('totalTax', '')
        }
        line_items.append(line_item)
    
    return line_items

def prepare_data_for_db(extracted_data, line_items, file_name):
    """
    Prepare the data in the correct format for database insertion.
    """
    timestamp = datetime.now()
    # Creating values for the database insert
    for line_item in line_items:
        value = (
            extracted_data['irn_no'],
            extracted_data['ack_no'],
            extracted_data['ack_date'],
            extracted_data['vendor_name'],
            extracted_data['vendor_gstin'],
            extracted_data['vendor_pan'],
            extracted_data['msme_no'],
            extracted_data['drug_license_no'],
            extracted_data['invoice_number'],
            extracted_data['eway_bill_no'],
            extracted_data['invoice_date'],
            extracted_data['term_of_payment'],
            extracted_data['po_number'],
            extracted_data['po_date'],
            line_item['description'],
            line_item['quantity'],
            line_item['hsn_code'],
            line_item['tax_rate'],
            line_item['rate'],
            line_item['unit'],
            line_item['amount'],
            line_item['total_tax'],
            extracted_data['round_off'],  # rounding_off

            '',  # total_invoice
            extracted_data['bank_details']['bank_name'],
            extracted_data['bank_details']['account_no'],
            extracted_data['bank_details']['ifsc_no'],
            extracted_data['freight_term'],
            extracted_data['place_of_supply'],
            extracted_data['consignee_name'],
            extracted_data['consignee_gstin'],
            extracted_data['consignee_pan'],
            extracted_data['freight'],
            timestamp,
            file_name,
            'pass'  # remark
        )
        print('value : ',value)
        columns = (
            'irn_no', 'ack_no', 'ack_date', 'vendor_name', 'vendor_gstin', 'vendor_pan',
            'msme_no', 'drug_license_no', 'invoice_number', 'eway_bill_no', 'invoice_date', 
            'term_of_payment', 'po_number', 'po_date', 'item_description', 'item_quantity', 
            'hsn_sac_code', 'tax_rate', 'rate', 'unit', 'amount', 'total_tax', 'rounding_off',
            'total_invoice', 'bank_name', 'account_no', 'ifsc_no', 'freight_term', 
            'place_of_supply', 'consignee_name', 'consignee_gstin', 'consignee_pan', 
            'freight', 'timestamp', 'file_name', 'remark'
        )
        insertExtractedData(columns, value)

def extractionFun(file_path):
    """
    Main extraction function that handles file processing and data extraction.
    """
    base64_file = convertBase64Fun(file_path)
    data = extract_data_with_retries(base64_file)
    print('all data :',data,"\n\n")

    if not data:
        timestamp = datetime.now()
        file_name = os.path.basename(file_path)
        insertExtractedData(
            ('timestamp', 'file_name', 'remark'),
            (timestamp, file_name, 'fail')
        )
        return

    extracted_data = extract_invoice_data(data)


    # print(extracted_data,">>>>\n\n")
    # here we define some conditoin base on some fields like irn no,invoince no,e-way bill no,invoice date,item qty,amount,total invoice,
    # extracted_data = {
    #     'irn_no':None,
    #     'invoice_number':'1',
    #     'eway_bill_no':'2',
    #     'invoice_date':'1',
        
    # }

    if extracted_data['irn_no']=='' or extracted_data['irn_no']==None  or extracted_data['invoice_number']=='' or extracted_data['invoice_number']==None  or  extracted_data['eway_bill_no']=='' or extracted_data['eway_bill_no']==None  or extracted_data['invoice_date']=='' or extracted_data['invoice_date']==None :
        # we want re-try api triggering
        print('\n\n','yessss','\n\n')

        base64_file = convertBase64Fun(file_path)
        data = extract_data_with_retries(base64_file)
        print('all data :',data,"\n\n")
        if not data:
            timestamp = datetime.now()
            file_name = os.path.basename(file_path)
            insertExtractedData(
                ('timestamp', 'file_name', 'remark'),
                (timestamp, file_name, 'fail')
            )
            return
        
    line_items = extract_line_items(data)
    print('line items :',line_items,'\n\n')
    file_name = os.path.basename(file_path)

    prepare_data_for_db(extracted_data, line_items, file_name)

def process_files_in_directory(input_folder):
    """
    Process all files in a given folder.
    """
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        logging.info(f"Processing file: {file_name}")
        extractionFun(file_path)
        logging.info('-' * 80)

# Directory path where input files are located
input_folder = r'C:\Users\Admin\Downloads\akums_oce\lohia_new\input'
# input_folder = r'C:\Users\Admin\Downloads\akums_oce\lohia_new\Invoices'
process_files_in_directory(input_folder)
