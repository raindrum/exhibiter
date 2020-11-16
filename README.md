![icon](https://raw.githubusercontent.com/raindrum/exhibiter/master/icon.svg)

This is a tool to help organize evidence for litigation. If you keep your evidence as named pdf, jpg, and png files in numbered exhibit folders, the program can automatically generate an exhibit list (.docx) and a PDF of all evidence (with exhibit dividers), suitable for jury documents and discovery responses.

I made this tool in the hopes that it would make eviction defense a little easier. Plaintiffs may use it as well, but *eviction plaintiffs* and their representatives may not. 

Copyright (c) 2020 Simon Raindrum Sherred.

# Installation

Exhibiter requires Python 3.8 or higher to run. [Here is the link to install it](https://www.python.org/downloads/), if needed. If you use Windows, make sure to choose the installer options to add Python to your PATH, and to disable Windows' 260-character path limit.

Once you have Python, you can install the program from a command prompt. On Windows, that's the `cmd` application; on MacOS it's `Terminal`. Run the following command:

```
pip3 install exhibiter
```

When you first run the program after installing it, it will ask to install [Pandoc](https://pandoc.org/), a free and open-source document converter. If the automatic install fails, you'll need to [install Pandoc yourself](https://pandoc.org/installing.html).

# Usage

## 1. Organize your Files First

To run this program, you must provide it with a folder full of organized evidence (the "input folder"). The input folder should contain one or more subfolders representing exhibits ("exhibit folders"). Exhibit folders, in turn, must contain one or more documents.

### Put Exhibits in the Input Folder

Exhibits are folders whose names follow the patterns `INDEX` or `INDEX (TITLE)`, where `INDEX` is a number, or a capital letter. An example exhibit would be  `101 (Rental Agreement)`.

Exhibits (and individual documents) will be omitted if their folder names contain `(UNUSED)` or `(EXCLUDE)` except if the program is run in Discovery Mode (`-d`).

Consider the following examples:

| Example Folder Name                        | Result                                                       |
| ------------------------------------------ | ------------------------------------------------------------ |
| 101                                        | included as Exhibit 101                                      |
| 102 (Proof of Rent Payments)               | included, and its entry in the Exhibit List (though not the PDF) will be preceded by a title |
| 103 (UNUSED)                               | excluded, except in Discovery Mode                           |
| 104 (Photographs of the Interior) (UNUSED) | same as above, but with title                                |
| Notes                                      | excluded because it doesn't follow the `INDEX (TITLE)` format |
| 105.pdf                                    | excluded because it is not a folder                          |

You probably shouldn't provide titles for Exhibits that contain only one Document, because in that case the Document name would make the title redundant.

### Put Documents in each Exhibit Folder

Each exhibit folder must contain one or more documents, which will be arranged alphabetically based on their filenames.

A document can be one of three things:

1. **a PDF**,
2. **an image** (specifically .png, .jpg, or .jpeg), or
3. **a folder of images**. The images will be arranged alphabetically by filename, but only the folder's name will be used as the name of the document.

Anything else in an Exhibit folder will be ignored, except `evidentiary disputes.txt`. If this file is present, its contents will be written into the Evidentiary Disputes column of the Exhibit List.

#### Rules for Document Names

Within each exhibit, **the program always arranges documents alphabetically** based on their filenames.

- **To arrange documents chronologically**, their names must start with a date in YYYY-MM-DD format followed by space (no other separators). For example, `2020-01-02 Welcome Note.pdf` will be detected and displayed in the Exhibit List as "Welcome Note 1/2/20."

- **Documents with dates will normally appear before those without**, because numbers precede letters.

- **To arrange documents manually**, precede each filename with a series of digits, followed by a period and a space. For example, `01. Welcome Note.jpg` will be displayed in the Exhibit List as "Welcome Note." Leading numbers in this format will be hidden in the List unless the program is run with the `-k` or `--keep-digits` option.

- Documents whose names contain the `(UNUSED)` or `(EXCLUDE)` tag will be omitted from the output unless the program is run in Discovery Mode (`-d`). In Discovery Mode, the tag will be ignored and the Document will be included, with the tag stripped from its name.

### Example Folder Structure

![Sample Input Folder](https://raw.githubusercontent.com/raindrum/exhibiter/master/ExampleFolder.png)

This example folder demonstrates most of the ways evidence can be arranged:

- Exhibits 102 through 104 have titles because their filenames contain a section in parentheses. Exhibit 101 is given no title because it would be redundant when it contains only one document.
- The contents of Exhibits 102 and 103 are arranged chronologically because their filenames start with a date in YYYY-MM-DD format. They will appear in the exhibit list in chronological order, and the dates will be processed so that they show in the exhibit list as, e.g., "Rent Receipt 1/1/20."
- The exact date for the security deposit in Exhibit 102 isn't known, but it can be manually arranged by giving it a number lower than the dates (here, 1). Because the number is followed by a period and a space, the program knows to exclude it from the document's name in the exhibit list; it will appear only as "Security Deposit."
- One of the rent receipts in Exhibit 102, and the entirety of Exhibit 103, are marked "(UNUSED)." Therefore, they will be omitted unless the program is run in discovery mode.
- Most files in the above example are treated as individual documents, whose filenames will appear in the exhibit list. The three images in the "Ceiling Photos" folder in Exhibit 104 are an exception; because they are inside a subfolder, they are treated as a single three-page document named "Ceiling Photos."

## 2. Run the Program

Exhibiter is primarily a command-line tool, though it also has a basic GUI option.

**First, open a command line**. On Windows, this is the program called `cmd`. On MacOS, it's `Terminal`.

**If you don't like command lines, use the `exhibiter -g` command**. In this mode, pop-ups will prompt you to select the input folder and name the output list and PDF.

If you don't use the `-g` option, you will need to specify an input folder from the command line by running `exhibiter INPUTFOLDER`. In this mode, the program will output to `Defense Exhibits.pdf` and `Defense Exhibit List.docx` in the current directory, unless you override those defaults with the `-o` and `-l` options respectively.

To see more options you can specify when running the program, run `exhibiter -h`.

# Command Line Options

Whether run in graphical mode or not, it's possible to pass a number of command-line options to the program to affect how it runs. These are explained below:

| Option                             | Description                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| `-g` or `--gui`                    | Use a graphical interface to select the input and output files and whether to use discovery mode, assuming those are not specified explicitly in the command line. This is meant as a tool for those who are not comfortable navigating their filesystem via a command line; it does not allow graphical selection of other program options, though they can be specified as additional command-line options while using `-g`. |
| `-d` or `--discovery-mode`         | Output discovery responses instead of trial exhibits. If this option is specified, the output will include the files marked `(UNUSED)` or `(EXCLUDE)`, but will not print page numbers. |
| `-o` or `--outpdf`                 | Specify where to output the PDF containing all evidence. Defaults to "Defense Exhibits.pdf" in the current directory. |
| `-l` or `--outlist`                | Specify where to output the DOCX file listing the evidence. Defaults to "Defense Exhibit List.docx" in the current directory. |
| `-k` or `--keep-digits`            | When processing file names to create entries in the exhibit list, the program normally assumes that when a file name starts with a number, followed by a period and a space, the number is not actually part of the document name. So a file named "2. Lease addendum.pdf" will normally appear in the exhibit list as "Lease addendum". With the `-k` option, it would appear instead as "2. Lease addendum". |
| `-c` or `--page-label-coordinates` | When not in discovery mode, the program prints exhibit page numbers (e.g. 101-3) on each page of evidence. By default the program places those page numbers near the bottom middle of the page, but sometimes this will obstruct evidence. This option lets you provide coordinates where the label should be placed, expressed as percentages of the way across and up the page. For instance, `-c 95 10` will print the label near the bottom right of the page, because it will be 95% *across* and 10% *up* the page. |
| `-n` or `-no-list-page-numbers`    | Normally, when not in Discovery Mode, the exhibit list will show the start and end page of each document, in parentheses. This option disables that. |
| `-p` or `--plaintiff`              | Label the list as a plaintiff's exhibit list rather than defendant's. |
| `--attachno`                       | Specify what attachment number to label the exhibit list as. Defaults to 4. |
| `--no-rebuttal`                    | Ordinarily the exhibit list will show one empty exhibit at the end, titled "Reserved for Rebuttal." This option disables that. |
| `--nopdf`                          | Do not output a PDF of evidence.                             |
| `--nolist`                         | Do not output a DOCX listing evidence.                       |

