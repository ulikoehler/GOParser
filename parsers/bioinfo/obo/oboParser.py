#! /usr/bin/env python

# 
# This is a obo file parser
# 

# imports
import urllib

# obo file parsing class
class OboParser():
    
    """ This is the main obo parser class """
    
    def __init__(self, oboContent, calcTree = True):
        
        """ Initalize an oboparser by the obocontent. """
        
        # the main attributes from the parsed file
        self.header = {}
        self.stanzas = {}
        
        # split the lines
        lineno, lines = 1, oboContent.split("\n")
        
        # decode a line with escaped characters
        # Note, that the obo format escapes some extraordinary characters like :, [ etc.
        def _decodeOboSpecialCharacters(str):
            str.replace("\\n", "\n")
            str.replace("\\W", " ")
            str.replace("\\t", "\t")
            str.replace("\\:", ":")
            str.replace("\\,", ",")
            str.replace("\\\"", "\"")
            str.replace("\\\\", "\\")
            str.replace("\\(", "(")
            str.replace("\\)", ")")
            str.replace("\\[", "[")
            str.replace("\\]", "]")
            str.replace("\\{", "{")
            str.replace("\\}", "}")
            return str
        
        # get tag values from lines
        # the result is a list of all (tag, value, comment) tag-value-pairs
        def _parseTagValue(lines):
            tags, escaped, plines = [], False, []
            # concat newline escaped lines
            escaped = False
            for line in lines:
                # check weather to append at the last line (escaped newline)
                if escaped:
                    # remove escaped character and append line
                    plines[-1] = plines[-1][:-1] + line
                    escaped = False
                # ok, just add the line as it is
                else:
                    plines.append(line)
                if line.endswith("\\"):
                    # ok, concat the following line to this one
                    escaped = True
            # analyse all tag-value-pairs
            for line in plines:
                # skip the processing of empty lines
                if line.strip() == "":
                    continue
                # ok, get the name, the value and the comment of the tag-value-pair
                attrName = _decodeOboSpecialCharacters(line[:line.find(":")].strip())
                attr, attrVal, attrCom = line[line.find(":")+1:], None, None
                if attr.find("!") == -1:
                    attrVal = _decodeOboSpecialCharacters(attr.strip())
                else:
                    attrVal = _decodeOboSpecialCharacters(attr[:attr.find("!")].strip())
                    attrCom = _decodeOboSpecialCharacters(attr[attr.find("!")+1:].strip())
                tags.append((attrName, attrVal, attrCom))
            return tags
        
        # analyse the header of the obo file
        def _analyseHeader(self, lines):
            # analyse the lines of the header
            for tag in _parseTagValue(lines):
                try:
                    self.header[tag[0]].append((tag[1], tag[2]))
                    # check weather to import an obo by url too
                    if tag[0] == "import":
                        # ok, ok, I hope this computer has an internet connection
                        self.header[tag[0]].append(OboParser.readUrl(tag[1], calcTree))
                except KeyError:
                    self.header[tag[0]] = [(tag[1], tag[2])]
        
        # analyse a stanza of the obo file
        def _analyseStanza(self, lines):
            # check for the stanza name and previous saved stanzas
            stanzaName, stanza = lines[0][1:-1], []
            try:
                # get previous saved stanzas
                stanza = self.stanzas[stanzaName]
            except KeyError:
                # ok, there had been no previous saved stanzas
                self.stanzas[stanzaName] = stanza
            # append current stanza
            curr = {}
            for obj in _parseTagValue(lines[1:]):
                try:
                    curr[obj[0]].append((obj[1], obj[2]))
                except KeyError:
                    curr[obj[0]] = [(obj[1], obj[2])]
            stanza.append(curr)
        
        # lines processing
        def _processlines(self, linesToAnalyse, passedHeader, lineno):
            if passedHeader:
                _analyseStanza(self, linesToAnalyse)
            else:
                _analyseHeader(self, linesToAnalyse)
        
        # process all lines
        passedHeader, linesToAnalyse = False, []
        for line in lines:
            # if the line starts with an [, this means a new stanza
            # begins, so analyse the previous read in stanza
            if line.startswith("["):
                _processlines(self, linesToAnalyse, passedHeader, lineno)
                linesToAnalyse, passedHeader = [ line ], True
            else:
                linesToAnalyse.append(line)
            lineno += 1
        # process the last (probably a stanza)
        _processlines(self, linesToAnalyse, passedHeader, lineno)
        
        # calculate the treee if necessary
        if calcTree:
            self.calcTree()
    
    # calculate the tree of the obo stanzas
    def calcTree(self, check = True):
        
        """ Calculate a term tree for this obo file """
        
        # skip calculation, if tree already exists (and check)
        if hasattr(self, "tree") and check:
            return
        
        self.tree = {}
        # first check, if an obo tree was imported, so that this tree
        # has to be used in the tree building
        try:
            for oboObj in xrange(1, len(self.headers['import']) + 1, 2):
                oboObj.calcTree(check)
                self.tree.update(oboObj.tree)
        except:
            pass
        
        # ok, now append all stanzas from this file
        for item in self.stanzas["Term"]:
            item['childrens'] = []
            self.tree[item["id"][0][0]] = item
        
        # perfect and now init the childrens (parents already init with is_a)
        for key in self.tree:
            node = self.tree[key]
            try:
                for element in node["is_a"]:
                    self.tree[ element[0] ]['childrens'].append(key)
            except:
                pass
    
    # read in an obo file
    @staticmethod
    def readOboFile(filename, calcTree = True):
        
        """ a shortcut for reading an obo file directly """
        
        with open(filename, "r") as f:
            return OboParser(f.read(), calcTree)
    
    # read the obo from an url
    @staticmethod
    def readUrl(oboUrl, calcTree = True):
        
        """ shortcut for reading an obo file directly from an url """
        
        return OboParser(urllib.urlopen(oboUrl).read(), calcTree)

# test/example usage
if __name__ == "__main__":
    
    """ Example and main test for the obo parser """
    
    import argparse
    parser =  argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="file", required=True, )
    args = parser.parse_args()
    obo = OboParser.readOboFile(args.file)
    print(obo.header)
    print(obo.stanzas)
    print(obo.tree)
