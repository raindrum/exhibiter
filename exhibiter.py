#!/bin/python

# This is a script to help organize evidence for jury
# documents and discovery responses. If you keep your
# evidence as named pdf, jpg, and png files organized in
# exhibit folders, then you can run this program to generate
# two files:
# 1) a single PDF containing all exhibits, with a cover page
#    before each one; and
# 2) a Word document with a table listing the exhibits and
#    their contents, meant to send to a court or opposing
#    counsel.
# For more info, see README.md.
#
# (C) 2020 Simon Raindrum Sherred ™

import os
import sys
import img2pdf
import texttable
from argparse import ArgumentParser
from pathlib import Path
from re import search, sub
from pdfrw import PdfReader, PdfWriter
from pypandoc import get_pandoc_path, download_pandoc, convert_text
from PIL import Image
from tkinter import filedialog, messagebox, Tk
from pikepdf import _cpphelpers

# -------------------------------------------------------
# Global Variables
# -------------------------------------------------------

# set img2pdf to use US letter size paper (8.5x11")
letter = (img2pdf.mm_to_pt(216),img2pdf.mm_to_pt(279))
img2pdfLayout = img2pdf.get_layout_fun(letter)

# if this file exists in an Exhibit Folder,
# its contents will be written into the exhibit list
disputeFileName = "evidentiary disputes.txt"

# files containing this regex will normally be omitted
omitPattern = "\(UNUSED\)|\(EXCLUDE\)"

# locate asset files 
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    isBundled = True
    assetFolder = Path(sys._MEIPASS) / "assets"
else:
    isBundled = False
    assetFolder = Path(__file__).parent.absolute() / "assets"
coverPages = assetFolder / "cover_pages.pdf"
refDoc = str(assetFolder / "list_style.docx")

# setup temp file (needed for img2pdf)
tempFile = assetFolder / ".tempFile.pdf"

# -------------------------------------------------------
# Classes
# -------------------------------------------------------

class Exhibit:
    def __init__(self, path):
        self.path = path
        filenameSections = path.stem.split(' ', 1)
        self.number = int(filenameSections[0])
        self.name = filenameSections[0]
        self.description = ""
        self.disputes = ""
        self.documents = []
        if len(filenameSections) > 1:
            self.title = sub(omitPattern, "", filenameSections[1]).strip('( )')
            self.name = str(self.number) + ": " + self.title
            self.description += self.title + ":"
        disputeFilePath = path / disputeFileName
        if disputeFilePath.exists():
            self.disputes += disputeFilePath.read_text()
        if not args.nopdf: self.add_cover_sheet()
    
    def add_cover_sheet(self):
        pageNo = self.number - 1
        outPdfWriter.addpage(
            PdfReader(coverPages).pages[pageNo])
    
    def add_document(self, document):
        self.documents.append(document)
        if self.description: self.description += "</p><p>"
        self.description += document.name
    
    def add_to_list(self): 
        global exhList
        exhList.add_row([self.number,"X","",
                         self.description,self.disputes])

class Document:
    def __init__(self, path):
        self.path = path
        self.pagecount = 0
        
        # if name contains an omit tag, hide the tag
        self.name = sub(omitPattern, "", path.stem).strip(' ')
        
        # if name begins with a number, remove it
        if not args.keep_digits:
            self.name = sub("^\d+\. ", "", self.name) 
        
        # if name begins with YYYY-MM-DD, put M/D/YYYY at end
        if search("^\d{4}-\d{2}-\d{2} .+", self.name):
            self.name = (self.name[11:]+" "+
                        self.name[5:7].lstrip('0')+
                        "/"+self.name[8:10].lstrip('0')+
                        "/"+self.name[2:4])
        
        # add whatever file(s) the doc includes
        if path.is_dir():
            for imagePath in sorted(self.path.iterdir()):
                self.add_file(imagePath)
        else: self.add_file(path)
        
        # if doc contains > 1 page, include pagecount
        if self.pagecount > 1:
            self.name += " (" + str(self.pagecount) + ")"
        
    def add_file(self, path):
        if search(omitPattern, path.name) and not includeAll:
            return
        if search(".pdf$", path.name):
            filePdf = PdfReader(path)
        else:
            img = Image.open(path)
            pdf_bytes = img2pdf.convert(
                img.filename,
                layout_fun=img2pdfLayout)
            temp = open(tempFile, "wb")
            temp.write(pdf_bytes)
            img.close()
            temp.close()
            filePdf = PdfReader(tempFile)
        outPdfWriter.addpages(filePdf.pages)
        self.pagecount += len(filePdf.pages)

