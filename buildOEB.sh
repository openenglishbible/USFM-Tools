#!/bin/bash

###############
#
#	Functions
#
###############

make-tmp () 
{
	echo buildOEB.sh:: Making tmp
	mkdir tmp	
}

clean-tmp () 
{
	echo buildOEB.sh:: Cleaning tmp
	rm -r tmp	
}

###############
#
#	Setup
#
###############

rm -r built/*

###############
#
#	NT
#
###############

usnt() {
	make-tmp
	cp $OEBDIR/us/4* tmp
	cp $OEBDIR/us/5* tmp
	cp $OEBDIR/us/6* tmp
	#python transform.py --target=context    --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=html       --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=reader     --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-US --oeb
	clean-tmp
}

cthnt() {
	make-tmp
	cp $OEBDIR/cth/4* tmp
	cp $OEBDIR/cth/5* tmp
	cp $OEBDIR/cth/6* tmp
	python transform.py --target=context    --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=md         --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-NT-$ID-Cth --oeb
	clean-tmp
}

###############
#
#    All
#
###############

all() {
	make-tmp
	cp $OEBDIR/* tmp
	python transform.py --target=$TARGET --usfmDir=tmp/ --builtDir=$BUILTDIR --name=$ID --oeb
	clean-tmp
}

###############
#
#	Full Release 
#
###############

release() {
	make-tmp
    cp $OEBDIR/us/00* tmp    
    cp $OEBDIR/us/08* tmp   # Ruth
    cp $OEBDIR/us/17* tmp   # Esther
    cp $OEBDIR/us/19* tmp   # Psalms
    cp $OEBDIR/us/29* tmp   # Joel    
    cp $OEBDIR/us/31* tmp   # Obadiah
    cp $OEBDIR/us/32* tmp   # Jonah
    cp $OEBDIR/us/33* tmp   # Micah
    cp $OEBDIR/us/34* tmp   # Naham
    cp $OEBDIR/us/35* tmp   # Habakkuk
    cp $OEBDIR/us/36* tmp   # Zephaniah
    cp $OEBDIR/us/37* tmp   # Haggai
    cp $OEBDIR/us/38* tmp   # Zechariah
    cp $OEBDIR/us/39* tmp   # Malachai
    # New Testament
	cp $OEBDIR/us/4* tmp
	cp $OEBDIR/us/5* tmp
	cp $OEBDIR/us/6* tmp
	#python transform.py --target=context   --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=html       --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb
	python transform.py --target=reader     --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-US --oeb
	clean-tmp
	make-tmp
    cp $OEBDIR/cth/00* tmp    
    cp $OEBDIR/cth/08* tmp  # Ruth
    cp $OEBDIR/cth/17* tmp  # Esther
    cp $OEBDIR/cth/19* tmp  # Psalms
    cp $OEBDIR/cth/29* tmp   # Joel    
    cp $OEBDIR/cth/31* tmp   # Obadiah
    cp $OEBDIR/cth/32* tmp   # Jonah
    cp $OEBDIR/cth/33* tmp   # Micah
    cp $OEBDIR/cth/34* tmp   # Naham
    cp $OEBDIR/cth/35* tmp   # Habakkuk
    cp $OEBDIR/cth/36* tmp   # Zephaniah
    cp $OEBDIR/cth/37* tmp   # Haggai
    cp $OEBDIR/cth/38* tmp   # Zechariah
    cp $OEBDIR/cth/39* tmp   # Malachai
    # New Testament
	cp $OEBDIR/cth/4* tmp
	cp $OEBDIR/cth/5* tmp
	cp $OEBDIR/cth/6* tmp
	#python transform.py --target=context    --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb
	python transform.py --target=reader     --usfmDir=tmp/ --builtDir=$BUILTDIR --name=OEB-$ID-Cth --oeb
	clean-tmp
}

###############
#
#	Individual Book Functions
#
###############

build-book () 
{
	make-tmp
	cp "$OEBDIR/$BOOKFILE" tmp
	python transform.py --target=$TARGET --usfmDir=tmp/ --builtDir=$BUILTDIR --name=$BOOKNAME --oeb
	clean-tmp
}



###############
#
#	Actions
#
###############

#OEBDIR=/Users/russellallen/git/Open-English-Bible/usfm/development
OEBDIR=/Users/russellallen/git/Open-English-Bible/usfm/release/us
#OEBDIR=/Users/russellallen/Dropbox/oeb/translations/usfm/TSI
BUILTDIR=/Users/russellallen/git/USFM-Tools/built

ID=oeb-current
TARGET=epub
all

#ID=2014.11
#release
#usnt
#all-nt-psalms
#all

#BOOKFILE='08-Ruth.usfm'
#BOOKNAME=ruth
#TARGET=rtf
#build-book

#ID=TSI-2015-12-07
#TARGET=rtf
#all


