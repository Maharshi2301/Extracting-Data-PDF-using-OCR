import ocrmypdf
import re
import PyPDF2
import csv
import os
import tkinter as tk
from tkinter import filedialog

################## GLOBAL VARS #################
RUN_CHASE_BANK = 0
RUN_BOA = 0
RUN_AMBOY_BANK = 0
#----------------------------------------------#


################## UTILITY FUNCTIONS #################

def createDifferentModules(d_text, d_page_num):

    global RUN_CHASE_BANK, RUN_BOA, RUN_AMBOY_BANK

    ###################### FIND OUT BANK NAME #####################
    chase_bank = None
    boa_bank = None
    amboy_bank = None
    
    if d_page_num == 0:
        chase_bank = re.findall(r'(Chase Bank)', d_text, re.IGNORECASE)
        if chase_bank: 
            RUN_CHASE_BANK = 1

        boa_bank = re.findall(r'Bank Of America', d_text, re.IGNORECASE)
        if boa_bank: 
            RUN_BOA = 1

        amboy_bank = re.findall(r'Amboy Bank', d_text, re.IGNORECASE)
        if amboy_bank: 
            RUN_AMBOY_BANK = 1

        if (RUN_CHASE_BANK, RUN_BOA, RUN_AMBOY_BANK) == (0,0,0):
            print("\nINPUT PDF does not appear to be BANK STATEMENT\n")

    #-------------------------------------------------------------#
    
    ################### CHASE BANK #####################
    if RUN_CHASE_BANK == 1:

        extract_checkingSummary('chase_bank', d_page_num, d_text) # Extracts all summary part from the text

    #--------------------------------------------------#

    
    ################## BANK OF AMERICA ###################
    if RUN_BOA == 1:

        extract_checkingSummary('boa_bank', d_page_num, d_text) # Extracts all summary part from the text

    #----------------------------------------------------#


    ################# AMBOY BANK ########################
    if RUN_AMBOY_BANK == 1:

        extract_checkingSummary('amboy_bank', d_page_num, d_text) # Extracts all summary part from the text

    #---------------------------------------------------#

def extract_checkingSummary(bankName, d_page_num, d_text):

    SUMMARY = re.findall(r'(Beginning Balance(?:.*\n)*?Ending Balance.*)', d_text, re.MULTILINE | re.IGNORECASE)
    if SUMMARY: 
        print("\nPage No:" + str(d_page_num+1) + "\n")
        for stringObject in SUMMARY:
            print(stringObject)
        print("\n")
        group_checkingSummary(SUMMARY, bankName, d_page_num)
    else:
        print("\n")
        print("NO MATCH FOUND FOR Summary!")
        print("\n")

