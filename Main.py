import os
import logging
import shutil
from Extractioin import extractionFun


def processFilesInDirectoryFun(input_folder,error_folder):
    """
    Process all files in a given folder.
    If an error occurs during processing, move the file to an error folder.
    """
    # error_folder = os.path.join(input_folder, "error_files")
    # os.makedirs(error_folder, exist_ok=True)  # Create error folder if it doesn't exist
    
    

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        # extractionFun(file_path)
        try:
            logging.info(f"Processing file: {file_name}")
            extractionFun(file_path)
            pass_path = os.path.join(pass_folder, file_name)
            shutil.move(file_path, pass_path)
            logging.info(f"Successfully processed file: {file_name}")
        except Exception as e:
            logging.error(f"Error processing file {file_name}: {e}")
            
            # Move the problematic file to the error folder
            error_file_path = os.path.join(error_folder, file_name)
            shutil.move(file_path, error_file_path)
            logging.warning(f"Moved file to error folder: {error_file_path}")
        finally:
            logging.info('-' * 80)


# input_folder = r"C:\Users\rupes\Downloads\akums_ocr\input"
input_folder = r'C:\Users\Admin\Downloads\akums_oce\lohia_new\Invoices'
error_folder = r"C:\Users\Admin\Downloads\akums_oce\lohia_new\error"
pass_folder = r"C:\Users\Admin\Downloads\akums_oce\lohia_new\pass"
processFilesInDirectoryFun(input_folder,error_folder)






