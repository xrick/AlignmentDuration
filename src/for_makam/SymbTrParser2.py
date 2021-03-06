# -*- coding: utf-8 -*-

# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


'''
contains SymbTr Parser class 
 
@author: joro
'''
import os
import sys
from Syllable import Syllable, MINIMAL_DURATION_UNIT
from src.align.Lyrics import Lyrics
from src.align._SymbTrParserBase import _SymbTrParserBase


from src.utilsLyrics.Utilz import  loadTextFile
from src.align.Word import createWord


class SymbTrParser2(_SymbTrParserBase):
    '''
    Parses lyrics from symbTr v 2.0 and Sections from tsv file.
    
    a list of syllables from column 12: soz1/söz1 is parsed. 
    Then concatenated into words if needed 
    TODO: take only section names from tsv file. parse sections from symbTr double s 
    '''


    
    def __init__(self, pathToSymbTrFile, sectionMetadata):
        '''
        Constructor
        '''
        _SymbTrParserBase.__init__(self,pathToSymbTrFile, sectionMetadata)
        
        
   
    
   
   
   ##################################################################################
     
    '''
    load all notes with syllables from symbTr file. 
    ignores all notes with no syllable!
    calculate syllable duration from the associated notes 
    '''

   

    def _loadSyllables(self, pathToSymbTrFile):
        '''
        top-most function
        '''
             
        allLines = loadTextFile(pathToSymbTrFile)
        
        currSyllable = None
        currSyllTotalDuration = None
        
        # skip first line. 
        for  i in range( 1, len(allLines) ):
            
            line = allLines[i]
            line = line.replace(os.linesep,'') # remove end line in an os-independent way 
            line = line.replace('\r','') 
            
            tokens = line.split("\t")
            if len(tokens) < 13:
                print "TOKENS ARE less than needed 13 ";  sys.exit()
            
            # sanity check  MINIMAL_DURATION of embelishments. 
#             hack: change crazy small notes to min duration. it does not matter a lot
            if tokens[7] > MINIMAL_DURATION_UNIT and  tokens[1] == '8':
                tokens[7] = MINIMAL_DURATION_UNIT


            currNoteDuration = float(tokens[6]) / float(tokens[7]) * MINIMAL_DURATION_UNIT
                
            currSyllable, currSyllTotalDuration = self.parseCurrTxtToken(currSyllable, currSyllTotalDuration, tokens, currNoteDuration)
            
            
        #end parsing loop
            
        # store last
        currSyllable.setDurationInMinUnit(currSyllTotalDuration)
        self.listSyllables.append(currSyllable)
    
    


    def parseCurrTxtToken(self, currSyllable, syllTotalDuration, tokens, currDuration):
        '''
        parse  the text: (soz1/söz1 token) containing the  syllable text. discriminate between cases of SAZ and so on
        '''
        currTxtToken = tokens[11]
        
        # skip ARANAGME sections
