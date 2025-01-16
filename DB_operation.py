from config import *
import psycopg2
from psycopg2 import OperationalError



def dbConnection():
    
    try:    
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = conn.cursor()
        print('db connected')
        return conn, cursor
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None, None


def insertExtractedData(columns,values):
    conn, cursor = dbConnection()
    if not conn or not cursor:
        return None

    cursor.execute('''CREATE TABLE IF NOT EXISTS demo_lohia5 (
    irn_no TEXT,
    ack_no TEXT,
    ack_date TEXT,
    vendor_name TEXT,
    vendor_gstin TEXT,
    vendor_pan TEXT,
    msme_no TEXT,
    drug_license_no TEXT,
    invoice_number TEXT,
    eway_bill_no TEXT,
    invoice_date TEXT,
    term_of_payment TEXT,
    po_number TEXT,
    po_date TEXT,
    item_description TEXT,
    item_quantity TEXT,
    hsn_sac_code TEXT,
    tax_rate TEXT,
    rate TEXT,
    unit TEXT,
    amount TEXT,
    total_tax TEXT,
    rounding_off TEXT,
    total_invoice TEXT,
    bank_name TEXT,
    account_no TEXT,
    ifsc_no TEXT,
    freight_term TEXT,
    place_of_supply TEXT,
    consignee_name TEXT,
    consignee_gstin TEXT,
    consignee_pan TEXT,
    freight TEXT,
    timestamp TEXT,
    file_name TEXT,
    remark TEXT
)
''');
    conn.commit()
    try:
        col_names = ', '.join(columns)
        value_placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO demo_lohia5 ({col_names}) VALUES ({value_placeholders})"
        cursor.execute(query, values)
        conn.commit() 
        print('inserted')
    except Exception as e:
        print(f"Error: {e}")



# insertExtractedData(
#             ('timestamp', 'file_name', 'remark'),
#             ('timestamp', 'file_name', 'fail')
#         )