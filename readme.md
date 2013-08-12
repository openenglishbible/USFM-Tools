This project comprises a framework for transforming .usfm files into specified targets.

It is primarily used for the Open English Bible, and may need adjustment if used for other purposes.

# Installation

# Prerequisites

    sudo easy_install pyparsing

# Get code

    git clone 
    cd USFM-Tools
    python transform.py --setup
 
(This downloads ConTeXt and may take a while.)
 
# Run

    python transform.py --target=context --usfmDir=/path/to/usfmfiles/ --builtDir=built/ --name=MyTranslation

