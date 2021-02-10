# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from netCDF4 import Dataset, chartostring
from ncdump import ncdump
import numpy as np
from NetCDFDecoder import NetCDFDecoder
from ArgoNetCDFBufrEncoder import ArgoNetCDFBufrEncoder
from datetime import datetime
import logging
import getopt
import os
import sys
import pathlib

def usage():
    print("argoNetCDFToBufr Usage")
    print("argoNetCDFToBufr.py -i <inputfile> -o <outputfile>")
    print(" or")
    print("argoNetCDFToBufr.py --ifile <inputfile> --ofile <outputfile>")
    print(" or")
    print("argoNetCDFToBufr.py --help")
    print("\nConverts a NetCDF Argo file to Bufr format")
    pass

def getCommandLine():
    # sort out command line arguments
    inputFile = ""
    outputFile = ""
    try:
      [opts, args] = getopt.getopt(sys.argv[1:],"i:o:d",["ifile=","ofile=", "debug", "help"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(2)
    debug = False
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("--help"):
            usage()
            exit(1)
    if len(inputFile)<1:
        print("Input file must be specified")
        exit(2)
    if len(outputFile)<1:
        print("Output file must be specified")
        exit(2)
    if (len(os.path.splitext(inputFile))==1):
        inputFile += ".nc"
    if (len(os.path.splitext(outputFile))==1):
        outputFile += ".dat"
    print("Reading from ", inputFile)
    print("Output to ", outputFile)
    print("Debug is ", debug)
    return [inputFile, outputFile, debug]

if __name__ == "__main__":
    print ("argoNetCDFToBufr\n")

    [inputFile, outputFile, debug] = getCommandLine()

    if debug:
        level = logging.DEBUG
    else:
        level = logging.NOTSET
    logging.basicConfig(filename='argoNetCDFToBufr.log',filemode='w',level=level)
    logging.info('Starting app...')
    if debug:
        print("Debug is output to ", pathlib.Path().absolute())

    decoder = NetCDFDecoder()
    decoder.loadFile(inputFile)

    # decode into common format
    channels = decoder.decode()

    # encode from common format to bufr
    encoder = ArgoNetCDFBufrEncoder(channels)
    buffer = encoder.getMessage(channels)

    # write to file
    f = open(outputFile, 'wb')
    buffer.tofile(f)
    f.close()
    