# -------------------------------------------------------
# Main Process
# -------------------------------------------------------

if tempFile.exists(): tempFile.unlink()

# determine whether program is launched from terminal or GUI
if sys.stdout.isatty(): GUI = False
else: GUI = True

# interpret command-line arguments
p = ArgumentParser(description=
"""This is a script to help arrange evidence for trial docs
and discovery. Before running it, you must organize the input
folder in a specific way. See README.md for more info.""")
p.add_argument("inputfolder",
    help="the root folder containing all exhibits. "+
         "If this is omitted, the program runs in GUI mode",
    action="store",
    nargs='?')
p.add_argument("-o", "--outpdf",
    help="specify where to output pdf "+
         "(defaults to ./Defense Exhibits.pdf)",
    action="store")
p.add_argument("-l", "--outlist",
    help="specify where to output exhibit list docx "+
         "(defaults to ./Defense Exhibit List.docx)",
    action="store")
p.add_argument("-a", "--all",
    help="don't omit files and folders marked "+
    "\"(UNUSED)\" or \"(EXCLUDE)\"",
    action="store_true")
p.add_argument("-g", "--force-gui",
    help="use file pickers even if launched from terminal. "+
         "Input folder must still be specified in command, "+
         "but will be ignored",
    action="store_true")
p.add_argument("-L", "--nolist",
    help="don't create an exhibit list",
    action="store_true")
p.add_argument("-P", "--nopdf",
    help="don't create a pdf of evidence",
    action="store_true")
p.add_argument("-R", "--norebuttal",
    help="don't reserve an additional exhibit for rebuttal",
    action="store_true")
p.add_argument("-p", "--plaintiff",
    help="label as plaintiff list instead of defense",
    action="store_true")
p.add_argument("-n", "--attachno",
    help="specify the attachment number of the exhibit list"+ 
         "(defaults to 4)",
    action="store",
    default="4")
p.add_argument("-k", "--keep-digits",
    help="don't remove leading digits from document names",
    action="store_true")
args = p.parse_args()

# Setup GUI
if args.force_gui or not args.inputfolder: GUI = True
if GUI: Tk().withdraw()

# Open GUI if 
if args.inputfolder: inputFolder = Path(args.inputfolder)
else:
    inputFolder = Path(filedialog.askdirectory(
        title="Select Evidence Folder"))

# setup PDF writer to combine PDF pages
if not args.nopdf: outPdfWriter = PdfWriter()

# setup Pandoc so the script can generate the exhibit list.
# See https://pandoc.org/
if args.nolist: makeList = False
else: 
    makeList = True
    try: get_pandoc_path()
    except OSError:
        installAsk = ("Creating the Exhibit List requires Pandoc, "+
        "a free and open-source document converter. You can install "+
        "it yourself (see https://pandoc.org/installing.html), or "+
        "it can be installed automatically. Automatically install Pandoc?")
        if GUI:
            MsgBox = messagebox.askquestion(installAsk)
            if (MsgBox == 'yes'):
                download_pandoc()
                messagebox.showinfo("Installed Pandoc",
                    "Pandoc has been installed to\n"+
                    get_pandoc_path())
            else:
                messagebox.showwarning(
               	    "Proceeding without Pandoc",
                    "Since Pandoc is not installed, no "+
                    "Exhibit List will be created this time.")
                makeList = False
        else:
            print(installAsk, end='')
            if input(" [y/N]: " == 'y'):
                download_pandoc()
                print("Done installing Pandoc.")
            else:
                print("Since you didn't type \"y\" to install Pandoc, "+
                      "no Exhibit List will be created this time.")
                makeList = False

