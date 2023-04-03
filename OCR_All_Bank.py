import ocrmypdf
import re
import csv
import PyPDF2
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%d%m%Y %H-%M-%S")

CHASE_Bank = 0
AMBOY_Bank = 0
BOA_Bank = 0
TOTAL_SUM = 0
PAGE_END__SUM = 0

def findbank(page_text,on_page_num):

    global CHASE_Bank, AMBOY_Bank, BOA_Bank

    if on_page_num==0:
        chase_bank = re.findall(r'(Chase Bank)',page_text, re.IGNORECASE)
        if chase_bank:
            CHASE_Bank = 1
        amboy_bank = re.findall(r'Amboy Bank',page_text, re.IGNORECASE)
        if amboy_bank:
            AMBOY_Bank = 1 
        boa_bank = re.findall(r'(BANK OF AMERICA)',page_text, re.IGNORECASE)
        if boa_bank:
            BOA_Bank = 1  
    if (CHASE_Bank,AMBOY_Bank,BOA_Bank)==(0,0,0):
        print("INPUT FILE IS NOT A BANK STATEMENT!")

    if CHASE_Bank == 1:
        extractSUMMARY('chase_bank', on_page_num, page_text)
        extractDEPOSITS('chase_bank', on_page_num, page_text)
        extractCHECKS('chase_bank', on_page_num, page_text)
        extractATMWITHDRAWALS('chase_bank', on_page_num, page_text)
    
    if AMBOY_Bank == 1:
        extractSUMMARY('amboy_bank',on_page_num, page_text)
        extractDEPOSITS('amboy_bank', on_page_num, page_text)
    
    if BOA_Bank == 1:
        extractSUMMARY('boa_bank', on_page_num, page_text)
        extractDEPOSITS('boa_bank', on_page_num, page_text)

def extractSUMMARY(bank_name,on_page_num,page_text):
        
        SUMMARY = re.findall(r'Beginning Balance(?:.*\n)*Ending Balance(?:.*)', text, re.MULTILINE | re.IGNORECASE)
        if SUMMARY:
            print("Page-"+str(on_page_num)+": [Y] BANK CHECKING SUMMARY")
            
            groupSUMMARY(SUMMARY,bank_name,on_page_num)
        else:
            print("Page-"+str(on_page_num)+": [X] BANK CHECKING SUMMARY")

