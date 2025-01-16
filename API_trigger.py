import base64
import requests,json


def convertBase64Fun(file):
    file_text = open(file, 'rb')
    file_read = file_text.read()
    file_encode = base64.encodebytes(file_read).decode('utf-8')
 
    # Determine file type and data type accordingly
    if file.lower().endswith('.pdf'):
        data_type = 'data:application/pdf;base64,'
 
    elif file.lower().endswith(('.png')):
        data_type = 'data:image/png;base64,'
 
    elif file.lower().endswith(('.jpeg')):
        data_type = 'data:image/jpeg;base64,'
 
    elif file.lower().endswith(('.jpg')):
        data_type = 'data:image/jpg;base64,'
 
    else:
        raise ValueError('Unsupported file type')
   
    # Add data type before base64 string
    # "file": data_type
    base64_with_data_type = data_type + file_encode
 
    return base64_with_data_type.replace('\n','')

def apiTriggerFun(filebase64):
    sample = {
        "validate": False,
        "settings": {
            "dpi": 300,
            "pages": "1-500",
            "ocr": {
                    "extract": True,
                    "multilingual": False,
                    "fields": { "extract": False, "filter": False, "model": "engine3" },
                    "table": { "extract": True, "include": True, "validate": False, "json": True },
                    "paragraphs": { "json": True },
                    "localization": { "translate": False, "language": "english", "model": "engine3" }
                }
        },
        "file": filebase64
    }
 
    json_data = json.dumps(sample)
   
    try:
        url = "https://sequelprescription.azurewebsites.net/api/invoice?code=MkpvL45PVylhTpWc0Oye6CrXw7G14gdt2R6q4d8xgsqMAzFuRVrr4g%3D%3D"
        response = requests.post(url, data=json_data, headers={"Content-type":"application/json"})
       
        # print(response,"Response generated")
        data = response.json()
        # print(data)
        return data
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the POST request:", e)
        return None
    except json.JSONDecodeError as e:
        print("An error occurred while parsing the JSON response:", e)
        return None  
    except IOError as e:
        print("An error occurred while writing the JSON response to a file:", e)
        return None
    






