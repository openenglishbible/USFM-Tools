#!/bin/bash

###############
#
#	Functions
#
###############

make-tmp () 
{
	echo Making tmp
	mkdir tmp	
}

clean-tmp () 
{
	echo Cleaning tmp
	rm -r tmp	
}

OEBDIR=/Users/russellallen/Dropbox/oeb/Open-English-Bible/final-usfm
#OEBDIR=/Users/russellallen/Documents/OEB/translations/usfm/web
#OEBDIR=/Users/russellallen/Dropbox/oeb/Open-English-Bible/sources/tcnt/usfm

###############
#
#	Setup
#
###############

rm -r built/*

###############
#
#	US NT
#
###############

usnt() {
	make-tmp
	cp $OEBDIR/us/4* tmp
	cp $OEBDIR/us/5* tmp
	cp $OEBDIR/us/6* tmp
	#python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=html       --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=reader     --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-US --oeb
	clean-tmp
}

###############
#
#	Cth NT
#
###############

cthnt() {
	make-tmp
	cp $OEBDIR/cth/4* tmp
	cp $OEBDIR/cth/5* tmp
	cp $OEBDIR/cth/6* tmp
	python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-Cth --oeb
	python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-NT-$ID-Cth --oeb
	clean-tmp
}

###############
#
#	Simple All US
#
###############

simple-all-us() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=html       --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
}

###############
#
#	PDF All US
#
###############

pdf-all-us() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
}

###############
#
# All US
#
###############

html-all-us() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=html    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
}

csv-all-us() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=csv    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
}

md-all-us() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=md    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
}

reader-all-cth() {
	make-tmp
	cp $OEBDIR/cth/* tmp
	python transform.py --target=reader --usfmDir=tmp/ --builtDir=built/ --name=oeb-cth-dev --oeb
	clean-tmp
}

###############
#
#	Full Release 
#
###############

all() {
	make-tmp
	cp $OEBDIR/us/* tmp
	python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=html       --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=reader     --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=csv        --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-US --oeb
	clean-tmp
	make-tmp
	cp $OEBDIR/cth/* tmp
	python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-Cth --oeb
	python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-Cth --oeb
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-Cth --oeb
	python transform.py --target=csv        --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-Cth --oeb
	python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-All-$ID-Cth --oeb
	clean-tmp
}

release() {
	make-tmp
    cp $OEBDIR/us/00* tmp    
    cp $OEBDIR/us/08* tmp
    cp $OEBDIR/us/17* tmp
    cp $OEBDIR/us/19* tmp
	cp $OEBDIR/us/4* tmp
	cp $OEBDIR/us/5* tmp
	cp $OEBDIR/us/6* tmp
	#python transform.py --target=context   --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb --order=normal
	#python transform.py --target=html       --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb
	python transform.py --target=reader     --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-US --oeb
	clean-tmp
	make-tmp
    cp $OEBDIR/cth/00* tmp    
    cp $OEBDIR/cth/08* tmp
    cp $OEBDIR/cth/17* tmp
    cp $OEBDIR/cth/19* tmp
	cp $OEBDIR/cth/4* tmp
	cp $OEBDIR/cth/5* tmp
	cp $OEBDIR/cth/6* tmp
	#python transform.py --target=context    --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=md         --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb --order=normal
	#python transform.py --target=csv        --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb
	#python transform.py --target=ascii      --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb
	python transform.py --target=reader     --usfmDir=tmp/ --builtDir=built/ --name=OEB-$ID-Cth --oeb
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
	cp $OEBDIR/us/$BOOKFILE tmp
	python transform.py --target=lout --usfmDir=tmp/ --builtDir=built/ --name=OEB-$BOOKNAME-Current-US --oeb
	clean-tmp
}

build-book-tex () 
{
	make-tmp
	cp $OEBDIR/us/$BOOKFILE tmp
	python transform.py --target=context --usfmDir=tmp/ --builtDir=built/ --name=OEB-$BOOKNAME-Current-US --oeb
	clean-tmp
}

build-book-text () 
{
	make-tmp
	cp $OEBDIR/us/$BOOKFILE tmp
	python transform.py --target=ascii --usfmDir=tmp/ --builtDir=built/ --name=OEB-$BOOKNAME-Current-US --oeb
	clean-tmp
}

build-book-md () 
{
	make-tmp
	cp $OEBDIR/us/$BOOKFILE tmp
	python transform.py --target=md --usfmDir=tmp/ --builtDir=built/ --name=OEB-$BOOKNAME-Current-US --oeb
	clean-tmp
}

build-book-singlehtml () 
{
	make-tmp
	cp $OEBDIR/us/$BOOKFILE tmp
	python transform.py --target=singlehtml --usfmDir=tmp/ --builtDir=built/ --name=OEB-$BOOKNAME-Current-US --oeb
	clean-tmp
}

buildbooks() 
{
	BOOKFILE=08-Ruth.usfm
	BOOKNAME=Ruth
	build-book

	BOOKFILE=17-Esther.usfm
	BOOKNAME=Esther
	build-book

	BOOKFILE=19-Psalms.usfm
	BOOKNAME=Psalms
	build-book

	BOOKFILE=27-Daniel.usfm
	BOOKNAME=Daniel
	build-book

	BOOKFILE=29-Joel.usfm
	BOOKNAME=Joel
	build-book

	BOOKFILE=31-Obadiah.usfm
	BOOKNAME=Obadiah
	build-book

	BOOKFILE=32-Jonah.usfm
	BOOKNAME=Jonah
	build-book

	BOOKFILE=34-Nahum.usfm
	BOOKNAME=Nahum
	build-book

	BOOKFILE=35-Habakkuk.usfm
	BOOKNAME=Habakkuk
	build-book

	BOOKFILE=36-Zephaniah.usfm
	BOOKNAME=Zephaniah
	build-book

	BOOKFILE=37-Haggai.usfm
	BOOKNAME=Haggai
	build-book

	BOOKFILE=38-Zechariah.usfm
	BOOKNAME=Zechariah
	build-book
}


###############
#
#	Actions
#
###############

#usnt
#cthnt
#buildbooks
#simple-all-us
#csv-all-us

#BOOKFILE=17-Esther.usfm
#BOOKNAME=Esther
#build-book-text

#ID=2014.11
#release
#usnt
#all-nt-psalms
#all

pdf-all-us