#         if currTxtToken.startswith(u'ARANA\u011eME') or currTxtToken.startswith(u'ARANAGME'): #             or tokens[1] == '8':             # skip embellishments. they dont count in duration
#             return None,None
        
         # '' (no lyrics at note) so still at same syllable
        if currTxtToken == '' and not (currSyllable is None) and not (syllTotalDuration is None):
            syllTotalDuration = syllTotalDuration + currDuration 
        
        elif currTxtToken.startswith('.'): #still in same _SAZ_ syllable
            if not (currSyllable is None) and not (syllTotalDuration is None) and currSyllable.text ==  "_SAZ_ ":
                syllTotalDuration = syllTotalDuration + currDuration
            
            # new syllable starting with '.'
            else:
                currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(currSyllable, syllTotalDuration, tokens, currDuration)
        
        #  not '' and not '.'   thus new syllable starts
        else:
            currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(currSyllable, syllTotalDuration, tokens, currDuration)
        
      
        return currSyllable, syllTotalDuration        


    
    
    def finishCurrentAndCreateNewSyllable(self, currSyllable, syllTotalDuration, tokens, currDuration):
        '''
        when syllable finished
        '''
        if not (currSyllable is None) and not (syllTotalDuration is None): # save last syllable and duration
            currSyllable.setDurationInMinUnit(syllTotalDuration)
            self.listSyllables.append(currSyllable)
        
        # init next syllable and its duration
        currSyllable = self.createSyllable(tokens)
        syllTotalDuration = currDuration
        return currSyllable, syllTotalDuration



    
    def createSyllable(self, tokens):
        '''
        create new syllable
        distinguish btw vocal syllable and instrumental syllable  
        '''
            
        currTxtToken = tokens[11]
        if currTxtToken.startswith('SAZ') or currTxtToken.startswith('.') or  currTxtToken.startswith(u'ARANA\u011eME') or currTxtToken.startswith(u'ARANAGME'):
            #  indicates end of word, it is stripped later by the code
            currSyllable = Syllable("_SAZ_ ", tokens[0])
        else:
            text = tokens[11].replace('_',' ')
            currSyllable = Syllable(text, tokens[0])
        
        return currSyllable
    
                    
#                         self.listSyllables.append(tupleSyllable)
            
     

       
     ##################################################################################
   
     
     
    def syllables2Lyrics(self): 
        """
        construct wordsList from syllables for all  sections
        use Lyrics and Syllable classes.
        """  
        wordsList = []
              
        for currSection in self.sections:
            
            # double empty space marks section end, but we dont use it for now             
            wordsList = self.syllable2ListWordsOneSection(currSection.startNote, currSection.endNote)
            
            # store lyrics
            currSection.lyrics  = Lyrics(wordsList)            
            
            
          


    def syllable2ListWordsOneSection(self, startNoteNumber, endNoteNumber):
        """
             combine syllables into listWords. use Word and Syllable classes. 
                for one section only .
                add syllables until noteNumber of current Syllable reaches  
            @param endNoteNumber:
             
            @param beginIndex: - beginning current index syllable
        """
        syllablesInCurrWord  = []
        listWords = []
        
        beginIndex = self._findSyllableIndex(startNoteNumber)
        # wrong noteNumber for section begin or no lyrics in section
        if (beginIndex == -1):
            return listWords
        
        
        while (beginIndex <= len(self.listSyllables)-1 # sanity check
                    and self.listSyllables[beginIndex].noteNum <= endNoteNumber ): # while note number associated with syllable is less than last note number in section 
                    
                        currSyllable = self.listSyllables[beginIndex]
                        
                        # construct new word at whitespace
                        if currSyllable.text[-1].isspace():
                            
                            word, syllablesInCurrWord = createWord(syllablesInCurrWord, currSyllable)
                            
                            # ignore SAZ
#                             if not word.text == '_SAZ_':
                            listWords.append(word)
                            
                            #restart counting
                            syllablesInCurrWord = []
                        
                        # still same word    
                        else:
                            syllablesInCurrWord.append(currSyllable)
                            
                            
                        beginIndex = beginIndex + 1
                        
        return listWords
  

    
        
    def _findSyllableIndex(self, noteNumberQuery):
        '''
        find which syllable has  queried note number 
        @param noteNumberQuery:  
        used only for begin syllables
        use binary search
        '''
        lo = 0
        high = len(self.listSyllables)
        
        while lo<high:
            mid = (lo+high)//2
            noteNum = self.listSyllables[mid].noteNum
            if noteNumberQuery < noteNum:
                high = mid
            elif noteNumberQuery > noteNum:
                lo = mid + 1
            else:
                return mid
       
        # no syllable with lyrics (case of lyrics starting after auftakt on istrument at begining of section) => return closest following syllable with lyrics  
      
        return high
             
            
        
        

     

    

#################################################################################

