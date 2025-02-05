import os
import re
import logging
from datetime import datetime
from API_trigger import convertBase64Fun, apiTriggerFun
from DB_operation import insertExtractedData
from General_function import poNmberDateAndItemcode


# Setup logger
logging.basicConfig(level=logging.INFO)


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
            (timestamp, file_name, 'fail1')
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


    irn_no = data.get('irnNo', '')
    ack_no = data.get('ackNo', '')
    ack_date = data.get('ackDate', '')
    vendor_name = data.get('vendorName', '')
    vendor_gstin = data.get('vendorGSTIN', '')
    vendor_pan = data.get('vendorPAN', '')
    msme_no = data.get('msmeNo', '')
    drug_license_no = data.get('drugLicenseNo', [''])[0] if data.get('drugLicenseNo') else ''
    invoice_number = data.get('invoiceNo', '')
    eway_bill_no = data.get('ewayBillNo', '')
    invoice_date = data.get('invoiceDate', '')
    term_of_payment = data.get('mode/termsOfPayment', '')
    po_number = data.get('purchaseOrderNo', [''])[0] if data.get('purchaseOrderNo') else ''
    po_date = data.get('purchaseOrderDate', [''])[0] if data.get('purchaseOrderDate') else ''
    
    bank_name = data.get('bankDetails', {}).get('bankName', '')
    account_no = data.get('bankDetails', {}).get('accountNo', '')
    ifsc_no = data.get('bankDetails', {}).get('ifscNo', '')
    
    round_off =data.get('roundingOff', '')
    total_invoice =data.get('netPayableAmount', '')
    freight_term = ''
    place_of_supply = data.get('transportDetails', {}).get('placeOfSupply', '')
    buyer_name = data.get('buyerName', '')
    buyer_gstin = data.get('buyerGSTIN', '')
    buyer_pan = data.get('buyerPAN', '')
    freight = ''

    if irn_no =='' or irn_no ==None  or invoice_number =='' or invoice_number ==None  or  invoice_date =='' or invoice_date ==None :
    # we want re-try api triggering
        print(irn_no,invoice_number,invoice_date,eway_bill_no,">>>",sep=' ||  ')
        print('\n\n','yessss','\n\n')
        return 'fail'

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

    for line_data in data.get('invoiceItems', []):
        # print('line daa : ',line_data)
        if line_data == []:
            pass
        description =  line_data.get('description', '')
        quantity =  line_data.get('quantity', '')
        hsn_code =  line_data.get('hsnSac', '')
        tax_rate =  line_data.get('taxableAmount', '')
        rate =  line_data.get('rate', '')
        unit =  line_data.get('uom', '')
        taxable_amount =  line_data.get('taxableAmount', '')
        amount =  line_data.get('totalAmount', '')
        total_tax =  data.get('totalTax', '')

        item_code = line_data.get('itemCode','')
        if not item_code:  # Checks if item_code is None or empty
            item_code = line_data.get('materialCode', '')
        
        timestamp = datetime.now()
        file_name = os.path.basename(file_path)

        if vendor_name.lower() in expected_vendor_list:
            print('condition satasfied >>>>')
            po_number,po_date,item_code = poNmberDateAndItemcode(description,po_number,po_date,item_code)
    
        if place_of_supply == {} or place_of_supply == None:
            place_of_supply = ''


        if amount != None:
            if amount==total_invoice:
                print('matched amount with net payable amount >>>>>>>>')
                amount == taxable_amount

        value = (
            irn_no,ack_no,ack_date,vendor_name,vendor_gstin,vendor_pan,msme_no,drug_license_no,invoice_number,eway_bill_no,invoice_date,term_of_payment,po_number,po_date,description,item_code,quantity,hsn_code,tax_rate,rate,unit,amount,total_tax,round_off,total_invoice,bank_name,account_no,ifsc_no,freight_term,place_of_supply,buyer_name,buyer_gstin,buyer_pan,freight,timestamp,file_name,'pass')
        
        print('value : ',value)
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
    

    return 'success'
