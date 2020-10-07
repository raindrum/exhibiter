# exhibiter - a Python program for arranging evidence
# copyright 2020 Simon Raindrum Sherred

# python3 standard imports
import os
import sys
from pathlib import Path
from argparse import ArgumentParser
from re import search, sub
from tkinter import Tk
from tkinter.filedialog import askdirectory, asksaveasfilename
from tkinter.messagebox import showwarning, askquestion, showinfo

# third-party imports
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, white
from pypandoc import get_pandoc_path, download_pandoc, convert_text
import texttable
import img2pdf
from PIL import Image

# -------------------------------------------------------
# Launcher
# -------------------------------------------------------

def cli_launch():
    global args, parser
    parser = ArgumentParser(
        description="This is a tool to help arrange "+
        "evidence for trial documents and discovery "+
        "responses. Before using it, you must organize "+
        "the input folder in a specific way. For more "+
        "info, see https://github.com/raindrum/exhibiter.")
    parser.add_argument(
        "inputfolder",
        help="the root folder containing all exhibits. "+
             "This MUST be included except in GUI mode",
        action="store",
        nargs='?')
    parser.add_argument(
        "-g", "--gui",
        help="use graphical interface to select input and "+
        "outputs, and whether to use discovery mode. "+
        "Does not present other options visually, but they "+
        "can be specified in the command along with -g",
        action="store_true")
    parser.add_argument(
        "-d", "--discovery-mode",
        help="don't omit files and folders marked "+
        "\"(UNUSED)\" or \"(EXCLUDE)\". These tags will "+
        "not be displayed in the exhibit list. This mode "+
        "also disables page numbering",
        action="store_true")
    parser.add_argument(
        "-o", "--outpdf",
        help="specify where to output exhibits pdf "+
             "(defaults to ./Defense Exhibits.pdf)",
        action="store")
    parser.add_argument(
        "-l", "--outlist",
        help="specify where to output exhibit list docx "+
             "(defaults to ./Defense Exhibit List.docx)",
        action="store")
    parser.add_argument(
        "-p", "--plaintiff",
        help="label as plaintiff list instead of defense",
        action="store_true")
    parser.add_argument(
        "-k", "--keep-digits",
        help="don't remove leading digits from document names",
        action="store_true")
    parser.add_argument(
        "--nolist",
        help="don't create an exhibit list",
        action="store_true")
    parser.add_argument(
        "--nopdf",
        help="don't create a pdf of evidence",
        action="store_true")
    parser.add_argument(
        "--no-page-counts",
        help="don't append page counts to the "+
             "names of multi-page documents",
        action="store_true")
    parser.add_argument(
        "--no-rebuttal",
        help="don't reserve an additional "+
             "exhibit for rebuttal",
        action="store_true")
    parser.add_argument("--attachno",
        help="specify the attachment number for "+
             "the exhibit list (defaults to 4)",
        action="store",
        default="4")
    args = parser.parse_args()
    main()

# -------------------------------------------------------
# Main Program
# -------------------------------------------------------

def main():
    # perform setup
    if args.gui: Tk().withdraw() # hide blank window
    set_globals()
    setup_pandoc()
    inputFolder = getInputFolder()
    if args.gui:
        answer = askquestion("Use Discovery Mode?",
            "Should the output include evidence that was "+
            "marked (UNUSED) or (EXCLUDE)?")
        args.discovery_mode = (answer == 'yes')
    
    # make exhibits of valid folders
    for x in sorted(inputFolder.iterdir()):
        if not is_exhibit(x): continue
        exhibit = Exhibit(x)
        print("EXHIBIT "+exhibit.name)
        if not args.nopdf: outPdf.addpage(exhibit.coverPage)
        for y in sorted(x.iterdir()):
            if not is_document(y): continue
            document = Document(y, exhibit)
            print("  "+document.list_line())
            exhibit.include(document)
        outList.include(exhibit)
    
    if not args.no_rebuttal: outList.reserve_rebuttal()
    
    if tempFile.exists(): tempFile.unlink()
    
    if args.gui: startFolder = inputFolder.parent
    
    # save outputs
    if not args.nolist:
        print("\nCreating exhibit list ...", end='')
        defaultName = party + " Exhibit List"
        if args.outlist: outListPath = Path(args.outlist)
        elif args.gui:
            outListPath = Path(asksaveasfilename(
                initialdir = startFolder,
                initialfile = defaultName+'.docx',
                title = "Save exhibit list as...",
                filetypes = [("Word Document","*.docx")]))
            startFolder = outListPath.parent
        else: outListPath = Path.cwd() / (defaultName+".docx")
        convert_text(str(outList),'docx','md',
                     outputfile=str(outListPath),
                     extra_args=['--reference-doc='+referenceDoc])
        print(" done.")

    if not args.nopdf:
        print("\nCreating evidence PDF ...", end='')
        defaultName = party + " Exhibits"
        if args.outpdf: outPdfPath = Path(args.outpdf)
        elif args.gui:
            outPdfPath = Path(asksaveasfilename(
                initialdir = startFolder,
                initialfile = defaultName+'.pdf',
                title = "Save evidence PDF as...",
                filetypes = [("PDF Document","*.pdf")]))
        else: outPdfPath = Path.cwd() / (defaultName+".pdf") 
        outPdf.write(outPdfPath)
        print(" done.")

