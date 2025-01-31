import os
import re
import logging
from datetime import datetime
from API_trigger import convertBase64Fun, apiTriggerFun
from DB_operation import insertExtractedData


# Setup logger
logging.basicConfig(level=logging.INFO)

"""
Attempt to fetch data from the API with retries on failure.
"""
def extractDataWithRetriesFun(base64_file, max_retries=3):
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

"""
Extract all necessary fields from the API response data.
"""
def extractInvoiceDataFun(data):
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
        'total_invoice':data.get('netPayableAmount', ''),
        'freight_term': '',
        'place_of_supply': data.get('placeOfSupply', ''),
        'buyer_name': data.get('buyerName', ''),
        'buyer_gstin': data.get('buyerGSTIN', ''),
        'buyer_pan': data.get('buyerPAN', ''),
        'freight': ''
    }

    return extracted_data


"""
Extract all line items from the invoice data.
"""
def extractIineItemsFun(data):
    line_items = []
    for line_data in data.get('invoiceItems', []):
        
        line_item = {
            'description': line_data.get('description', ''),
            'quantity': line_data.get('quantity', ''),
            'hsn_code': line_data.get('hsnSac', ''),
            'tax_rate': data.get('taxableAmount', ''),
            'rate': line_data.get('rate', ''),
            'unit': line_data.get('uom', ''),
            'amount': line_data.get('taxableAmount', ''),
            'total_tax': data.get('totalTax', ''),
            'item_code':line_data.get('itemCode', '')
        }

        line_items.append(line_item)
    
    return line_items


# def expectedVendor():

    



# def poNmberDateAndItemcode(description,extracted_data['po_number'],extracted_data['po_date'],line_item['description']):
def poNmberDateAndItemcode(description,po_number,po_date,item_code):

    

    # po number 
    # if re.search(r'(?si)po\sno.*?[0-9]+|p\.o\.\sno(\.\s|\s)[0-9]+',description):
    if re.search(r'(?si)po\sno.*?[0-9]+|p\.o\.\sno.*?[0-9]+',description):
        po_number = re.search(r'(?si)po\sno.*?[0-9]+|p\.o\.\sno(\.\s|\s)[0-9]+',description).group()
        po_number = re.search(r'(?si)[0-9]+',po_number).group()
    else:
        po_number = po_number
    print('po_number :',po_number,sep='  ||  ')

    # po date
    if re.search(r'(?si)po\sno.*?\d+(\.|\-)\d+(\.|\-)\d+',description):
        po_date = re.search(r'(?si)po\sno.*?\d+(\.|\-)\d+(\.|\-)\d+',description).group()
        po_date = re.search(r'(?si)\d+(\.|\-)\d+(\.|\-)\d+',po_date).group()

    else:
        po_date = po_date
    print('po date :',po_date,sep=' || ')


    # item code / material number
    if re.search(r'(?si)(material|mat)\sno.*?[0-9]+',description):
        item_code = re.search(r'(?si)(material|mat)\sno.*?[0-9]+',description).group()
        item_code = re.search(r'(?si)[0-9]+',item_code).group()

    else:
        item_code = item_code 
    print('item_code :',item_code,sep=' || ')
    

    return po_number,po_date,item_code 


