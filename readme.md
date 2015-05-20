This project comprises a framework for transforming .usfm files into specified targets.

It is primarily used for the Open English Bible, and may need adjustment if used for other purposes.

# Installation

# Prerequisites

    pip install pyparsing
    
    For Word output:
    pip install python-docx
    
    Install copies of ConTeXt for PDF output:
    http://wiki.contextgarden.net/ConTeXt_Standalone
    
    Install Calibre for ePub output:
    http://calibre-ebook.com

# Get code

    git clone https://github.com/openenglishbible/USFM-Tools.git
    cd USFM-Tools

# Run

    python transform.py --target=singlehtml --usfmDir=/path/to/usfmfiles/ --builtDir=built/ --name=MyTranslation

