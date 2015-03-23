This project comprises a framework for transforming .usfm files into specified targets.

It is primarily used for the Open English Bible, and may need adjustment if used for other purposes.

# Installation

# Prerequisites

    pip install pyparsing

# Get code

    git clone https://github.com/openenglishbible/USFM-Tools.git
    cd USFM-Tools

# Install ConTeXt for PDF output

    See http://wiki.contextgarden.net/ConTeXt_Standalone 
 
# Run

    python transform.py --target=context --usfmDir=/path/to/usfmfiles/ --builtDir=built/ --name=MyTranslation

