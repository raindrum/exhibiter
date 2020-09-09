![icon](icon.svg)

This is a tool to help organize evidence for litigation. If you keep your evidence as named pdf, jpg, and png files in numbered exhibit folders, the program can automatically generate an exhibit list and PDF suitable for jury documents and discovery responses.

I made this tool in the hopes that it would make eviction defense a little easier. Plaintiffs may use it as well, but *eviction plaintiffs* and their representatives may not. 

Copyright 2020 Simon Raindrum Sherred.

# Installation

This package requires Python 3.8 or higher to run. If you do not have Python, follow [this link](https://www.python.org/downloads/) to install it. If you use Windows, make sure to select the options to add Python to your PATH, and to disable the 260-character path limit.

Once you have Python, you should be able to install the program by running the following command:

```
pip install https://github.com/raindrum/exhibiter/raw/master/dist/exhibiter-1.0.0.tar.gz
```

The program also requires [Pandoc](https://pandoc.org/), a free and open-source document converter.  It can usually install Pandoc automatically with your permission, but if this fails you will need to install it by following [the directions on their website](https://pandoc.org/installing.html).

# Usage

## 1. Organize your Files First

For the script to run correctly, all your evidence for the case must be organized in a specific way. This organizational structure is meant to be intuitive, but it still needs a little explanation.

The Evidence Folder is the main folder that you want the program to process. It does not matter where this folder is, or what it is named; you will just need to tell the program where it is.

### 1.1. Put Exhibits in the Evidence Folder

The Evidence Folder must contain one or more Exhibit Folders, whose names must be a number, plus optionally a title and/or an `UNUSED` tag in parentheses. Non-folders, and folders that don't begin with numbers, will be omitted.

The following Exhibit Folder examples should help understand the functionality:

| Folder Name                                | Result                                                       |
| ------------------------------------------ | ------------------------------------------------------------ |
| 101                                        | included                                                     |
| 102 (Proof of Rent Payments)               | included with title                                          |
| 103 (UNUSED)                               | excluded except in Discovery mode. "(EXCLUDE)" has the same effect |
| 104 (Photographs of the Interior) (UNUSED) | same as above, but with title                                |
| Notes                                      | excluded because name does not begin with a number           |
| 105.pdf                                    | excluded because it is not a folder                          |

You should not provide titles for Exhibits that contain only one Document, because in that case the Document name would make the title redundant.

Also note that exhibits with numbers over 200 will not work properly. If, for whatever reason, you need more than 200 exhibits, add more pages to the included `assets/cover_pages.pdf`.

### 1.2. Put Documents in each Exhibit Folder

Each Exhibit Folder must contain one or more Documents, which will be arranged alphabetically. A Document can be one of three things:

1. a PDF,
2. an image file (specifically .png, .jpg, or .jpeg), or
3. a folder full of image files, in which case the Document will contain all of them in alphabetical order.

Anything else in an Exhibit folder will be ignored, except `evidentiary disputes.txt`. If this file is present, its contents will be written into the Evidentiary Disputes column of the exhibit list.

#### Rules for Document Names

1. Inside each Exhibit, the program arranges Documents alphabetically based on their filenames. Here's how to make the best use of this:
   - For chronological order, start the filename with a date in YYYY-MM-DD format, followed by a space. E.g. `2020-01-09 Welcome Note.pdf`. This will be detected and displayed in the Exhibit List as "Welcome Note 1/9/20."
   - For other ordering, begin the filename with any number of digits, followed by a period and a space. E.g. `01. Welcome Note`. The number will be hidden in the exhibit list. To preserve these numbers, you can run the program from a command line with the `-k` or `--keep-digits` option.
2. If a filename contains `(UNUSED)` or `(EXCLUDE)`, the Document will be omitted except in Discovery mode.
3. Filenames are processed to create a line in the Exhibit List for the document.

Note that for Documents that are themselves folders of images, the relevant filename is the name of the folder, *not* the images inside. The images will be arranged alphabetically, and their names are otherwise ignored.

## 2. Run the Program

Open a command line and type `exhibiter`, then press Enter, to see the options for running the program from a command line. Fundamentally, the program depends on specifying the path to an input folder, by typing `exhibiter FOLDERNAME`.

You can also type `exhibiter -g` to use the program in graphical mode. Note that this mode does not include the advanced options available in command-line mode.