def groupSUMMARY(SUMMARY,bank_name,on_page_num):
    
    if bank_name=='chase_bank':
        csvfolderpath = output_folder+'/BANK CHECKING SUMMARY'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'/Checking_Summary_PAGE_'+str(page_num)+'.csv'
        
        GROUPED_SUMMARY = re.findall(r'([a-zA-Z]+\s[\W]*(?:[a-zA-Z]+\s)*)(\d+)*([-\$\s]*[\d]+[.,].*)*',''.join(SUMMARY), re.IGNORECASE)
        
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*TRANSACTION_TYPE*','*INSTANCE*','*AMOUNT*','*REMARKS*'])
            if GROUPED_SUMMARY:
                    SUM = 0;
                    for i,match in enumerate(GROUPED_SUMMARY):
                        AMT_STR = re.findall(r'([-$\s]+\d+[.,]+.*)',''.join(match[2]))
                        AMT_VAL = ''.join(AMT_STR).replace('$','')
                        AMT_VAL = AMT_VAL.replace(' ','')
                        AMT_VAL  = AMT_VAL.replace(',','')
                        
                        #print(AMT_VAL)
                        if i < len(GROUPED_SUMMARY)-1:
                            
                            if AMT_VAL!='':
                                if match[1]== '-':
                                    SUM =SUM - float(AMT_VAL)
                                    SUM = round(SUM,2)
                                else:
                                    SUM = SUM + float(AMT_VAL)
                                    SUM = round(SUM,2)

                        #print("\t"+match[0]+"| "+match[1]+" |"+match[2]+"\n\tAbsoluteVal = "+AMT_VAL+"\tCurrentSum = "+str(float(SUM))+"\n")
                        if i == len(GROUPED_SUMMARY)-1:
                            writer.writerow([match[0], match[1], match[2], "Calculated Sum = " + str(float(SUM))])
                        else:
                            writer.writerow([match[0],match[1],match[2]])
                    
                    SUM = float(SUM)
                    if SUM==float(AMT_VAL):
                        writer.writerow(['OCR SUCCESS!!'])
                    else:
                        writer.writerow(['Manual Check Required!!'])
    
    if bank_name=='amboy_bank':
        csvfilepath = output_folder+'/BANK CHECKING SUMMARY'+'/Checking_Summary_PAGE_'+str(page_num)+'.csv'
        csvfolderpath = output_folder+'/BANK CHECKING SUMMARY'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        
        GROUPED_SUMMARY = re.findall(r'((?:[a-z,|]+\s)+[\]\d-]*)(?:(?:\()*([+-])(?:\)*))*(\s[$]\d+[\s,]+.*)',''.join(SUMMARY), re.IGNORECASE)
        
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*TRANSACTION_TYPE*','*INSTANCE*','*AMOUNT*','*REMARKS*'])
            if GROUPED_SUMMARY:
                    SUM = 0;
                    for i,match in enumerate(GROUPED_SUMMARY):
                        AMT_STR = re.findall(r'([$]+\d+.*)',''.join(match[2]))
                        AMT_VAL = ''.join(AMT_STR).replace('$','')
                        AMT_VAL = AMT_VAL.replace(' ','')
                        if AMT_VAL[-3]==',':
                            AMT_VAL = AMT_VAL[:-2]+'.'+AMT_VAL[-2:]
                        AMT_VAL  = AMT_VAL.replace(',','')
                        
                        print(AMT_VAL)
                        if i < len(GROUPED_SUMMARY)-1:
                            
                            if AMT_VAL!='':
                                if match[1]== '-':
                                    SUM =SUM - float(AMT_VAL)
                                    SUM = round(SUM,2)
                                else:
                                    SUM = SUM + float(AMT_VAL)
                                    SUM = round(SUM,2)

                        print("\t"+match[0]+"| "+match[1]+" |"+match[2]+"\n\tAbsoluteVal = "+AMT_VAL+"\tCurrentSum = "+str(float(SUM))+"\n")
                        if i == len(GROUPED_SUMMARY)-1:
                            writer.writerow([match[0], match[1], match[2], "Calculated Sum = " + str(float(SUM))])
                        else:
                            writer.writerow([match[0],match[1],match[2]])
                    
                    SUM = float(SUM)
                    if SUM==float(AMT_VAL):
                        writer.writerow(['OCR SUCCESS!!'])
                    else:
                        writer.writerow(['Manual Check Required!!'])

    if bank_name=='boa_bank':
        csvfilepath = output_folder+'/BANK CHECKING SUMMARY'+'/Checking_Summary_PAGE_'+str(page_num)+'.csv'
        csvfolderpath = output_folder+'/BANK CHECKING SUMMARY'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        
        GROUPED_SUMMARY = re.findall(r'([a-zA-Z]+\s*(?:[a-zA-Z]*\s)*(?=on|-*\d+,*\d*\.\d+))(on.*?(?=\s\$))*\s*((?:\$|-*)\d+,*\d*.\d+)\s(.*)',''.join(SUMMARY), re.IGNORECASE)
        
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['**LABELS**', '**DATE**', '**AMOUNT**', '**COMMENTS**' , '**REMARKS**'])
            if GROUPED_SUMMARY:
                    SUM = 0;
                    for i,match in enumerate(GROUPED_SUMMARY):
                        AMT_STR = re.findall(r'-*\d.*',''.join(match[2]))
                        AMT_VAL = ''.join(AMT_STR)
                        AMT_VAL  = AMT_VAL.replace(',','')
                        #print(AMT_VAL)
                        if i < len(GROUPED_SUMMARY)-1:
                            if AMT_VAL!='':
                                SUM = SUM + float(AMT_VAL)
                                SUM = round(SUM,2)

                        #print("\t"+match[0]+"| "+match[1]+" |"+match[2]+" |"+match[3]+"\n\tAbsoluteVal = "+AMT_VAL+"\tCurrentSum = "+str(float(SUM))+"\n")
                        if i == len(GROUPED_SUMMARY)-1:
                            writer.writerow([match[0], match[1], match[2], match[3], "Calculated Sum = " + str(float(SUM))])
                        else:
                            writer.writerow([match[0],match[1],match[2],match[3]])
                    
                    SUM = float(SUM)
                    if SUM==float(AMT_VAL):
                        writer.writerow(['OCR SUCCESS!!'])
                    else:
                        writer.writerow(['Manual Check Required!!'])

