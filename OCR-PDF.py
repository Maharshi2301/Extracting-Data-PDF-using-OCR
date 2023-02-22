import ocrmypdf
import re
import PyPDF2

def ocr(file_path, save_path):
    ocrmypdf.ocr(file_path,save_path, skip_text=False)

text = ""
ocr("Chase Bank.pdf","outfile6.pdf")

# Open the PDF file in read-binary mode
with open('outfile6.pdf', 'rb') as f:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(f)

    # Iterate over each page in the PDF document
    for page_num in range(len(reader.pages)):
        # Get the page object
        page = reader.pages[page_num]

        # Extract the text from the page
        text+= page.extract_text()

        # Print the text to the terminal
        print(text)



pattern = r'((?:INSTANCES\sAMOUNT\s\n)(((\w)+\s)+[\W\d]+\s)+\n)'
match = re.search(pattern, text)


# Extract the data if a match was found
# if match:
    # data = match.group(1)
    # ending_balance = match.group(2)
    
if match:
    matched_string = match.group(1)
    print(matched_string)


# name = re.findall(r'INSTANCES\sAMOUNT\s(?:\r?\n(?:\S|\s)*)*((?:\S|\s)+)\r?\nEnding Balance\s([\d.,]+)', text)
#dob = re.findall(r'(?:\sDate of Birth\W*|:\s)(\d+\/\d+\/\d+)', text)

# print("Name")
#for text_1 in name:
# print(text_1)
#for text_1 in dob:
#    print("Date of Birth")
#    print(text_1)