def getInputFolder():
    if args.inputfolder: inputFolder = Path(args.inputfolder)
    elif args.gui:
        print("Please select an input folder.")
        userPick = askdirectoruply(title="Select Evidence Folder")
        if userPick: inputFolder = Path(userPick)
        else: sys.exit()
    else:
        print("\nError: You must specify an input "+
              "folder or else use GUI mode (-g).\n")
        parser.print_help()
        sys.exit()    
    # Check if input folder is valid
    validInput = False
    for folder in inputFolder.iterdir():
        if search("\d+( \(.+\))?", folder.name): validInput = True
    if validInput: return inputFolder
    else:
        error = (
            "This directory doesn't seem to have any "+
            "Exhibit Folders in it. Exhibit folder names "+
            "must be a number, optionally followed by a "+
            "title in parentheses. E.g. \"101 (Rental "+
            "Agreement)\""
        )
        if args.gui: showwarning("Invalid input folder", error)
        else: print(error)
        sys.exit()

# -------------------------------------------------------
# Classes
# -------------------------------------------------------

class ExhibitList:
    def __init__(self):
        self.exhibits=[]
        self.header =(
            "**Attachment "+args.attachno+": "+
            party+" Exhibit List**"+
            "\n\n### "+party.upper()+" EXHIBITS\n")
        self.table = texttable.Texttable()
        self.table.set_cols_width([22,10,10,100,60])
        self.table.header([
            '**No.**',
            '**ID**',
            '**EV**',
            '**Description**',
            '**Evidentiary Disputes**'])
    
    def __str__(self):         
        t = self.table.draw()
        t = t.replace("+=","+:").replace("=+",":+",3)
        return self.header+t
    
    def include(self, exhibit):
        self.exhibits.append(exhibit)
        self.table.add_row(exhibit.listRow())
        
    def reserve_rebuttal(self):
        lastNumber = self.exhibits[-1].number
        if search("[A-Y]", lastNumber):
            nextNumber = ord(lastNumber)
            nextNumber += 1
            nextNumber = chr(nextNumber)
        else: 
            nextNumber = str(int(lastNumber)+1)
        self.table.add_row([
            nextNumber,
            "X",
            "",
            "Reserved for Rebuttal",
            ""
        ])
        print("EXHIBIT "+nextNumber+": Reserved for Rebuttal")


class Exhibit:
    def __init__(self, path):
        self.path = path
        self.pagecount = 0
        filenameSections = path.stem.split(' ', 1)
        self.number = filenameSections[0]
        self.numberColumn = filenameSections[0]
        self.coverPage = self.make_cover_page()
        self.name = filenameSections[0]
        self.description = ""
        self.disputes = ""
        self.documents = []
        self.title = ""
        if len(filenameSections) > 1:
            self.title = sub(omitPattern, "", filenameSections[1]).strip('( )')
            self.name = self.number + ": " + self.title
            self.description += self.title + ":"
        disputeFilePath = path / disputeFileName
        if disputeFilePath.exists():
            self.disputes += disputeFilePath.read_text()

    def make_cover_page(self):
        c = Canvas(str(tempFile), pagesize=letter)
        width, height = letter
        c.setFont("Helvetica",32)
        c.drawCentredString(
            width/2,
            height/7,
            str("EXHIBIT "+self.number))
        c.save()
        return PdfReader(tempFile).pages[0]
    
    def include(self, document):
        self.documents.append(document)
        if self.description: self.description += "</p><p>"
        if not args.discovery_mode:
            self.updateNumberColumn(document)
        self.pagecount += document.pagecount
        self.description += document.list_line()
        
    def updateNumberColumn(self, document):
        num = len(self.documents)
        exh = self.number
        if num == 2:
            if self.title: self.numberColumn+="</p><p>"+exh
            self.numberColumn+="-1"
        if num >= 2:
            self.numberColumn+="</p><p>"
            self.numberColumn+=exh+"-"+str(document.startPage)

    def listRow(self): 
        return [
            self.numberColumn,
            "X",
            "",
            self.description,
            self.disputes
        ]