"""
Prepare the data in the correct format for database insertion.
"""
def prepareDataForDbFun(extracted_data, line_items, file_name):
    timestamp = datetime.now()

    expected_vendor_list = [
        'ALLIED LABELS PVT.LTD',
        'CAREWELL GLASS & AMPOULES PVT. LTD.',
        'SIGNET EXCIPIENTS PRIVATE LIMITED',
        'Vinayak Enterprises',
        'Vinayak Enterprises (Roorkee)',
        'Laxmi Print N Pack',
        'METROCHEM API PRIVATE LIMITED UNIT-I',
        'CHIPQO ENTERPRISES 2023-24',
        'ONYX BIOTEC PVT. LTD.',
        'TORIOX SERGUSA PACKAGING PRIVATE LIMITED',
        'M/s Laxmi Print N Pack',
        'COVALENT LABORATORIES PRIVATE LIMITED'
    ]
    expected_vendor_list = [vendor.lower() for vendor in expected_vendor_list]



    # Creating values for the database insert
    for line_item in line_items:

        if extracted_data['vendor_name'].lower() in expected_vendor_list:
            print('condition satasfied >>>>')
            extracted_data['po_number'],extracted_data['po_date'],line_item['item_code'] = poNmberDateAndItemcode(line_item['description'],extracted_data['po_number'],extracted_data['po_date'],line_item['item_code'])
        
        

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
            line_item['item_code'],
            line_item['quantity'],
            line_item['hsn_code'],
            line_item['tax_rate'],
            line_item['rate'],
            line_item['unit'],
            line_item['amount'],
            line_item['total_tax'],
            extracted_data['round_off'],  # rounding_off
            extracted_data['total_invoice'], # total_invoice
            extracted_data['bank_details']['bank_name'],
            extracted_data['bank_details']['account_no'],
            extracted_data['bank_details']['ifsc_no'],
            extracted_data['freight_term'],
            extracted_data['place_of_supply'],
            extracted_data['buyer_name'],
            extracted_data['buyer_gstin'],
            extracted_data['buyer_pan'],
            extracted_data['freight'],
            timestamp,
            file_name,
            'pass'  # remark
        )
        # print('value : ',value)
        columns = (
            'irn_no', 'ack_no', 'ack_date', 'vendor_name', 'vendor_gstin', 'vendor_pan',
            'msme_no', 'drug_license_no', 'invoice_number', 'eway_bill_no', 'invoice_date', 
            'term_of_payment', 'po_number', 'po_date', 'item_description','item_code', 'item_quantity', 
            'hsn_sac_code', 'tax_rate', 'rate', 'unit', 'amount', 'total_tax', 'rounding_off',
            'total_invoice', 'bank_name', 'account_no', 'ifsc_no', 'freight_term', 
            'place_of_supply', 'buyer_name', 'buyer_gstin', 'buyer_pan', 
            'freight', 'timestamp', 'file_name', 'remark'
        )
        insertExtractedData(columns, value)


"""
The `extractionFun` function processes a file by converting it to base64, extracting data with
retries, checking for specific fields, and preparing the extracted data for a database.

:param file_path: The code you provided seems to be a function for extracting data from a file. It
appears to involve converting the file to base64, extracting data with retries, and then processing
the extracted data further
:return: The function `extractionFun` returns either None or triggers a retry API call based on
certain conditions related to extracted data.
"""

def extractionFun(file_path):
    base64_file = convertBase64Fun(file_path)       #convert to base 64 file
    data = extractDataWithRetriesFun(base64_file)   #retries api calling 

    #key exist or not 'result'
    try:
        data =  data['results'][0] 
    except:
        timestamp = datetime.now()
        file_name = os.path.basename(file_path)
        insertExtractedData(
            ('timestamp', 'file_name', 'remark'),
            (timestamp, file_name, 'fail')
        )
        return
    print('data :',data,"\n\n",len(data),sep='  || ')
    
    # data is none
    if not data:
        timestamp = datetime.now()
        file_name = os.path.basename(file_path)
        insertExtractedData(
            ('timestamp', 'file_name', 'remark'),
            (timestamp, file_name, 'fail')
        )
        return

    extracted_data = extractInvoiceDataFun(data)      #extraction invoice and retrun in dictionary pattern


    print(extracted_data,">>>>\n\n")
    
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
        data = extractDataWithRetriesFun(base64_file)
        data =  data['results'][0]
        if not data:
            timestamp = datetime.now()
            file_name = os.path.basename(file_path)
            insertExtractedData(
                ('timestamp', 'file_name', 'remark'),
                (timestamp, file_name, 'fail')
            )
            return
        
        
    line_items = extractIineItemsFun(data)
    print('line items :',line_items,'\n\n')
    file_name = os.path.basename(file_path)

    prepareDataForDbFun(extracted_data, line_items, file_name)


