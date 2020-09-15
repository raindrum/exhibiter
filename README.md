![icon](https://raw.githubusercontent.com/raindrum/exhibiter/master/icon.svg)

This is a tool to help organize evidence for litigation. If you keep your evidence as named pdf, jpg, and png files in numbered exhibit folders, the program can automatically generate an exhibit list (.docx) and a PDF of all evidence (with exhibit dividers), suitable for jury documents and discovery responses.

I made this tool in the hopes that it would make eviction defense a little easier. Plaintiffs may use it as well, but *eviction plaintiffs* and their representatives may not. 

Copyright 2020 Simon Raindrum Sherred.

# Installation

Exhibiter requires Python 3.8 or higher to run. [Here is the link to install it](https://www.python.org/downloads/), if needed. If you use Windows, make sure to choose the installer options to add Python to your PATH, and to disable Windows' 260-character path limit.

Once you have Python, you can install the program from a command prompt. On Windows, that's the `cmd` application; on MacOS it's `Terminal`. Run the following command:

```
pip3 install exhibiter
```

When you first run the program after installing it, it will ask to install [Pandoc](https://pandoc.org/), a free and open-source document converter. If the automatic install fails, you'll need to [install Pandoc yourself](https://pandoc.org/installing.html).

# Usage

## 1. Organize your Files First

For the script to run correctly, all your evidence for the case must be organized in a specific way. This organizational structure is meant to be intuitive, but it still needs a little explanation.

The Input Folder is the main folder that you want the program to process, and it should contain all the relevant evidence. It does not matter where this folder is, or what it is named; you will just need to tell the program where it is.

### Put Exhibits in the Input Folder

The Input Folder must contain one or more Exhibit Folders. These are folders whose names follow the patterns `NUMBER` or `NUMBER (TITLE)`, such as `101 (Rental Agreement)`. Each one will presumably contain one or more Documents. 

Exhibits (and Documents) will be omitted if their folder names contain `(UNUSED)` or `(EXCLUDE)` except if the program is run in Discovery Mode (`-d`).

Consider the following examples:

| Example Folder Name                        | Result                                                       |
| ------------------------------------------ | ------------------------------------------------------------ |
| 101                                        | included as Exhibit 101                                      |
| 102 (Proof of Rent Payments)               | included, and its entry in the Exhibit List (though not the PDF) will be preceded by a title |
| 103 (UNUSED)                               | excluded, except in Discovery Mode                           |
| 104 (Photographs of the Interior) (UNUSED) | same as above, but with title                                |
| Notes                                      | excluded because it doesn't follow the `NUMBER (TITLE)` format |
| 105.pdf                                    | excluded because it is not a folder                          |

You probably shouldn't provide titles for Exhibits that contain only one Document, because in that case the Document name would make the title redundant.

Also note that exhibit numbers over 200 will cause errors unless you add more pages to the included `assets/cover_pages.pdf`.

### Put Documents in each Exhibit Folder

Each Exhibit Folder must contain one or more Documents, which will be arranged alphabetically.

A Document can be one of three things:

1. **a PDF**,
2. **an image** (specifically .png, .jpg, or .jpeg), or
3. **a folder of images**. The images will be arranged alphabetically by name, but only the folder name will be displayed as the name of the Document.

Anything else in an Exhibit folder will be ignored, except `evidentiary disputes.txt`. If this file is present, its contents will be written into the Evidentiary Disputes column of the exhibit list.

#### Rules for Document Names

Within each Exhibit, **the program arranges Documents alphabetically** based on their file names.

**To arrange documents chronologically**, their names must start with a date in YYYY-MM-DD format followed by space (no other separators). For example, `2020-01-02 Welcome Note.pdf` will be detected and displayed in the Exhibit List as "Welcome Note 1/2/20."

**Documents with dates will normally appear before those without**, because numbers precede letters.

**To arrange documents manually**, precede each filename with a series of digits, followed by a period and a space. For example, `01. Welcome Note` will be displayed in the Exhibit List as "Welcome Note." Leading numbers in this format will be hidden in the List unless the program is run with the `-k` or `--keep-digits` option.

Documents whose names contain the `(UNUSED)` or `(EXCLUDE)` tag will be omitted from the output unless the program is run in Discovery Mode (`-d`). In Discovery Mode, the tag will be ignored and the Document will be included, with the tag stripped from its name.

## 2. Run the Program

Exhibiter is primarily a command-line tool, though it also has a basic GUI option.

**First, open a command line**. On Windows, this is the program called `cmd`. On MacOS, it's `Terminal`.

**If you don't like command lines, use the `exhibiter -g` command**. In this mode, pop-ups will prompt you to select the input folder and name the output list and PDF.

If you don't use the `-g` option, you will need to specify an input folder from the command line by running `exhibiter INPUTFOLDER`. In this mode, the program will output to `Defense Exhibits.pdf` and `Defense Exhibit List.docx` in the current directory, unless you override those defaults with the `-o` and `-l` options respectively.

To see more options you can specify when running the program, run `exhibiter -h`.