# whether to omit files marked (UNUSED) and (EXCLUDE)
if args.all: includeAll = True
elif GUI:
    MsgBox = messagebox.askquestion("Use Discovery Mode?",
        "Should the output include evidence that was marked "+
        "(UNUSED) or (EXCLUDE)?")
    includeAll = (MsgBox == 'yes')
else: includeAll = False

# setup markdown table, to which each exhibit will add a row
if args.plaintiff: party = "Plaintiff"
else: party = "Defense"
listHeader ="**Attachment " + args.attachno + ": "
listHeader += party + """ Exhibit List**

### """ + party.upper() + """ EXHIBITS
"""
exhList = texttable.Texttable()
exhList.set_cols_width([5,4,4,41,18])
exhList.header(['**No. **','**ID**','**EV**',
                '**Description**','**Evidentiary Disputes**'])

# process all subfolders in alphabetical order
for exhibitPath in sorted(inputFolder.iterdir()):
    if (not exhibitPath.is_dir() or
        not search("\d+( \(.+\))?", exhibitPath.name) or
        (search(omitPattern, exhibitPath.name) and not includeAll)): continue
    exhibit = Exhibit(exhibitPath)
    print("\nExhibit " + exhibit.name)
    for documentPath in sorted(exhibit.path.iterdir()):
        if (search(omitPattern, documentPath.name) and not includeAll): continue
        if (not documentPath.is_dir() and
            not search(".pdf$|.png$|.jpg$|.jpeg$", documentPath.name)): continue
        document = Document(documentPath)
        exhibit.add_document(document)
        print("  " + document.name)
    if makeList: exhibit.add_to_list()
else:
    if makeList and not args.norebuttal:
        lastExh = str(exhibit.number + 1)
        exhList.add_row([exhibit.number + 1,"X","","Reserved for Rebuttal",""])
        print("\nExhibit "+lastExh+": Reserved for Rebuttal")

# delete tempfile to clean up
if tempFile.exists(): tempFile.unlink()

# set default output folder for GUI
if GUI: outFolder = inputFolder.parent

# make Exhibit List (.docx file)
if makeList:
    print("\nCreating exhibit list ...", end='')
    defaultName = party + " Exhibit List"
    if args.outlist: outListPath = Path(args.outlist)
    elif GUI:
        outListPath = Path(filedialog.asksaveasfilename(
            initialdir = outFolder,
            initialfile = defaultName,
            title = "Save exhibit list as...",
            filetypes = [("Word Document","*.docx")]))
        outFolder = outListPath.parent
    else: outListPath = Path.cwd() / (defaultName+".docx")
    
    # set column justification
    t = exhList.draw().replace("+=","+:").replace("=+",":+",3)

    # make docx from markdown
    convert_text(listHeader + t,'docx','md',
                 outputfile=outListPath.name,
                 extra_args=['--reference-doc='+refDoc])
    
    print(" done.")

# Make Exhibit File (.pdf file)
if not args.nopdf:
    print("\nCreating evidence PDF ...", end='')
    defaultName = party + " Exhibits"
    if args.outpdf: outPdfPath = Path(args.outpdf)
    elif GUI:
        outPdfPath = Path(filedialog.asksaveasfilename(
            initialdir = outFolder,
            initialfile = defaultName,
            title = "Save evidence PDF as...",
            filetypes = [("PDF Document","*.pdf")]))
    else: outPdfPath = Path.cwd() / (defaultName+".pdf") 
    outPdfWriter.write(outPdfPath)
    print(" done.")
