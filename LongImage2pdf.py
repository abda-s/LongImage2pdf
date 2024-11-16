import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QLineEdit, QProgressBar, QDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
from fpdf import FPDF
import math
import os

class ImageProcessingThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, image_path, output_pdf_path):
        super().__init__()
        self.image_path = image_path
        self.output_pdf_path = output_pdf_path

    def run(self):
        try:
            # Load the image
            image = Image.open(self.image_path)
            image_width, image_height = image.size

            # Define the A4 page size in points (1 inch = 72 points)
            A4_ratio = 1.4142
            A4_width = image_width  # A4 width in points
            A4_height = image_width * A4_ratio  # A4 height in points

            # Calculate the aspect ratio of the image
            image_aspect_ratio = image_width / image_height

            # Calculate the new height based on the A4 width, maintaining the aspect ratio
            new_width = A4_width
            new_height = new_width / image_aspect_ratio

            # If the calculated height exceeds the A4 height, scale the image to fit A4 height
            if new_height > A4_height:
                new_height = A4_height
                new_width = new_height * image_aspect_ratio

            # Resize the image to fit the A4 aspect ratio
            image_resized = image.resize((int(new_width), int(new_height)))

            # Calculate the number of pages needed to fit the image height
            page_height = new_height  # The height of the page is now the resized height
            pages = math.ceil(image_height / page_height)  # Use math.ceil to round up the number of pages

            # Create and save each cropped section of the image
            temp_images = []
            for i in range(pages):
                top = i * page_height
                bottom = min((i + 1) * page_height, image_height)
                cropped_image = image.crop((0, top, image_width, bottom))

                # Convert to RGB mode for saving as JPEG
                cropped_image = cropped_image.convert("RGB")

                # Save the cropped image as .jpg
                temp_image_path = f"temp_page_{i + 1}.jpg"
                cropped_image.save(temp_image_path)
                temp_images.append(temp_image_path)

                # Update progress
                self.progress_updated.emit(int((i + 1) / pages * 100))

            # Create a PDF with each cropped image
            pdf = FPDF(unit="pt", format=(A4_width, A4_height))  # Standard A4 size for the PDF
            for temp_image in temp_images:
                pdf.add_page()
                pdf.image(temp_image, x=0, y=0, w=A4_width, h=A4_height)  # Fit image to A4

            # Output the PDF to a file
            pdf.output(self.output_pdf_path)

            # Clean up temporary images
            for temp_image in temp_images:
                os.remove(temp_image)

            self.finished.emit("PDF created successfully!")

        except Exception as e:
            self.finished.emit(f"An error occurred: {str(e)}")


class ImageToPDFApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image to PDF Converter")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-family: Arial, sans-serif;")

        # Initialize UI components
        self.image_path = None
        self.output_pdf_path = None

        # Create widgets
        self.select_image_button = QPushButton("Select Image", self)
        self.select_output_button = QPushButton("Select Output PDF Path", self)
        self.convert_button = QPushButton("Convert to PDF", self)
        self.status_label = QLabel("Status: Waiting for input...", self)
        self.progress_bar = QProgressBar(self)

        # Set up layouts
        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.select_image_button)
        self.buttons_layout.addWidget(self.select_output_button)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addWidget(self.convert_button)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.progress_bar)

        self.setLayout(self.main_layout)

        # Connect buttons to functions
        self.select_image_button.clicked.connect(self.select_image)
        self.select_output_button.clicked.connect(self.select_output)
        self.convert_button.clicked.connect(self.convert_to_pdf)

    def select_image(self):
        """Select image file"""
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if self.image_path:
            self.status_label.setText(f"Selected Image: {os.path.basename(self.image_path)}")

    def select_output(self):
        """Select output PDF path"""
        self.output_pdf_path, _ = QFileDialog.getSaveFileName(self, "Select Output PDF Path", "", "PDF Files (*.pdf)")
        if self.output_pdf_path:
            self.status_label.setText(f"Output PDF Path: {os.path.basename(self.output_pdf_path)}")

    def convert_to_pdf(self):
        """Start the image to PDF conversion in a separate thread"""
        if not self.image_path or not self.output_pdf_path:
            self.status_label.setText("Please select both an image and an output path.")
            return

        self.status_label.setText("Converting...")
        self.progress_bar.setValue(0)
        self.convert_button.setEnabled(False)

        # Start the processing thread
        self.thread = ImageProcessingThread(self.image_path, self.output_pdf_path)
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.finished.connect(self.on_conversion_finished)
        self.thread.start()

    def update_progress(self, progress):
        """Update the progress bar"""
        self.progress_bar.setValue(progress)

    def on_conversion_finished(self, message):
        """Handle when the conversion is finished"""
        self.status_label.setText(message)
        self.convert_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageToPDFApp()
    window.show()
    sys.exit(app.exec_())
