import ocrmypdf
import re
import PyPDF2
import csv
import os
import datetime

now = datetime.datetime.now()
date_time = now.strftime("%d%m%Y %H-%M-%S")
def ocr(file_path, save_path):
    ocrmypdf.ocr(file_path,save_path, skip_text=False)

input_file="D:/OCR-OUTAMATION/BOF Bank.pdf"
input_file_name= os.path.splitext(os.path.basename(input_file))[0]

output_file= 'D:/OCR-OUTAMATION/generated_output/' + input_file_name + 'outfile.pdf'
output_folder="D:/OCR-OUTAMATION/generated_output/" + input_file_name+' '+date_time

if not os.path.exists(output_folder):
    # create folder if it deos not exist
    os.makedirs(output_folder)

# ocr(input_file,output_file)

# Open the PDF file in read-binary mode
with open(output_file, 'rb') as f:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(f)

    # Iterate over each page in the PDF document
    for page_num in range(len(reader.pages)):
        # Get the page object
        page = reader.pages[page_num]

        # Extract the text from the page
        text= page.extract_text()

        # Print the text to the terminal
        print(text)
        
        # print INSTANCES AMOUNT
        IST_AMT = re.findall(r'(Beginning Balance(?:.*\n)*?Ending Balance.*\n)',text,re.MULTILINE | re.IGNORECASE)
        groups = re.findall(r'([a-zA-Z]+\s[\W]*(?:[a-zA-Z]+\s)*)(\d+)*(\s*[-$]*\d*[,.]\d+)*',''.join(IST_AMT))
        
        if IST_AMT:
            print("Match Successful")
            
            for row in groups:
                print(row[0])
                
            # print(type(groups))
            
                path='D:/OCR-OUTAMATION/generated_output/' + input_file_name + '/Checking_Summary++PAGE_' +str(page_num)+ '.csv'
             
            # Open a new CSV file in write mode
                with open(path, 'w', newline='') as csvfile:
    
                # Create a csv.writer object
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(['*LABEL*','*INSTANCE*','*AMOUNT*'])
                        # write each row of  data to the CSV File
                        for row in groups:
                            print(row[0]+row[1]+row[2])
                            csv_writer.writerow([row[0],row[1],row[2]])
                        
        else:
           print("No Match Found")



# match = re.search(pattern, text)    
# if match:
    # matched_string = match.group(1)
    # print(matched_string)
    


# name = re.findall(r'INSTANCES\sAMOUNT\s(?:\r?\n(?:\S|\s)*)*((?:\S|\s)+)\r?\nEnding Balance\s([\d.,]+)', text)
#dob = re.findall(r'(?:\sDate of Birth\W*|:\s)(\d+\/\d+\/\d+)', text)

# print("Name")
#for text_1 in name:
# print(text_1)
#for text_1 in dob:
#    print("Date of Birth")
#    print(text_1)