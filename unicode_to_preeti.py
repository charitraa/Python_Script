from preeti_unicode import file_converter

# Convert DOCX
file_converter(
    input_file="/home/meow/Desktop/Final book of Marwadi (Final) 1.docx",
    input_format="docx",
    output_file="unicode_output.docx",
    output_format="docx",
)

print("✅ DOCX converted successfully!")
