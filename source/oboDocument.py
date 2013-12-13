#! /usr/bin/env python

###################################################
# OBO Parser for parsing GO/HPO annotation graphs #
# written by: Yann Spoeri, Uli Koehler            #
###################################################

# import all stuff
import oboHeader
import oboStanza
import oboTagValue
import oboTrailingMod

# An obo document is build by a header and multiple stanza elements

class OboDocument():
    
    """ An obo document is basically build by an header element and multiple stanza elements """
    
    def __init__(self, header, stanzas):
        
        """ initalize the obo document by a header element and stanzas """
        
        self.header = header
        self.stanzas = stanzas
    
    @staticmethod
    def parseFileData(data):
        
        """ get an oboDocument by the lines of an obo document file """
        
        pass # TODO
    
    @staticmethod
    def parseFile(fileName):
        
        """ """
        
        with open(fileName, "r") as f:
            return OboDocument.parseFileData(f.read())
    
    