def group_checkingSummary(d_SUMMARY, bankName, d_page_num):

    if bankName == 'chase_bank':

        GROUPED_SUMMARY = re.findall(r'([a-zA-Z]+\s[\W]*(?:[a-zA-Z]+\s)*)(\d+)*([-\$\s]*[\d]+[.,].*)*',''.join(d_SUMMARY))

        csv_path = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary/Checking_Summary_PAGE_'+str(d_page_num)+'.csv'
        csv_folder = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary'
         # create folder if it doesn't exist
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['**LABELS**', '**INSTANCES**', '**AMOUNT**', '**REMARKS**'])

            if GROUPED_SUMMARY:
                print("\n")
                print("\tGroups created!")
                print("\n")
                SUM=0

                for i, match in enumerate(GROUPED_SUMMARY):

                    AMT_ABSOLUTE_VALUE = re.findall(r'-*\d.*', ''.join(match[2]))

                    AMT_String = ''.join(AMT_ABSOLUTE_VALUE)
                    AMT_String = AMT_String.replace(',','')
                    if i < len(GROUPED_SUMMARY)-1:
                        if AMT_String != '':    
                            SUM += float(AMT_String)
                            SUM = round(SUM,2)
                    print("\t"+match[0]+" "+match[1]+" "+match[2]+"\n\tAbsoluteVal = "+AMT_String+"\tCurrentSum = "+str(float(SUM))+"\n")

                    if i == len(GROUPED_SUMMARY)-1:
                        writer.writerow([match[0], match[1], match[2], "Calculated Sum = " + str(float(SUM))])
                    else:
                        writer.writerow([match[0], match[1], match[2]])

                SUM = float(SUM)
                print("\n\t"+str(SUM))
                print('\n')

                if SUM == float(AMT_String):
                    writer.writerow([""])
                    writer.writerow(["Perfect OCR Generated!"])
                else:
                    writer.writerow([""])
                    writer.writerow(["Imperfect OCR! Manual re-checking required."])

            else:
                print("\n")
                print("NO GROUPS CREATED!")
                print("\n")

    if bankName == 'boa_bank':
        
        GROUPED_SUMMARY = re.findall(r'([a-zA-Z]+\s*(?:[a-zA-Z]*\s)*(?=on|-*\d+,*\d*\.\d+))(on.*?(?=\s\$))*\s*((?:\$|-*)\d+,*\d*.\d+)\s(.*)', ''.join(d_SUMMARY))

        csv_path = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary/Checking_Summary_PAGE_'+str(d_page_num)+'.csv'
        csv_folder = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary'
        # create folder if it doesn't exist
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['**LABELS**', '**DATE**', '**AMOUNT**', '**COMMENTS**', '**REMARKS**'])

            if GROUPED_SUMMARY:

                print("\n")
                print("\tGroups created!")
                print("\n") 
                SUM=0

                for i, match in enumerate(GROUPED_SUMMARY):

                    AMT_ABSOLUTE_VALUE = re.findall(r'-*\d.*', ''.join(match[2]))

                    AMT_String = ''.join(AMT_ABSOLUTE_VALUE)
                    AMT_String = AMT_String.replace(',','')
                    if i < len(GROUPED_SUMMARY)-1:
                        if AMT_String != '':    
                            SUM += float(AMT_String)
                            SUM = round(SUM,2)

                    print("\t"+match[0]+" "+match[1]+" "+match[2].replace('�','-')+" "+match[3]+"\n\tAbsoluteVal = "+AMT_String+"\tCurrentSum = "+str(float(SUM))+"\n")

                    if i == len(GROUPED_SUMMARY)-1:
                        writer.writerow([match[0], match[1], match[2], match[3], "Calculated Sum = " + str(float(SUM))])
                    else:
                        writer.writerow([match[0], match[1], match[2], match[3]])

                SUM = float(SUM)
                print("\n\t"+str(SUM))
                print('\n')

                if SUM == float(AMT_String):
                    writer.writerow([""])
                    writer.writerow(["Perfect OCR Generated!"])
                else:
                    writer.writerow([""])
                    writer.writerow(["Imperfect OCR! Manual re-checking required."])

            else:
                print("\n")
                print("NO GROUPS CREATED!")
                print("\n")
    
    if bankName == 'amboy_bank':
        
        GROUPED_SUMMARY = re.findall(r'([a-zA-Z]+[\W]*(?:[a-zA-Z]+\s*)*)(\|*\s\d+\-+\d+\]*)*([\(\+\-\)\s\-$\s]+\d+[\s,.]\d*.*)',''.join(d_SUMMARY), re.IGNORECASE | re.MULTILINE)

        csv_path = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary/Checking_Summary_PAGE_'+str(d_page_num)+'.csv'
        csv_folder = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/Bank_Summary'
        # create folder if it doesn't exist
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['**LABELS**', '**DATE**', '**AMOUNT**', '**REMARKS**'])

            if GROUPED_SUMMARY:
                print("\n")
                print("\tGroups created!")
                print("\n")
                SUM=0

                for i, match in enumerate(GROUPED_SUMMARY):

                    date = ''.join(match[1]) 
                    if len(date) == 8:
                        date = date[:3] + date[3:5] + '-' + date[5:]
                    
                    AMT_ABSOLUTE_VALUE = re.findall(r'(?:\(([-])\)\s)*\$(\d.+)', ''.join(match[2]))

                    AMT_String = ''.join(AMT_ABSOLUTE_VALUE[0])
                    AMT_String = AMT_String.replace(' ','')

                    if AMT_String[-3] == ',':      
                        AMT_String = AMT_String[:-2]+'.'+AMT_String[-2:]

                    AMT_String = AMT_String.replace(',','')
                    if i < len(GROUPED_SUMMARY)-1:
                        if AMT_String != '':    
                            SUM += float(AMT_String)
                            SUM = round(SUM,2)
                    print("\t"+match[0]+" "+date+" "+match[2]+"\n\tAbsoluteVal = "+AMT_String+"\tCurrentSum = "+str(float(SUM))+"\n")

                    if i == len(GROUPED_SUMMARY)-1:
                        writer.writerow([match[0], date, match[2], "Calculated Sum = " + str(float(SUM))])
                    else:
                        writer.writerow([match[0], date, match[2]])

                SUM = float(SUM)
                print("\n\t"+str(SUM))
                print('\n')

                if SUM == float(AMT_String):
                    writer.writerow([""])
                    writer.writerow(["Perfect OCR Generated!"])
                else:
                    writer.writerow([""])
                    writer.writerow(["Imperfect OCR! Manual re-checking required."])

            else:
                print("\n")
                print("NO GROUPS CREATED!")
                print("\n")

def ocr(file_path, save_path):
    ocrmypdf.ocr(file_path,save_path, skip_text=False)

#------------------------------------------------------#


################# PATHS & VARIABLES ##################
# create the root window
root = tk.Tk()
# root.withdraw()  for hiding the gui display
# root.mainloop()   for keeping up-to-date gui display

input_file = filedialog.askopenfilename(defaultextension='.pdf', title='Select Input File')
# input_file='D:\OCR-OUTAMATION\BOA Bank.pdf'
input_file_name = os.path.splitext(os.path.basename(input_file))[0]

output_file = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+'/output_text.pdf'
output_folder = "D:/OCR-OUTAMATION/generated_output/"+input_file_name
#----------------------------------------------------#


# create folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


################## DRIVING CODE ####################
ocr(input_file, output_file)

#Open the PDF file in read-binary mode
with open(output_file, 'rb') as f:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(f)

    print('\n')
    # Iterate over each page in the PDF document
    for page_num in range(len(reader.pages)):
        # Get the page object
        page = reader.pages[page_num]

        # Extract the text from the page
        text = page.extract_text()
        # Print the text to the terminal
        print(text)
        createDifferentModules(text, page_num)
#--------------------------------------------------#
