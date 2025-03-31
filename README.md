# JPG2PDF
A simple python script that will allow you pick any directory filled with JPGs and it'll turn them into OCR PDFs

It is a simple upload, not even GIT synces, as I figure it was super simple.  If I update it, I may go ahead and sync it.

I banged it out, and I figured somebody else could look at it and use it.

#### How I run it

Under Win11
Under venv @ 3.11.0

#### What does it do?  Why did I make it?

I ran into an issue where somebody in my family only scans documents in JPGs.

When the script is run, you get a dialog box asking you to find a subdirectory.
It scans the subdirectory and allows you to select which files you want to turn into OCR'ed PDFs.

It leaves the original files, and appends ocr_txt to a PDF version of the original file name.

You need OCRmyPDF and Tesseract installed.  I think you also need pageclean installed for OCRmyPDF.


