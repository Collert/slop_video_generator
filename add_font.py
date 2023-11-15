import os
import fnmatch
import configparser
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont

config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read('config.cfg')

def check_install(filename = "imdisplay.exe", start_dir=config['Misc']['ImageMagick_directory']):
    for root, dirs, files in os.walk(start_dir):
        for name in fnmatch.filter(files, filename):
            return
    raise FileNotFoundError("ImageMagick installation not found. Check your config file.")

check_install()
xml_path = config['Misc']['ImageMagick_directory'] + "/type-ghostscript.xml"
font_path = input("Paste the path to your font: ")
# Check if the provided path is a .ttf file
if not font_path.lower().endswith('.ttf'):
    raise ValueError("The provided path is not a .ttf file")

# Load the TTF file
font = TTFont(font_path)

# Extract font metadata
font_name = font['name'].getDebugName(4).replace(' ', '-')  # Get the full font name
font_family = font['name'].getDebugName(1)  # Get the font family name
font_style = font['name'].getDebugName(2)  # Get the font style

# Use 'OS/2' table to get the font weight
font_weight = font['OS/2'].usWeightClass

# Create a new <type> element
new_type = ET.Element('type')
new_type.set('name', font_name)
new_type.set('fullname', font_name)
new_type.set('family', font_family)
new_type.set('style', font_style)
new_type.set('weight', str(font_weight))
new_type.set('stretch', 'normal')  # Assume normal stretch
new_type.set('format', 'type1')  # Assume type1 format
new_type.set('metrics', font_path)
new_type.set('glyphs', font_path)

# Parse the XML file
tree = ET.parse(xml_path)
root = tree.getroot()

# Add the new <type> element to the <typemap> root element
root.append(new_type)

# Save the updated XML file
try:
    tree.write(xml_path)
except PermissionError:
    print(f"Failed to write to {xml_path}: Make sure to run this terminal window as administrator.")

print(f'Font added! Use it in your generator as "{font_name}"')