This is a tool to help organize evidence for litigation. If you keep your evidence as named pdf, jpg, and png files in numbered exhibit folders, the program can automatically generate an exhibit list and PDF suitable for jury documents and discovery responses.

I made this tool in the hopes that it would make eviction defense a little easier. Plaintiffs may use it as well, but *eviction plaintiffs* and their representatives may not. 

Copyright 2020 Simon Raindrum Sherred.

# Installation

## Easy

Go to the Releases page and download the version for your operating system. Save it wherever it will be convenient for you to access.

When you first run the program, it will ask to install [Pandoc](https://pandoc.org/) if it is not already installed.

## Advanced

Alternatively, if you have [Python 3.8](https://www.python.org/downloads/) or higher and you want the program in script form, just download `exhibiter.py` and the `assets` folder and place them in the same directory. Use Python to run `exhibiter.py`, and then install any missing modules with [pip](https://pypi.org/project/pip/). 

If you need to compile a version that isn't in the Releases page, run [pyinstaller](https://pypi.org/project/pyinstaller/) on the included `exhibiter.spec`.

# Usage

## 1. Organize your Files First

For the script to run correctly, all your evidence for the case must be organized in a specific way. This organizational structure is meant to be intuitive, but it still needs a little explanation.

The Evidence Folder is the main folder that you want the program to process. It does not matter where this folder is, or what it is named; you will just need to tell the program where it is.

### 1.1. Put Exhibits in the Evidence Folder

The Evidence Folder must contain one or more Exhibit Folders, whose names must be a number (corresponding to their exhibit number), plus optionally a title and an EXCLUDE flag, each of which should be in parentheses.

- Exhibit numbers must be between 1 and 200.[^1]
- If present, the title will be added at the beginning of the Exhibit's description in the Exhibit List.[^2]
- If the EXCLUDE flag is present, then the exhibit will be omitted unless the program is launched from a command line with the `-a` or `--all` option.[^3]

An example Evidence Folder might contain a set of Exhibit Folders with the following names:

> - **101**
> - **102**
> - **103 (Written Communication Between the Parties)**
> - **104 (Photographs of the Interior) (EXCLUDE)**
> - **105 (EXCLUDE)**

### 1.2. Put Documents in each Exhibit

Each Exhibit Folder must contain one or more Documents, which will be arranged alphabetically. A Document can be one of three things:

1. a PDF,
2. an image file (specifically .png, .jpg, or .jpeg), or
3. a folder full of image files.

Every Document has a name that will appear in the Exhibit List. The name is determined based on the Document's file name.[^4] The program reads a file name and performs several steps in processing it:

1. If the Document's name contains an EXCLUDE tag (in parentheses), the document will be omitted unless the program is run with the `-a` or `--all` option.
2. If the Document's name begins with a number followed by a period and a space (e.g. "01. Welcome Note.pdf"), that part will be omitted. This is so you can use numbers to manually organize the files if the automatic organizing is not ideal.[^5]
3. If the Document's name begins with a date in YYYY-MM-DD format (e.g. 1995-01-09), this will be moved to the end of the name in M/D/YY format. It is recommended that you use YYYY-MM-DD date format for every Document that has a relevant date.[^6]

Some Exhibits may have evidentiary issues, like being admissible only for certain purposes, which should be noted in the Exhibit List. You can make these notes by creating a text file called `evidentiary disputes.txt` in the relevant Exhibit Folder. If this file is present, its contents will be written into the Evidentiary Disputes column of the Exhibit List.

An example Exhibit Folder might contain the following set of Documents:

> - **2020-01-03 **

### 2. Run the Program

If you installed a compiled version of the program, you should be able to run it by double-clicking it. The  program will then walk you through the process. On some platforms, you can also launch the program by dragging an Evidence Folder onto it.

Alternatively, the program also be run from a command line, where it is possible to specify various advanced options. These features are documented in the program itself, and can be accessed by running it with the `-h` option.

[^1]: If you need more exhibits than this, or want to customize the appearance of the cover sheets, you will need to modify ```assets/cover_pages.pdf```, included inside the program.
[^2]:  I don't recommend providing titles for Exhibits that contain only one Document, because in that case the Document name makes a title redundant.
[^3]:  The EXCLUDE flag is intended for indicating files that will not be presented at trial, but which must be included in discovery responses.
[^4]: Note that if a Document is a folder of images rather than a single file, the document name comes from the name of the folder. The images inside will be arranged in alphabetical order, and their file names will otherwise be ignored.
[^5]: To prevent the program from stripping these digits, you can run it from a command line with the `-k` or `--keep-digits` option enabled.
[^6]:  YYYY-MM-DD dates are useful because the program arranges documents alphabetically, and in this format chronological and alphabetical order are identical. Do not omit leading zeros; January 9, 1995 should be written as 1995-01-09.