def extractDEPOSITS(bank_name, on_page_num, page_text):

    if bank_name=='chase_bank':
        DEPOSITS_GROUP = re.findall(r'(DEPOSITS AND ADDITIONS(?:.*\n)*?Total Deposits and Additions.*)', text, re.MULTILINE)
        DEPOSIT = re.findall(r'^\d(?:.*\n)*?Total Deposits and Additions.*', ''.join(DEPOSITS_GROUP), re.MULTILINE)
        if DEPOSIT:
            print("Page-"+str(on_page_num)+": [Y] DEPOSIT")
            groupDEPOSIT(DEPOSIT,bank_name,on_page_num)

        else:
            print("Page-"+str(on_page_num)+": [X] DEPOSIT")
            TOTAL_SUM=0
            PAGE_END__SUM=0

    if bank_name=='boa_bank':
        DEPOSIT = re.findall(r'Deposits and other credits(?!\s\d)(?:.*\n)*', text, re.MULTILINE)
        if DEPOSIT:
            print("Page-"+str(on_page_num)+": [Y] DEPOSIT")
            groupDEPOSIT(DEPOSIT,bank_name,on_page_num)

        else:
            print("Page-"+str(on_page_num)+": [X] DEPOSIT")
    
    if bank_name=='amboy_bank':
        DEPOSIT = re.findall(r'De\s?posits and Other Cre\s?dits\s?(?:.*\n)*', text, re.MULTILINE)
        if DEPOSIT:
            print("Page-"+str(on_page_num)+": [Y] DEPOSIT")
            groupDEPOSIT(DEPOSIT,bank_name,on_page_num)

        else:
            print("Page-"+str(on_page_num)+": [X] DEPOSIT")

