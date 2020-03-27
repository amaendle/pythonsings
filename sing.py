from voxpopuli import Voice, BritishEnglishPhonemes, GermanPhonemes, FrenchPhonemes, SpanishPhonemes
import os
import re

# If it does not work, probably espeak or mbroli or the chosen voices are not installed correctly:
# Make sure that espeak can find the files for the chosen voices in
# 1.) "eSpeak\espeak-data\voices\mb"
# 2.) "eSpeak\espeak-data\mbrola"
# To check if espeak works e.g. with the voice "de2" you can use the console: 
# >  espeak -s 160 -p 50 --pho -q -v mb/mb-de2 "Hallo Welt"
# More information about the used packages: 
# https://github.com/hadware/voxpopuli
# https://github.com/numediart/MBROLA
# https://github.com/espeak-ng/espeak-ng
# If you are running windows and don't want to compile the mbroli.exe you can find it on:
# https://web.archive.org/web/20190714175301/http://tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html
# https://github.com/numediart/MBROLA#on-msdoswindows

# sample code for creating waves diretly from text
#voice = Voice(lang="fr")
#wav = voice.to_audio('"salut c\'est cool"')
#with open("salut2.wav", "wb") as wavfile:
#    wavfile.write(wav)

# Adapt the locations of mbroli, espeak and the voices, if necessary
Voice.mbrola_voices_folder = 'C:\\Users\\maendle\\.mbrola'
Voice.mbrola_binary ='mbrola'
Voice.espeak_binary ='espeak'

# create a set of vowels
VOWELS = GermanPhonemes.VOWELS.union({'@','6','_','{'})
VOWELS = VOWELS.union(BritishEnglishPhonemes.VOWELS)
VOWELS = VOWELS.union(FrenchPhonemes.VOWELS)
VOWELS = VOWELS.union(SpanishPhonemes.VOWELS)

# removes pauses 
def unpause(phonemes_list):
    for num in reversed(range(len(phonemes_list))):
        if phonemes_list[num].name in{'_'}:
            del phonemes_list[num] #phonemes_list.remove(el)
    return phonemes_list

# translates text to phonemes, removes natural pauses and adds pauses add the location of the "|" character in text
def txt2phonemes(text):
    spltext = str.split(text,'|')
    empty = voice._str_to_phonemes('""')
    del empty[1:]
    for num, itxt in enumerate(spltext, start=0):
        if num==0:
            phonemes_list = unpause(voice._str_to_phonemes('"'+itxt+'"'))
        else:
            phonemes_list += empty
            phonemes_list += unpause(voice._str_to_phonemes('"'+itxt+'"'))
    return phonemes_list
	
## remove double pause
#for num, el in enumerate(phonemes_list, start=1):
#    if phonemes_list[num-1].name in {'_'}:
#        if el.name in{'_'}:
#            phonemes_list.remove(el)

# gets frequency from note name 
def getFrequency(note, octave=4):
    transp = 0
    if 0 < len(note):
        if note[0] == '+':
            transp += 12
            note = note[1:]
        if note[0] == '-':
            transp -= 12
            note = note[1:]
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    if note.upper() not in notes:
        return('_')
    keyNr = notes.index(note.upper())
    if keyNr < 3:
        keyNr += 12
    keyNr += ((octave-1)*12)+1 +transp
    return round(440 * 2 ** ((keyNr- 49) / 12))

# gets time in ms from note length
def getLength(notelen, len=1000):
    if notelen 	== '':
        notelen = 1
    else:
        if  '.' in notelen:
            notelen = re.split('\..*', notelen)[0] 
            return round(1.5*(len/int(notelen)))
        notelen = int(notelen)
    return round(len/notelen)	

