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
contains a class
Created on Mar 3, 2014

@author: joro



'''


import os
import sys
from SymbTrParser2 import SymbTrParser2
from PhonetizerMakam import Phonetizer

# trick to make terminal NOT assume ascii
reload(sys).setdefaultencoding("utf-8")


import codecs

# from utils.Utils import writeListToTextFile


# 
# COMPOSITION_NAME = 'muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik'
# COMPOSITION_NAME = 'huseyni--sarki--turkaksagi--hicran_oku--sevki_bey'
# 
# PATH_TEST_DATASET='/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data/'
# PATH_TEST_DATASET = '/Volumes/IZOTOPE/sertan_sarki/'

class MakamScore():
    '''
    classdocs
    '''


##################################################################################

    def __init__(self, pathToSymbTrFile, sectionMetadata):
        '''
        Constructor
        
        '''
        self.compositionName = os.path.splitext(pathToSymbTrFile)[0]
        
        ''' lyrics divided into sectons.
        # e.g. "nakarat" : [ word1 word2 ] '''
        
        self._loadSectionsAndSyllablesFromSymbTr(pathToSymbTrFile, sectionMetadata)
        
        self._lyricsSections2GroupsSimilarMElody()
        
        # pats to individual ..txt lyrics files. 
        self.pathsTolyricSectionFiles = []
        
      
  ##################################################################################

    def _loadSectionsAndSyllablesFromSymbTr(self, pathToSymbTrFile, sectionMetadata):
        '''
        parses symbTr file. Reads lyrics, 
        reads section names
        groups together section names and lyrics 
        '''
        self.symbTrParser = SymbTrParser2(pathToSymbTrFile, sectionMetadata)
       
        # list of Word object
        self.symbTrParser.syllables2Lyrics()
        
       
        
     
            
            
    def getLyricsForSection(self, melodicStructure):
        '''
        convenience getter. 
        takes first appearance of melodicStructure
        '''
        lyrics = None

        #deprecated 
        #replace with sectionAnno.scoreSection.lyrics

#         for section in self.symbTrParser.sections:
#             if section.melodicStructure == melodicStructure:
#                 lyrics = section.lyrics
#                 break
#         if not lyrics.listWords:
#             logger.warn("no lyrics for demanded section {} ".format(melodicStructure ))
#             return None
        return lyrics 
    
    
    def _lyricsSections2GroupsSimilarMElody(self):
        '''
        divide into groups with similar melody
        '''
        
        self.groupsSimilarMelody = {}
        
        for idx, section in enumerate(self.symbTrParser.sections):
            if section.name != 'VOCAL_SECTION':
                continue
    
            # first letter used as key in dict
            currMelodicStructLetter = section.melodicStructure[0]
            if currMelodicStructLetter not in self.groupsSimilarMelody: # start a new group
                self.groupsSimilarMelody[currMelodicStructLetter] = [section]
            else:
                if not self.existsInGroup( section): # same melody and lyrics
                    sectionsWithThisName = self.groupsSimilarMelody[currMelodicStructLetter]
                    sectionsWithThisName.append(section)
    
    def existsInGroup(self, section):
    
        currMelodicStructLetter = section.melodicStructure[0]
        
        sectionsInGroup = self.groupsSimilarMelody[currMelodicStructLetter]
        for sectionInGr in sectionsInGroup:
            if sectionInGr.melodicStructure == section.melodicStructure and sectionInGr.lyricStructure == section.lyricStructure:
                    return 1
        return 0
    
    
    def getProbableSectionsForMelodicStructure(self, querySectionLink):
        
        ''' get list with similar melodies and diff lyrics 
        (exlude same lyricsStructure)'''
        # B? -> B 
        melodicStructLetter = querySectionLink.melodicStructure[0]
        
        if melodicStructLetter not in self.groupsSimilarMelody:
            sys.exit("section {} not in metadata".format(querySectionLink.melodicStructure))
        
        return self.groupsSimilarMelody[melodicStructLetter]

    def getSectionsSameLyrics(self, querySection, listSections):
        '''
        get subset with  lyrics same as querySection
        '''
        sectionsSameLyrics = [section for section in listSections if section.lyricStructure == querySection.lyricStructure]
        return sectionsSameLyrics
        
  
   ##################################################################################
    def printSectionsAndLyrics(self):
        '''
        utility method to print all lyrics that are read from symbTr
        '''
        for currSection in self.symbTrParser.sections:
    
            print '\n' + str(currSection.melodicStructure) + ' ' + str(currSection.lyricStructure)

            print currSection.lyrics
#             for word in  currSection[1]:
#                 print word.__str__().encode('utf-8','replace')
        

#     def serializePhonemesForSection(self, whichSection, outputFileName):
#         '''
#         list of all phonemes. print to file @param outputFileName
#         '''    
#         lyrics = self.getLyricsForSection(whichSection)
#         if not lyrics:
#             sys.exit("no lyrics")
#         
#         writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileName )
#         return lyrics.phonemesNetwork
    
            
        
        
    def printSyllables(self, whichSection):
        '''
        debug: print syllables 
        '''
        
        lyrics = self.getLyricsForSection(whichSection)
        if not lyrics:
            sys.exit("no lyrics")
            
        lyrics.printSyllables
        
     
               




def loadMakamScore2(symbtrtxtURI, sectionMetadata):
    '''
    same as loadLyrics, but return MakamScore, so that all lyrics can be shown if needed
    '''
    
    lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'grapheme2METUphonemeLookupTable')

    Phonetizer.initLookupTable(False,  lookupTableURI)
    
    makamScore = MakamScore(symbtrtxtURI, sectionMetadata )
    return makamScore   

  
  
def printMakamScore(ScoreURI, sectionMetadata):
        '''
        
        Paramters:
        ScoreURI - full URI of symbTR file
        sectionMetadata - dict with sections. 
        
        '''
            
#         
#         ScoreURI = URI_dataset + compositionName + '/' + compositionName + '.txt'
#         URISectionsMetadata = URI_dataset + compositionName + '/' + compositionName + '.sectionsMetadata.json'
        makamScore = loadMakamScore2(ScoreURI, sectionMetadata)
        makamScore.printSectionsAndLyrics()
        
        print '---------------------------------------------\n'
        
        ####### print groups with similar melody 
        print 'groupsSimilarMelody:'
        for group in makamScore.groupsSimilarMelody:
          print group + ':'
          for y in makamScore.groupsSimilarMelody[group]:
            print y
        print '---------------------------------------------\n'

        ####### print probable sections
        # print '---------------------------------------------\n'
        # sections = makamScore.getProbableSectionsForMelodicStructure('B1')
        # if sections:
        #     for section in sections:
        #         print section.__str__()
        
        # print '---------------------------------------------\n'
        # print '---------------------------------------------\n'
        # print '---------------------------------------------\n'     
           
