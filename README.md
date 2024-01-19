
# AutoMark

## Overview
AutoMark is a Fontforge script designed to simplify the process of adding OpenType mark features(mark to base, mark to ligature, and mark to mark), and placing anchors for Arabic glyphs (on marks, base glyphs, and ligatures). The script using codepoints(instead of glyph names) and even trying to bring a range of predictable non-Unicode glyphs by checking OpenType GSUB features such as `ccmp`, `init`, `medi`, `fina`, `liga`, and `rlig`. AutoMark's functionality is not realted to the number of a glyph's outline contours and/or components.

## How It Works
AutoMark contains an in-built database for Arabic script codepoints, which includes preferences for anchor placements relative to glyph shape. Additionally, specific functions are included to calculate anchor placement in various glyph shapes. The database and functions are designed to be flexible and independent of glyph shape in varius typefaces.

## Usage

Before running AutoMark:
- Ensure the input font or Fontforge source file does not contain any mark or mkmk features and anchors. If it does contain advanced mark features or other mark types, they can still works with no interfering (like cursive attachments,etc).
- Python and FontForge must be installed and accessible in the system's PATH.

To run AutoMark, use the following command:
```
fontforge -script Automark.py input_font_path output_font_path
```
(you can use the input and output file name in the same directory of AutoMark.py)
*Note: AutoMark is designed to prevent overwriting the input file; using the same name for input and output will not result in file overwriting(the output file name will give a '-AutoMark' suffix).*

## Customization
The script allows for the customization of parameters to fine-tune anchor placements within glyphs. run Automark -help
to get more information.

## Side Notes
Currently, the script does not have any dependencies outside of Python and FontForge. While there is no conscious effort to minimize dependencies, as a result, the script does not require a `requirements.txt` at the moment.

## License
AutoMark is released under the MIT License. See the LICENSE file for more details.