def sing(text, notes, voice, fname=None):
    phonemes_list = txt2phonemes(text)
	# create note array from frequencies and lengths from notes
    notearr = [re.split('(\d*\.*$)', pcode, maxsplit=1) for pcode in notes.split(' ')]
    for num, note in enumerate(notearr, start=0):
        notearr[num] = [getFrequency(note[0]),getLength(note[1])]
    print(notearr)
    vnum = 0
    for num, phoneme in enumerate(phonemes_list, start=0): #phoneme list object inherits from the list object
        if len(notearr) <= vnum:
            print("not enouch notes for the recognized number of syllables")
            break
        if phoneme.name == '_' or (phoneme.name in VOWELS and len(phoneme.pitch_modifiers)>0): #GermanPhonemes.VOWELS.union({'@','6','_'}):
            #print("is vowel")
            #print(len(phoneme.pitch_modifiers))
            phoneme.duration = notearr[vnum][1]
            for pnum, pimo in enumerate(phoneme.pitch_modifiers,start=0):
                if notearr[vnum][0] != '_':
                    phoneme.pitch_modifiers[pnum] = (pimo[0],notearr[vnum][0])
            vnum += 1
        #print(phoneme)
        #print("---")
    print(phonemes_list)
    if fname != None:
        voice.to_audio(phonemes_list, fname)
    voice.say(phonemes_list)
	
# Sing in German: "Alle meine Entchen"
voice = Voice(lang="de", voice_id=2)	
text = "Alle meine Entchen schwimmen auf dem See. | schwimmen auf dem See. | Köpfchen in das Wasser. Schwänzchen in die Höh."
notes = 'd4 e4 f4 g4 a2 a2 b4 b4 b4 b4 a2 4 b4 b4 b4 b4 a2 4 g4 g4 g4 g4 f2 f2 a4 a4 a4 a4 d2' 
sing(text, notes, voice, "entchen.wav")

# Sing "Atemlos"
voice = Voice(lang="de", voice_id=5)	
text = "Atemlos durch die Nacht | bis ein neuer Tag erwacht."
notes = '+c4 b4 a2 a4 g8 e2 8 e4 g8 g4. -b8 b4. b4 c4.'
# if you don't specify a filename, you sing without saving:
sing(text, notes, voice) 

# Sing in French: "Frère Jacques"
voice = Voice(lang="fr", voice_id=1)	
# in the text Jacques is changed by Jacquès and matines by matinès for the purpose of singing..
text = "Frèrè Jacquès, Frèrè Jacquès, dormez-vous, dormez-vous? Sonnez les matinès, sonnez les matinès, Ding, ding, dong. Ding, ding, dong."
notes = 'f4 g4 a4 f4 f4 g4 a4 f4 a4 b4 +c2 a4 b4 +c2 +c8 +d8 +c8 b8 a4 f4 +c8 +d8 +c8 b8 a4 f4 f4 c4 f2 f4 c4 f2'
sing(text, notes, voice, "jaques.wav") 

# Sing in English: "Twinkle, Twinkle, Little Star"
VOWELS = VOWELS.union({'5'})
voice = Voice(lang="en", voice_id=1)	
text = "Twinkle, twinkle, little star, How we wonder what you are. Up above the world so high, Like a diamond in the sky. Twinkle, twinkle, little star, How we wonder what you are."
notes = 'c4 c4 g4 g4 a4 a4 g2 f4 f4 e4 e4 d4 d4 c2 g4 g4 f4 f4 e4 e4 d2 g4 g4 f8 f8 f4 e4 e4 d2 c4 c4 g4 g4 a4 a4 g2 f4 f4 e4 e4 d4 d4 c2'
sing(text, notes, voice, "twinkle.wav") 

# Sing in Spanish: "La cucaracha"
VOWELS = VOWELS.union({'5'})
voice = Voice(lang="es", voice_id=1)	
text = "La cucaracha, la cucaracha. | Ya no puede caminar. | Porque no tiene, porque le falta, | marihuana que fumar."
notes = 'c8 c4 c4 f4 a8 c8 c8 c8 f4 a4 4 f8 f8 e8 e8 d8 d8 c4 8 c8 c8 c8 e4 g8 c8 c8 c8 e4 g4 4 +c8 +d8 +c8 a#8 a8 g8 f8'
sing(text, notes, voice, 'cucaracha.wav') 

#audio = voice._phonemes_to_audio(phonemes_list)	
