![icon](https://raw.githubusercontent.com/raindrum/exhibiter/master/graphics/promo.png)

This is a tool to help assemble evidence for litigation. Given an organized folder of PDFs and images, Exhibiter can create a single PDF containing all the evidence, complete with cover sheets and page numbers. It also creates an exhibit list as a Word document. An example of its inputs and outputs is available [here](https://github.com/raindrum/exhibiter/tree/master/example).

I made this tool in the hopes that it would make eviction defense a little easier. Others may use it as well, but eviction plaintiffs and their representatives may not.

# Installation

If you use Windows or MacOS, head to the [Releases](https://github.com/raindrum/exhibiter/releases) page and download the latest `.exe` or `.app`, respectively. Save it wherever you want, and it's installed! Just double-click it whenever you want to run it.

Alternatively, if you use Linux, or if you just want to run the program from a command-line, you can install it with `pip`. To do that, ensure that [Python 3](https://www.python.org/downloads/) is installed, then run the following command:

```bash
python3 -m pip install exhibiter
```

After that, you should be able to launch the Exhibiter GUI with the `exhibiter` command, or the command-line interface with `exhibiter-cli`.

# Usage

Before you can use Exhibiter to compile evidence, you'll need to do a little work to rename and organize the input files.

First, let's define some basic concepts:

- The **input folder** is the folder that you'll ultimately tell Exhibiter to process. It must contain one or more exhibit folders.
- **Exhibits** are the files and folders located directly within the input folder. They can be PDFs, photos, or folders full of PDFs or photos. Every exhibit will have its own row in the exhibit list, and its own cover sheet in the main evidence PDF.
- As noted above, an exhibit can be a folder. **Documents** are the files and folders located directly within an exhibit folder. Like exhibits, they can be PDFs, photos, or folders full of PDFs or photos. The exhibit list will display brief a description of each document in every exhibit.

The sections below give a bit more detail on these concepts. If you want an example of a completed input folder, see [here](https://github.com/raindrum/exhibiter/tree/master/example).

## Name the Exhibits

Every exhibit's filename (or folder name) must have a number or capital letter. For instance, `101` and `A` are both valid folder names, representing Exhibit 101 or Exhibit A, respectively.

You may also give each exhibit a title, which will appear in the exhibit list. If the exhibit is a folder full of named documents, the title is optional. If the exhibit is a PDF or image, it *must* have a title.

An exhibit has a title if, after the exhibit number, the filename has a period, space, and then some text. An example of a titled exhibit is `103. Party Communications`.

Finally, you may also add `(UNUSED)` at the end of a filename, indicating that Exhibiter should omit this exhibit unless expressly told otherwise. This is useful for evidence that should be produced in discovery but which you do not plan to introduce at trial.

## Organize the Documents

As noted above, exhibits can be folders full of individual named documents. A document can be a PDF, an image in JPG or PNG format, or a folder full of PDFs or images. In any case, the document's filename determines how and where the document will appear. Note that if a document is a folder, the relevant filename is the name of the *folder*, not the files inside.

Within each exhibit, documents will be arranged in alphabetical order based on their filenames.

Each document will appear in the exhibit list with a description derived from its filename. Exhibiter has some opinions about how to turn filenames into descriptions, so you'll need to understand its process so that you can write filenames in a compatible format:

1. First, Exhibiter removes the file extension, e.g. `.pdf`.
2. If the filename starts with a number followed by a period and a space, Exhibiter removes this number, on the assumption that it's only meant for indicating the order of documents.
3. If the filename starts with a date in YYYY-MM-DD or YYYYMMDD format, Exhibiter moves it to the end of the description, in M/D/YY format. If chronology is important, you should start filenames with these dates so that they will appear in chronological order. An example document filename is `2019-01-03 Rent Payment.jpg`.
4. If the document's filename ends with `(UNUSED)`, the document will normally be omitted, the same way that entire exhibits with that tag will be omitted. If you tell Exhibiter *not* to omit such documents, the word `(UNUSED)` will be omitted from the description.

## Run the Program

Finally, you're ready to run the program, by double-clicking the executable if you followed the Windows or MacOS instructions, or by running the `exhibiter` command if you installed it from `pip`. You should see a window like this:

![screenshot](https://raw.githubusercontent.com/raindrum/exhibiter/master/graphics/screenshot.png)

You can mouse over any of the options to see a description of what it does.