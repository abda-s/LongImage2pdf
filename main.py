from PIL import Image
from fpdf import FPDF
import math

# Load the image
image_path = "tall_image.png"
image = Image.open(image_path)

# Get the width and height of the image
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
for i in range(pages):
    top = i * page_height
    bottom = min((i + 1) * page_height, image_height)
    cropped_image = image.crop((0, top, image_width, bottom))
    
    # Convert to RGB mode for saving as JPEG
    cropped_image = cropped_image.convert("RGB")
    
    # Save the cropped image as .jpg
    cropped_image.save(f"page_{i + 1}.jpg")

print(f"Image successfully split into {pages} pages.")

# Create a PDF with each cropped image
pdf = FPDF(unit="pt", format=(A4_width, A4_height))  # Standard A4 size for the PDF
for i in range(pages):
    pdf.add_page()
    pdf.image(f"page_{i + 1}.jpg", x=0, y=0, w=A4_width, h=A4_height)  # Fit image to A4

# Output the PDF to a file
pdf.output("output.pdf")
print("PDF created successfully.")
