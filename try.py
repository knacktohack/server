from PyPDF2 import PdfReader

reader = PdfReader("out/demo.pdf")

text = ""
for page in reader.pages:
  text += page.extract_text() + "\n"

print(text)