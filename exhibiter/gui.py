"""This tool takes a folder full of evidence and makes a PDF containing
all of it, plus a Word document that lists the evidence in detail.
Before using it, you must organize the input folder into exhibits, as
described <a href="https://github.com/raindrum/exhibiter#usage">here</a>."""

# python standard imports
import sys
from pathlib import Path

# third-party imports
from PySide2 import QtCore, QtWidgets, QtGui

# internal imports
from exhibiter import Exhibit, evidence_in_dir, write_pdf, write_list

_description = __doc__.replace("\n", " ")


class ExhibiterWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exhibiter")
        self.setWindowIcon(QtGui.QIcon("icon.ico"))
        self.layout = QtWidgets.QVBoxLayout()
        # Defaults
        self.selected_dir = Path()
        self.exhibits_need_regen = True
        self.exhibits = []

        header = QtWidgets.QLabel(_description)
        header.setOpenExternalLinks(True)
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setWordWrap(True)
        self.layout.addWidget(header)

        # input folder location
        input_dir_btn = QtWidgets.QPushButton("Choose Input Folder")
        input_dir_btn.setToolTip(
            "This is the folder containing all of the evidence\n"
            + "to compile. It must be organized into subfolders\n"
            + "of exhibits, as described in the link above."
        )
        input_dir_btn.clicked.connect(self.input_folder_picker)
        self.layout.addWidget(input_dir_btn)

        # exclude toggle
        self.exclusions_toggle = QtWidgets.QCheckBox(
            'Include documents marked "(UNUSED)"'
        )
        self.exclusions_toggle.setToolTip(
            "Unless this option is checked, any document\n"
            + "or exhibit will be omitted if its filename\n"
            + "has one of these words (with parentheses)."
        )
        self.exclusions_toggle.toggled.connect(self.trigger_exhibit_regen)
        self.layout.addWidget(self.exclusions_toggle)

        # container to hold the PDF and DOCX options sets
        outputs_box = QtWidgets.QHBoxLayout()
        self.layout.addLayout(outputs_box)

        # container to hold exhibit list (docx) options
        list_box = QtWidgets.QVBoxLayout()
        outputs_box.addLayout(list_box)
        outputs_box.addSpacing(15)

        # exhibit list heading
        list_options_heading = QtWidgets.QLabel("<b>Exhibit List</b>")
        list_options_heading.setAlignment(QtCore.Qt.AlignCenter)
        list_box.addWidget(list_options_heading)

        # party selection
        party_label = QtWidgets.QLabel("Party:")
        party_label.setWordWrap(True)
        self.party_choices = QtWidgets.QComboBox()
        self.party_choices.addItems(["Defense", "Plaintiff"])
        party_row = QtWidgets.QHBoxLayout()
        self.party_choices.setToolTip(
            'Should the exhibit list say "Defense Exhibits"\n'
            'or "Plaintiff Exhibits"?'
        )
        party_row.addWidget(party_label)
        party_row.addWidget(self.party_choices)
        list_box.addLayout(party_row)

        # page numbering toggle
        self.reserve_rebuttal = QtWidgets.QCheckBox("Reserve rebuttal exhibit")
        self.reserve_rebuttal.setChecked(True)
        self.reserve_rebuttal.setToolTip(
            "Should the exhibit list show a blank exhibit at\n"
            + 'the end, labeled "Reserved for Rebuttal"?'
        )
        list_box.addWidget(self.reserve_rebuttal)

        # attachment number selection
        attachno_label = QtWidgets.QLabel("Attachment Number:")
        attachno_label.setWordWrap(True)
        self.attachno_spinbox = QtWidgets.QSpinBox()
        self.attachno_spinbox.setValue(4)
        attachno_row = QtWidgets.QHBoxLayout()
        attachno_row.addWidget(attachno_label)
        attachno_row.addWidget(self.attachno_spinbox)
        self.attachno_spinbox.setToolTip(
            "The exhibit list's header says it is\n"
            + '"Attachment X: Exhibit List". This is X.'
        )
        list_box.addLayout(attachno_row)

        # save docx
        self.docx_save_btn = QtWidgets.QPushButton("Save Exhibit List")
        self.docx_save_btn.setEnabled(False)
        self.docx_save_btn.setToolTip("You must select an input folder first.")
        self.docx_save_btn.clicked.connect(self.save_docx)
        list_box.addWidget(self.docx_save_btn)

        # container to hold exhibit list (docx) options
        pdf_box = QtWidgets.QVBoxLayout()
        outputs_box.addLayout(pdf_box)

        # pdf options
        pdf_options_heading = QtWidgets.QLabel("<b>Evidence PDF</b>")
        pdf_options_heading.setAlignment(QtCore.Qt.AlignCenter)
        pdf_box.addWidget(pdf_options_heading)

        # landscape rotation toggle
        self.rotation_toggle = QtWidgets.QCheckBox("Rotate landscape photos")
        self.rotation_toggle.setToolTip(
            "Should landscape photos be rotated to portrait\n"
            + "so that they take up more of the page?"
        )
        self.rotation_toggle.setChecked(True)
        self.rotation_toggle.toggled.connect(self.trigger_exhibit_regen)
        pdf_box.addWidget(self.rotation_toggle)

        # page numbering toggle
        self.pagination_toggle = QtWidgets.QCheckBox("Page numbers")
        self.pagination_toggle.setToolTip(
            "Should each page be stamped with its page number?\n"
            + "Page numbers are relative to the exhibit, e.g. 101-2"
        )
        self.pagination_toggle.setChecked(True)
        self.pagination_toggle.toggled.connect(self.toggle_page_labels)
        pdf_box.addWidget(self.pagination_toggle)

        # page label location setter
        self.page_coords_label = QtWidgets.QLabel("Page number coords (X, Y):")
        self.page_coords_spinbox_x = QtWidgets.QSpinBox()
        self.page_coords_spinbox_x.setToolTip(
            "Horizontal position of page numbers,\n"
            + "expressed as a percentage of the way\n"
            + "from the page's left edge to right."
        )
        self.page_coords_spinbox_x.setValue(50)
        self.page_coords_spinbox_x.valueChanged.connect(self.trigger_exhibit_regen)
        self.page_coords_spinbox_y = QtWidgets.QSpinBox()
        self.page_coords_spinbox_y.setToolTip(
            "Vertical position of page numbers,\n"
            + "expressed as a percentage of the way\n"
            + "from the page's bottom edge to top."
        )
        self.page_coords_spinbox_y.setValue(3)
        self.page_coords_spinbox_y.valueChanged.connect(self.trigger_exhibit_regen)
        page_coords_row = QtWidgets.QHBoxLayout()
        self.page_coords_label.setWordWrap(True)
        page_coords_row.addWidget(self.page_coords_label)
        page_coords_row.addWidget(self.page_coords_spinbox_x)
        page_coords_row.addWidget(self.page_coords_spinbox_y)
        pdf_box.addLayout(page_coords_row)

        # pdf save button
        self.pdf_save_btn = QtWidgets.QPushButton("Save Evidence PDF")
        self.pdf_save_btn.setEnabled(False)
        self.pdf_save_btn.setToolTip("You must select an input folder first.")
        self.pdf_save_btn.clicked.connect(self.save_pdf)
        pdf_box.addWidget(self.pdf_save_btn)

        # footer text
        footer = QtWidgets.QLabel(
            "Copyright 2021 Simon Raindrum Sherred.\n"
            + "Eviction plaintiffs are not permitted to use this software."
        )
        footer.setWordWrap(True)
        footer.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(footer)

        self.setLayout(self.layout)

    def msg_if_fail(func):
        def wrapper(*args):
            try:
                func(*args)
            except Exception as e:
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle(type(e).__name__)
                msg.setText(str(e))
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()

        return wrapper

    @msg_if_fail
    @QtCore.Slot()
    def input_folder_picker(self):
        selection = QtWidgets.QFileDialog.getExistingDirectory(
            caption="Choose the folder to scan for exhibits",
            directory=str(self.selected_dir),
        )
        if selection:
            self.input_dir = selection
            self.selected_dir = Path(selection).parent
            self.load_exhibits()

    @QtCore.Slot()
    def trigger_exhibit_regen(self):
        """When certain options are toggled, signal that the exhibit
        list needs to be rebuilt."""
        self.exhibits_need_regen = True

    @msg_if_fail
    @QtCore.Slot()
    def save_pdf(self):
        if self.exhibits_need_regen:
            self.load_exhibits()
        selection = QtWidgets.QFileDialog.getSaveFileName(
            caption="Choose where to save the Exhibits PDF",
            directory=str(self.selected_dir),
            filter="PDF Document (*.pdf *.PDF)",
        )[0]
        if selection:
            output_pdf = Path(str(selection))
            self.selected_dir = str(output_pdf.parent)
            write_pdf(self.exhibits, output_pdf)

    @msg_if_fail
    @QtCore.Slot()
    def save_docx(self):
        if self.exhibits_need_regen:
            self.load_exhibits()
        selection = QtWidgets.QFileDialog.getSaveFileName(
            caption="Choose where to save the Exhibit List",
            directory=str(self.selected_dir),
            filter="Word Document (*.docx)",
        )[0]
        if selection:
            output_docx = Path(selection)
            write_list(
                self.exhibits,
                output_docx,
                attachment_no=self.attachno_spinbox.value(),
                party_label=self.party_choices.currentText(),
                show_page_numbers=True,
                reserve_rebuttal=self.reserve_rebuttal.isChecked(),
            )
            self.selected_dir = str(output_docx.parent)

    @QtCore.Slot()
    def toggle_page_labels(self):
        enabled = self.pagination_toggle.isChecked()
        self.page_coords_label.setEnabled(enabled)
        self.page_coords_spinbox_x.setEnabled(enabled)
        self.page_coords_spinbox_y.setEnabled(enabled)
        self.trigger_exhibit_regen()

    def load_exhibits(self):
        # find all the exhibit locations
        exhibit_paths = evidence_in_dir(
            Path(self.input_dir), self.exclusions_toggle.isChecked()
        )

        # then add them all to the exhibit list
        self.exhibits = []
        for path in exhibit_paths:
            self.exhibits.append(
                Exhibit.from_path(
                    path,
                    respect_exclusions=not self.exclusions_toggle.isChecked(),
                    number_pages=self.pagination_toggle.isChecked(),
                    page_label_coords=(
                        self.page_coords_spinbox_x.value(),
                        self.page_coords_spinbox_y.value(),
                    ),
                    rotate_landscape_pics=self.rotation_toggle.isChecked(),
                    strip_leading_digits=True,
                )
            )

        # update theGUI
        self.exhibits_need_regen = False
        self.docx_save_btn.setEnabled(True)
        self.pdf_save_btn.setEnabled(True)
        self.pdf_save_btn.setToolTip(
            "This is the PDF file that contains all of the\n"
            + "combined evidence, split up by exhibit dividers."
        )
        self.docx_save_btn.setToolTip(
            "This is the exhibit list, a word document\n"
            + "listing the exhibits and their contents."
        )


def gui():
    """Entry point"""
    app = QtWidgets.QApplication([])
    app.setApplicationName("Exhibiter")
    widget = ExhibiterWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    gui()