class Document:
    def __init__(self, path, exhibit):
        self.exhibit = exhibit
        self.path = path
        self.startPage = exhibit.pagecount + 1
        self.pagecount = 0
        self.formatName(path)
        if path.is_dir():
            for x in sorted(path.iterdir()):
                if is_page(x): self.include(x)
        else: self.include(path)

    def __str__(self):
        return self.name
    
    def formatName(self, path):
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

    def include(self, path):
        if search(".pdf$", path.name):
            newPages = PdfReader(path).pages
        else:
            img = Image.open(path)
            pdf_bytes = img2pdf.convert(img.filename,
                                        layout_fun=img2pdfLayout)
            temp = open(tempFile, "wb")
            temp.write(pdf_bytes)
            img.close()
            temp.close()
            newPages = PdfReader(tempFile).pages
        if not args.nopdf:
            for page in newPages:
                self.pagecount += 1
                if not args.discovery_mode:
                    page = self.numbered_page(
                        page,
                        self.pagecount + self.exhibit.pagecount
                    )
                outPdf.addpage(page)
    
    def numbered_page(self, page, num):
        c = Canvas(str(tempFile), pagesize=letter)
        width, height = letter
        c.setFillColor(white)
        midx = width/2
        midy = height/22
        c.rect(
            midx-25,
            midy-4,
            50,
            15,
            stroke=0,
            fill=1)
        c.setFillColor(black)
        c.drawCentredString(
            width/2,
            height/22,
            self.exhibit.number+"-"+str(num))
        c.save()
        numPdf = PdfReader(tempFile)
        numPage = numPdf.pages[0]
        merger = PageMerge(page)
        merger.add(numPage).render()
        return page
        
    def list_line(self):
        if args.no_page_counts or self.pagecount <= 1:
            return self.name
        else: 
            return self.name + " ("+str(self.pagecount)+")"


# -------------------------------------------------------
# Sanity Checks
# -------------------------------------------------------

def is_exhibit(path):
    if not path.is_dir(): return False
    elif not search("(\d+|[A-Y])( \(.+\))?", path.name): return False
    elif (not args.discovery_mode and search(omitPattern, path.name)):
        return False
    else: return True

def is_document(path):
    if (not args.discovery_mode and search(omitPattern, path.name)):
        return False
    elif (not path.is_dir() and
    not search(extensions, path.name)):
        return False
    else: return True
    
def is_page(path):
    if (not args.discovery_mode and search(omitPattern, path.name)):
        return False
    if not search(extensions, path.name):
        return False
    elif (not args.discovery_mode and
    search(omitPattern, path.name)):
        return False
    else: return True

# -------------------------------------------------------
# Setup
# -------------------------------------------------------

def set_globals():
    global referenceDoc, omitPattern, extensions
    global disputeFileName, outPdfWriter, img2pdfLayout, party
    global tempFile, outList, outPdf
    
    # find assets
    assetFolder = Path(__file__).parent.absolute() / "assets" 
    referenceDoc = str(assetFolder / "list_style.docx")
    
    if args.plaintiff: party = "Plaintiff"
    else: party = "Defense"
    
    # if this file exists in an Exhibit Folder,
    # its contents will be written into the exhibit list
    disputeFileName = "evidentiary disputes.txt"
    
    # files that match this pattern can be documents
    # or document parts
    extensions = ".pdf$|.png$|.jpg$|.jpeg$|"+\
                 ".PDF$|.PNG$|.JPG$|.JPEG$"
    
    # files containing this regex will normally be omitted
    omitPattern = "\(UNUSED\)|\(EXCLUDE\)"
    
    # set img2pdf to use US letter size paper (8.5x11")
    letter = (img2pdf.mm_to_pt(216),img2pdf.mm_to_pt(279))
    img2pdfLayout = img2pdf.get_layout_fun(letter)
    
    # setup temp file (needed for img2pdf)
    tempFile = assetFolder / ".tempFile.pdf"
    if tempFile.exists(): tempFile.unlink()
    
    outList = ExhibitList()
    outPdf = PdfWriter()


def setup_pandoc():
    try: get_pandoc_path()
    except OSError:
        installAsk = (
            "Creating the Exhibit List requires Pandoc, "+
            "a free and open-source document converter. "+
            "You can install it yourself (see "+
            "https://pandoc.org/installing.html), or it "+
            "can be installed automatically. "+
            "Automatically install Pandoc?")
        if args.gui:
            answer = askquestion("Install Pandoc?",installAsk)
            if (answer == 'yes'):
                download_pandoc()
                showinfo(
                    "Installed Pandoc",
                    "Pandoc has been installed to\n"+
                    get_pandoc_path())
            else:
                showwarning(
                    "Proceeding without Pandoc",
                    "Since Pandoc is not installed, no "+
                    "Exhibit List will be created.")
                args.nolist = True
        else:
            print(installAsk, end='')
            if input(" [y/N]: ") == 'y':
                download_pandoc()
                print("Done installing Pandoc.")
            else:
                print("Since you didn't type \"y\" to "+
                "install Pandoc, no Exhibit List will be "+
                "created.")
                args.nolist = True
