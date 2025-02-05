import re

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