def groupDEPOSIT(DEPOSIT, bank_name,on_page_num):
    
    global TOTAL_SUM, PAGE_END__SUM

    if bank_name=='chase_bank':
        csvfolderpath = output_folder+'/DEPOSITS & ADDITIONS'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'/DEPOSITS_AND_ADDITIONS_PAGE_'+str(page_num)+'.csv'
        
        GROUPED_DEPOSIT = re.findall(r'(\d+\/\d+\s|)(.*?(?=\$*\d+,*\d*\.\d+))(\$*\d+,*\d*\.\d+)(\s+Temple GA(?:.*\n){3}.*)*', ''.join(DEPOSIT), re.MULTILINE)
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*DATE*','*DESCRIPTION*','*AMOUNT*','*REMARKS*'])
            if GROUPED_DEPOSIT:
                TOTAL_SUM=0
                for i, match in enumerate(GROUPED_DEPOSIT):
                    DEPOSIT_AMT = re.findall(r'(\$?\d+[,.]\d+[,.]*\d+)', ''.join(match[2]))
                    CURRENT_AMT = ''.join(DEPOSIT_AMT).replace('$','')
                    CURRENT_AMT = CURRENT_AMT.replace(',','')
                    #print(CURRENT_AMT)
                    if i<len(GROUPED_DEPOSIT)-1:
                        TOTAL_SUM+=float(CURRENT_AMT)
                        TOTAL_SUM=round(TOTAL_SUM,2)
                        writer.writerow([match[0],match[1]+match[3],match[2]])
                    if i==len(GROUPED_DEPOSIT)-1:
                        writer.writerow([match[0],match[1]+match[3],match[2],'Total Sum = '+str(TOTAL_SUM)])
                        if float(TOTAL_SUM)!=float(CURRENT_AMT):
                            writer.writerow(['MANUAL CHECKING REQUIRED!!'])
                            TOTAL_SUM=0
                        else:
                            writer.writerow(['OCR SUCCESS!!'])
                            TOTAL_SUM=0

    if bank_name=='boa_bank':
        csvfolderpath = output_folder+'/DEPOSITS & ADDITIONS'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'/DEPOSITS_AND_ADDITIONS_PAGE_'+str(page_num)+'.csv'
        GROUPED_DEPOSIT = re.findall(r'(\d+[/]\d+[/]\d+\s(?!CHECKCARD)|Total)(.*?(?=\s\$?\d+,*\d*\.\d+))(\s\$?\d+,*\d*\.\d+)(\s*[\d]*ID(?:.*\n)|DONUTS(?:.*\n))*(\s*[\d]*CO(?:.*\n))*', ''.join(DEPOSIT), re.MULTILINE)
        
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*DATE*','*DESCRIPTION*','*AMOUNT*','*REMARKS*'])
            if GROUPED_DEPOSIT:
                for i, match in enumerate(GROUPED_DEPOSIT):
                    DEPOSIT_AMT = re.findall(r'(\s\$?\d+,*\d*\.\d+)', ''.join(match[2]))
                    CURRENT_AMT = ''.join(DEPOSIT_AMT).replace('$','')
                    CURRENT_AMT = CURRENT_AMT.replace(',','')
                    if i<len(GROUPED_DEPOSIT)-1:
                        TOTAL_SUM+=float(CURRENT_AMT)
                        TOTAL_SUM=round(TOTAL_SUM,2)
                        writer.writerow([match[0], match[1]+''.join(match[3])+''.join(match[4]), match[2],"CurrentVal = "+CURRENT_AMT,"TotalSum = "+str(TOTAL_SUM)])
                    if i==len(GROUPED_DEPOSIT)-1:
                        PAGE_END = re.findall(r'(Total deposits and other credits)',''.join(DEPOSIT), re.MULTILINE)
                        if PAGE_END:
                            #TOTAL_SUM+=float(CURRENT_AMT)
                            TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1]+''.join(match[3])+''.join(match[4]), match[2],"TotalSum = "+str(TOTAL_SUM),"PageEndSum = "+str(PAGE_END__SUM)])

                            if float(TOTAL_SUM)!=float(CURRENT_AMT):
                                writer.writerow(['MANUAL CHECKING REQUIRED!!'])
                                TOTAL_SUM = 0
                            else:
                                writer.writerow(['OCR SUCCESS!!'])
                                TOTAL_SUM = 0

                            PAGE_END__SUM = 0    
                        else:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            PAGE_END__SUM += float(TOTAL_SUM)
                            PAGE_END__SUM = round(PAGE_END__SUM,2)
                            writer.writerow([match[0], match[1]+''.join(match[3])+''.join(match[4]), match[2],"CurrentVal = "+CURRENT_AMT,"TotalSum = "+str(TOTAL_SUM)])
                            TOTAL_SUM = 0
            else:
                print('Page-'+str(page_num)+': NO MATCH FOUND!')

    if bank_name=='amboy_bank':
        csvfolderpath = output_folder+'/DEPOSITS & ADDITIONS'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'/DEPOSITS_AND_ADDITIONS_PAGE_'+str(page_num)+'.csv'
        print('Page-'+str(page_num)+': MATCH FOUND!')
        FIND_CHECKS = re.findall(r'Checks',''.join(DEPOSIT), re.MULTILINE)
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*DATE*','*DESCRIPTION*','*AMOUNT*','*REMARKS*'])
            if FIND_CHECKS:
                DEPOSIT_ON_CHECKS = re.findall(r'(De\s?posits and Other Cre\s?dits \(cont.\)(?:.*\n)*(?=Checks))',''.join(DEPOSIT), re.MULTILINE)
                if DEPOSIT_ON_CHECKS:
                    GROUPED_DEPOSIT_ON_CHECKS = re.findall(r'(\d{2}\-\d{2})\s(.*?(?=\s\$?\d+,*\d*\.\,?\d+))\s(\$?\d+,*\d*\.\,?\d+)', ''.join(DEPOSIT_ON_CHECKS), re.MULTILINE)
                    for i, match in enumerate(GROUPED_DEPOSIT_ON_CHECKS):
                        DEPOSIT_AMT = re.findall(r'(\$?\d+,*\d*\.\,?\d+)', ''.join(match[2]))
                        CURRENT_AMT = ''.join(DEPOSIT_AMT).replace('$','')
                        if CURRENT_AMT[-3]==',':
                            CURRENT_AMT = CURRENT_AMT[:-2]+'.'+CURRENT_AMT[-2:]
                        CURRENT_AMT = CURRENT_AMT.replace(',','')
                        if i<len(GROUPED_DEPOSIT_ON_CHECKS)-1:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            #TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1], match[2], "CurrentAmt: "+CURRENT_AMT, "TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                        if i==len(GROUPED_DEPOSIT_ON_CHECKS)-1:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1], match[2], "CurrentAmt: "+CURRENT_AMT, "TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                            TOTAL_SUM = 0
                            PAGE_END__SUM = 0

            else:
                    GROUPED_DEPOSIT = re.findall(r'(\d{2}\-\d{2})\s(.*?(?=\s\$?\d+,*\d*\.\,?\d+))\s(\$?\d+,*\d*\.\,?\d+)', ''.join(DEPOSIT), re.MULTILINE)
                    for i, match in enumerate(GROUPED_DEPOSIT):
                        DEPOSIT_AMT = re.findall(r'(\$?\d+,*\d*\.\,?\d+)', ''.join(match[2]))
                        CURRENT_AMT = ''.join(DEPOSIT_AMT).replace('$','5')
                        CURRENT_AMT = CURRENT_AMT.replace(' ','')
                        if CURRENT_AMT[-3]==',':
                            CURRENT_AMT = CURRENT_AMT[:-2]+'.'+CURRENT_AMT[-2:]
                        CURRENT_AMT = CURRENT_AMT.replace(',','')
                        if i<len(GROUPED_DEPOSIT)-1:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1], match[2], "CurrentAmt: "+str(CURRENT_AMT), "TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                        if i==len(GROUPED_DEPOSIT)-1:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            PAGE_END__SUM += float(TOTAL_SUM)
                            PAGE_END__SUM = round(PAGE_END__SUM,2)
                            writer.writerow([match[0], match[1], match[2], "CurrentAmt: "+str(CURRENT_AMT), "TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                            TOTAL_SUM = 0

def extractCHECKS(bank_name, on_page_num, page_text):
    if bank_name=='chase_bank':
        CHECKS = re.findall(r'CHECKS PAID(?:.*\n)*', text, re.MULTILINE)
        if CHECKS:
            print("Page-"+str(on_page_num)+": [Y] CHECKS")
            groupCHECKS(CHECKS,bank_name,on_page_num)
        else:
            print("Page-"+str(on_page_num)+': [X] CHECKS')
            TOTAL_SUM=0
            PAGE_END__SUM=0

def groupCHECKS(CHECKS, bank_name, on_page_num):
    
    global TOTAL_SUM, PAGE_END__SUM

    if bank_name=='chase_bank':
        csvfolderpath = output_folder+'\CHECKS PAID'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'\CHECKS PAID_PAGE_'+str(page_num)+'.csv'
        FIND_TOTAL_CHECKS = re.findall(r'Total Checks Paid',''.join(CHECKS), re.MULTILINE)
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*CHECK NO*','*DESCRIPTION*','*PAID ON*','*AMOUNT*','*REMARKS*'])
            if FIND_TOTAL_CHECKS:
                    DEPOSIT_IN_CHECKS = re.findall(r'CHECKS PAID(?:.*\n)*?Total Checks Paid.*',''.join(CHECKS), re.MULTILINE)
                    if DEPOSIT_IN_CHECKS:
                        GROUPED_DEPOSIT_IN_CHECKS = re.findall(r'(\d+\s[*“\w\d]*|Total)(.*(?=\d{2}\/\d{2})*|Checks)\s(\d{2}\/\d{2}|Paid)\s(\$?\d+[.,]*\d*[.]\d+)', ''.join(DEPOSIT_IN_CHECKS), re.MULTILINE)
                        for i, match in enumerate(GROUPED_DEPOSIT_IN_CHECKS):
                            CHECKS_AMT = re.findall(r'(\$?\d+[.,]*\d*[.]\d+)', ''.join(match[3]))
                            CURRENT_AMT = ''.join(CHECKS_AMT).replace('$','')
                            CURRENT_AMT = CURRENT_AMT.replace(',','')
                            #print(CURRENT_AMT)
                            if i<len(GROUPED_DEPOSIT_IN_CHECKS)-1:
                                TOTAL_SUM+=float(CURRENT_AMT)
                                #TOTAL_SUM+=float(PAGE_END__SUM)
                                TOTAL_SUM=round(TOTAL_SUM,2)
                                writer.writerow([match[0], match[1], match[2], match[3] ,"TotalAmt: "+str(TOTAL_SUM),"PageEndAmt: "+str(PAGE_END__SUM)])
                            if i==len(GROUPED_DEPOSIT_IN_CHECKS)-1:
                                #TOTAL_SUM+=float(CURRENT_AMT)
                                TOTAL_SUM+=float(PAGE_END__SUM)
                                TOTAL_SUM=round(TOTAL_SUM,2)
                                writer.writerow([match[0], match[1], match[2], match[3],"TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                                if float(TOTAL_SUM)==float(CURRENT_AMT):
                                    writer.writerow(['OCR SUCCESS!'])
                                    TOTAL_SUM = 0
                                    PAGE_END__SUM = 0
                                else:
                                    writer.writerow(['MANUAL RECHECKING REQUIRED!'])
                                    TOTAL_SUM = 0
                                    PAGE_END__SUM = 0
                                

            else:
                        GROUPED_CHECKS = re.findall(r'(\d+\s[*“\w\d]*|Total|)(.*(?=\d{2}\/\d{2})*|Checks)\s(\d{2}\/\d{2}|Paid)\s(\$?\d+[.,]*\d*[.]\d+)', ''.join(CHECKS), re.MULTILINE)
                        for i, match in enumerate(GROUPED_CHECKS):
                            CHECKS_AMT = re.findall(r'(\$?\d+[.,]*\d*[.]\d+)', ''.join(match[3]))
                            CURRENT_AMT = ''.join(CHECKS_AMT).replace('$','')
                            #CURRENT_AMT = CURRENT_AMT.replace(' ','')
                            CURRENT_AMT = CURRENT_AMT.replace(',','')
                            if i<len(GROUPED_CHECKS)-1:
                                TOTAL_SUM+=float(CURRENT_AMT)
                                #TOTAL_SUM+=float(PAGE_END__SUM)
                                TOTAL_SUM=round(TOTAL_SUM,2)
                                writer.writerow([match[0], match[1], match[2], match[3],"TotalAmt: "+str(TOTAL_SUM), "PageEndAmt: "+str(PAGE_END__SUM)])
                            if i==len(GROUPED_CHECKS)-1:
                                TOTAL_SUM+=float(CURRENT_AMT)
                                PAGE_END__SUM += float(TOTAL_SUM)
                                PAGE_END__SUM = round(PAGE_END__SUM,2)
                                writer.writerow([match[0], match[1], match[2], match[3],"TotalAmt: "+str(TOTAL_SUM),"PageEndAmt: "+str(PAGE_END__SUM)])
                                TOTAL_SUM = 0

def extractATMWITHDRAWALS(bank_name, on_page_num, page_text):

    if bank_name=='chase_bank':
        ATM = re.findall(r'\|?ATM & DEBIT CARD WITHDRAWALS\|?(?:.*\n)*', text, re.MULTILINE)
        if ATM:
            print("Page-"+str(on_page_num)+": [Y] ATM & DEBIT CARD WITHDRAWALS\n")
            groupATMWITHDRAWALS(ATM,bank_name,on_page_num)
        else:
            print("Page-"+str(on_page_num)+': [X] ATM & DEBIT CARD WITHDRAWALS\n')
            TOTAL_SUM=0
            PAGE_END__SUM=0

def groupATMWITHDRAWALS(ATM, bank_name, on_page_num):

    global TOTAL_SUM, PAGE_END__SUM

    if bank_name=='chase_bank':
        csvfolderpath = output_folder+'\ATM & DEBIT CARD WITHDRAWALS'
        if not os.path.exists(csvfolderpath):
            # create folder if it doesn't exist
            os.makedirs(csvfolderpath)
        csvfilepath = csvfolderpath+'\ATM & DEBIT CARD WITHDRAWALS_PAGE_'+str(page_num)+'.csv'
        FIND_TOTAL_WITHDRAWALS = re.findall(r'Total ATM & Debit Card Withdrawals',''.join(ATM), re.MULTILINE)
        with open(csvfilepath,'w', newline='') as csv_file:
        # Create a CSV writer object
            writer = csv.writer(csv_file)
            writer.writerow(['*DATE*','*DESCRIPTION*','*AMOUNT*','*REMARKS*'])
            if FIND_TOTAL_WITHDRAWALS:
                ATM_WITHDRAWALS = re.findall(r'\|ATM & DEBIT CARD WITHDRAWALS \|(?:.*\n)*?Total ATM & Debit Card Withdrawals.*',''.join(ATM), re.MULTILINE)
                if ATM_WITHDRAWALS:
                    GROUPED_ATM_WITHDRAWALS = re.findall(r'(\d+\/\d+|Total ATM & Debit Card Withdrawals)\s(.*\d{4})?(.*)(\s*Purchase.*)*', ''.join(ATM_WITHDRAWALS), re.MULTILINE)
                    for i, match in enumerate(GROUPED_ATM_WITHDRAWALS):
                        CHECKS_AMT = re.findall(r'(\d+[.,]\s?[^A-Z].*|\d{2,}\s\d{2}$)', ''.join(match[2]))
                        CURRENT_AMT = ''.join(CHECKS_AMT).replace('$','')
                        CURRENT_AMT = CURRENT_AMT.replace(',','')
                        if CHECKS_AMT == re.findall(r'(\d{2,}\s\d{2}$)', ''.join(match[2])):
                            CURRENT_AMT = CURRENT_AMT.replace(' ','.')
                        #print(CURRENT_AMT)
                        if i<len(GROUPED_ATM_WITHDRAWALS)-1 and CURRENT_AMT!='':
                            TOTAL_SUM+=float(CURRENT_AMT)
                            #TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1]+match[3], match[2]])
                        if i==len(GROUPED_ATM_WITHDRAWALS)-1:
                            #TOTAL_SUM+=float(CURRENT_AMT)
                            TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1]+match[3], match[2],"\tTotalAmt: "+str(TOTAL_SUM)+"\tPageEndAmt: "+str(PAGE_END__SUM)])
                            if float(TOTAL_SUM)==float(CURRENT_AMT):
                                writer.writerow(['OCR SUCCESS!'])
                            else:
                                writer.writerow(['MANUAL RECHECKING REQUIRED!'])
                            TOTAL_SUM = 0
                            PAGE_END__SUM = 0


            else:
                    GROUPED_ATM_WITHDRAWALS = re.findall(r'(\d+\/\d+|Total ATM & Debit Card Withdrawals)\s(.*\d{4})?(.*)(\s*Purchase.*)*', ''.join(ATM), re.MULTILINE)
                    for i, match in enumerate(GROUPED_ATM_WITHDRAWALS):
                        CHECKS_AMT = re.findall(r'(\d+[.,]\s?[^A-Z].*|\d{2,}\s\d{2}$)', ''.join(match[2]))
                        CURRENT_AMT = ''.join(CHECKS_AMT).replace('$','')
                        #CURRENT_AMT = CURRENT_AMT.replace(' ','')
                        CURRENT_AMT = CURRENT_AMT.replace(',','')
                        #if CURRENT_AMT[-3]==' ':
                        #    CURRENT_AMT = CURRENT_AMT[:-2]+'.'+CURRENT_AMT[-2:]
                        if i<len(GROUPED_ATM_WITHDRAWALS)-1 and CURRENT_AMT!='':
                            TOTAL_SUM+=float(CURRENT_AMT)
                            #TOTAL_SUM+=float(PAGE_END__SUM)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            writer.writerow([match[0], match[1]+match[3], match[2]])
                        if i==len(GROUPED_ATM_WITHDRAWALS)-1:
                            TOTAL_SUM+=float(CURRENT_AMT)
                            TOTAL_SUM=round(TOTAL_SUM,2)
                            PAGE_END__SUM += float(TOTAL_SUM)
                            PAGE_END__SUM = round(PAGE_END__SUM,2)
                            writer.writerow([match[0], match[1]+match[3], match[2],"\tTotalAmt: "+str(TOTAL_SUM)+"\tPageEndAmt: "+str(PAGE_END__SUM)])
                            TOTAL_SUM = 0
 

def ocr(file_path, save_path):
    ocrmypdf.ocr(file_path,save_path, skip_text=False)

root = tk.Tk()
root.withdraw()

input_file = filedialog.askopenfilename(defaultextension='.pdf', title='Select Input File')
input_file_name = os.path.splitext(os.path.basename(input_file))[0]
print(input_file_name)
global output_folder
output_folder = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+' - '+dt_string
output_file = 'D:/OCR-OUTAMATION/generated_output/'+input_file_name+' output_text.pdf'


if not os.path.exists(output_folder):
    # create folder if it doesn't exist
    os.makedirs(output_folder)

#Perform OCR on the PDF File

ocr(input_file, output_file)

with open(output_file, 'rb') as f:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(f)
    
    # Iterate over each page in the PDF document
    for page_num in range(len(reader.pages)):
        
        # Get the page object
        page = reader.pages[page_num]

        # Extract the text from the page
        text = page.extract_text()

        # Print the OCR text to the terminal
        #print(text)

        #find bank
        findbank(text,page_num)

########################################################################################
#Chase Bank
#SUMMARY RE: (Beginning Balance(?:.*\n)*?Ending Balance.*)
#GROUP SUMMARY RE: ([a-zA-Z]+\s[\W]*(?:[a-zA-Z]+\s)*)(\d+)*([-\$\s]*[\d]+[.,].*)*
#AMT_STR RE: [-$\s]+\d+[.,]+.*
########################################################################################
########################################################################################
#Amboy Bank
#SUMMARY RE: Beginning Balance(?:.*\n)*Ending Balance(?:.*)
#GROUP SUMMARY RE: ((?:[a-z,]+\s)+[\d-]*)(?:\(([+-])\))*(\s[$]\d+[\s,]+.*)
#AMT_STR RE: ([$]\d+[\s,]+.*)
########################################################################################
########################################################################################
#BOF Bank
#SUMMARY RE: 
#GROUP SUMMARY RE: 
########################################################################################