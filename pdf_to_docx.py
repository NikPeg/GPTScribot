from pdf2docx import Converter

name = input("Enter filename:\n")
cv = Converter(name)
cv.convert(name[:-4] + ".docx", start=0, end=None)
cv.close()
