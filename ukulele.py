from pychord import Chord
from pychord.constants import VAL_NOTE_DICT
import itertools

#chords = ['A', 'Am', 'C', 'D', 'Dm', 'Em', 'F', 'F#m', 'G']
#secondary_chords = ['E', 'Bm', 'B','Bb', 'C#m', 'F#', 'Gm']

chords = ['Am', 'C', 'D', 'Em', 'F', 'G']
secondary_chords = ['A', 'E', 'Bm', 'B','Bb', 'C#m', 'Dm', 'F#', 'F#m', 'Gm', 'Cm', 'Eb', 'Dsus2', 'Dsus4', 'Asus2', 'Asus4', 'A5', 'D5', 'G5', 'E5', 'C5',  'B5', 'F5', 'F#5','Gsus4', 'Csus4']
#secondary_chords = ['A', 'E', 'Bm', 'B', 'Dm', 'F#m', 'Bb', 'D7', 'F#', 'A7', 'C#m', 'G7', 'E7', 'Em7', 'B7', 'Gm', 'Am7', 'Eb', 'C7', 'Cadd9', 'Cm', 'C#', 'Dsus2', 'Fm', 'G#', 'G#m', 'Bm7', 'Dm7', 'Ab', 'Dsus4', 'Asus2', 'FM7', 'CM7', 'GM7', 'D#', 'F#m7', 'A5', 'D5', 'Bbm', 'F#7', 'DM7', 'Db', 'F7', 'A#', 'Gsus4', 'G5', 'Gm7', 'C#m7', 'D#m', 'AM7', 'E5', 'C#7', 'Gb', 'Cm7', 'Csus4', 'C5', 'A7sus4', 'Ebm', 'B5', 'Bb7', 'Fm7', 'EM7', 'Dadd9', 'F5', 'G#m7', 'Bsus4', 'G#7', 'A#m', 'Aadd9', 'Bsus2', 'Gadd9', 'Fadd9', 'Abm', 'BbM7', 'Em6', 'Eb7', 'Fsus4', 'Am6', 'D#7', 'F#5', 'D7sus4', 'Dbm', 'D4', 'EbM7', 'Bb5', 'Bbm7', 'E7sus4', 'E2', 'D#m7', 'Gbm', 'BM7', 'A4', 'C#5', 'B7sus4', 'Ab7', 'G4', 'Gm6', 'B2', 'A#7', 'Eb5', 'G7sus4', 'Dm6', 'Bb6', 'Ebsus2', 'G#5', 'C#dim', 'AbM7', 'E4', 'Fdim', 'F#dim', 'Gaug', 'Cdim', 'Ebm7', 'D#dim', 'Fm6', 'Gdim', 'Bdim', 'G#sus4', 'Abm7', 'C#sus4', 'A#m7', 'G#dim', 'Em/F#', 'Edim', 'Ddim', 'Bbdim', 'Eaug', 'C4', 'C7sus4', 'F#7sus4', 'Caug', 'F4', 'Db7', 'Bm6', 'Aaug', 'DbM7', 'Ab5', 'Adim', 'Cm6', 'Faug', 'Cb', 'D/Bb', 'D#5', 'D#M7', 'A#dim', 'AmM7', 'A#5', 'EmM7', 'F#M7', 'F#add9', 'Dbsus2', 'Badd11', 'F7sus4', 'Bb2', 'Gb5', 'A#M7', 'Ebdim', 'Ab/Bb', 'Absus2', 'Bbaug', 'Daug', 'DmM7', 'G#M7', 'Gb7', 'C#add9', 'Db/Eb', 'Bbm6', 'E/Bb', 'GbM7', 'Bb/Eb', 'C#M7', 'A#sus4', 'Ab7sus4', 'G/Bb', 'F#m6', 'Abm6', 'Dbsus4', 'F#4', 'A/Bb', 'G#sus2', 'Bb7sus4', 'G5/F#', 'G#m6', 'Db5', 'C#m6', 'Dbm7', 'G#6', 'F#mM7', 'C#7sus4', 'G#4', 'Eb/Ab', 'G/C#', 'E5/D#', 'Abdim', 'C/C#', 'C/F#', 'Eb7sus4', 'G#7sus4', 'Fm/Bb', 'Ebadd9', 'C/G#', 'D#6', 'D#add9', 'Dbdim', 'Gbm7', 'D/D#', 'Gbdim', 'Am/D#', 'Adim/C#', 'Bdim/D#', 'Dsus2/Bb', 'G/G#', 'G#mM7', 'C/D#', 'A#4', 'Bm/C#', 'Eb/F#', 'Dbm6', 'Bb/Db', 'Gbsus4', 'EbmM7', 'Ab/C#', 'Am/A#', 'C#/F#', 'Edim/C#', 'A#sus2', 'D#/F#', 'D/G#', 'C5/Bb', 'F/G#', 'A#/F#', 'C#mM7', 'Db7sus4', 'CbM7', 'A/Eb', 'FmM7', 'Em/G#']


num_str = 3
max_fingers = 4
max_diff = 3
max_fret = 7
fold_voicing = True

def comps(chord):
    components = Chord(chord).components(visible=False)
    if fold_voicing:
        return sorted(set([n%12 for n in components]))
    return components

for chord in chords:
    print(chord, Chord(chord).components(), comps(chord))

def way_len(way):
    pos = [w for w in way if w]
    return len(pos), max(max(pos)-min(pos),1) if pos else 1, max(way), -(min(pos) if pos else max_fret+1)

def find_all(chord, strings, strict=True):
    chord = comps(chord)
    if len(chord)==num_str-2:
        all_chords = [a for n in chord for m in chord for a in itertools.permutations(chord+[n]+[m])]
    elif len(chord)==num_str-1:
        all_chords = [a for n in chord for a in itertools.permutations(chord+[n])]
    elif len(chord)==num_str:
        all_chords = itertools.permutations(chord)
    elif strict:
        raise Exception('len(chord)=%d but num_str=%d'%(len(chord),num_str))
    else:
        return []
    all_chords = set(all_chords)
    all_ways = set()
    for c in all_chords:
        if all(c[i] in strings[i] for i in range(num_str)):
            candidate = tuple(strings[i].index(c[i]) for i in range(num_str))
            pos = [n for n in candidate if n]
            if not pos or (len(pos)<=max_fingers and max(pos)-min(pos)<=max_diff):
                all_ways.add(candidate)
    return sorted([(way, way_len(way)) for way in all_ways], key=lambda x: x[1])

def find_min(chord, strings, strict=True):
    all_ways = find_all(chord, strings, strict)
    return [way for way in all_ways if way[1]==all_ways[0][1]]

def notes(numbers, deltas=None):
    if deltas is None:
        return [VAL_NOTE_DICT[number][0] for number in numbers]
    return [VAL_NOTE_DICT[(number+delta)%12][0]+'+'*((number+delta)//12) for number,delta in zip(numbers,deltas)]

all_results = []
for i in range(12):
    for j in range(i+1):
        for k in range(j+1):
            for l in range(k+1 if num_str==4 else 1):
                if num_str == 4:
                    tuning= (l, k, j, i)
                else:
                    tuning = (k, j, i)
                if len(set(tuning))<len(tuning)-1:
                    continue
                strings = [[(a%12 if fold_voicing else a) for a in (range(n,n+max_fret+1))] for n in tuning]
                have = True
                tuning_max_fingers = 0
                tuning_max_diff = 0
                tuning_max_fret = 0
                tuning_min_fret = max_fret+1
                zero = 0
                one = 0
                two = 0
                two_far = 0
                three = 0
                other = 0
                zero_chords = []
                one_chords = []
                two_chords = []
                two_far_chords = []
                three_chords = []
                other_chords = []
                tab = {}
                for chord in chords:
                    #print(chord, Chord(chord).components(), comps(chord))
                    best = find_min(chord,strings)
                    if not best:
                        have = False
                        break
                    tab[chord] = [(way[0], notes(tuning, way[0])) for way in best]
                    if len(tab[chord])==1:
                        tab[chord] = tab[chord][0]
                    fingers, diff, hi_fret, neg_lo_fret = best[0][1]
                    tuning_max_fingers = max(tuning_max_fingers, fingers)
                    tuning_max_diff = max(tuning_max_diff, diff)
                    tuning_max_fret = max(tuning_max_fret, hi_fret)
                    tuning_min_fret = min(tuning_min_fret, -neg_lo_fret)
                    if fingers == 0:
                        zero += 1
                        zero_chords.append(chord)
                    elif fingers == 1:
                        one += 1
                        one_chords.append(chord)
                    elif fingers == 2 and diff<=1:
                        two += 1
                        two_chords.append(chord)
                    elif fingers == 2 and diff==2:
                        two_far += 1
                        two_far_chords.append(chord)
                    elif fingers == 3 and diff<=2:
                        three += 1
                        three_chords.append(chord)
                    else:
                        other += 1
                        other_chords.append(chord)
                sec_count = 0
                sec_score = 0
                for chord in secondary_chords:
                    best = find_min(chord, strings, strict=False)
                    if not best:
                        continue
                    tab[chord] = [(way[0], notes(tuning, way[0])) for way in best]
                    if len(tab[chord])==1:
                        tab[chord] = tab[chord][0]
                    sec_count += 1
                    fingers, diff, hi_fret, neg_lo_fret = best[0][1]
                    if fingers == 0:
                        sec_score += 5
                        zero_chords.append(chord)
                    elif fingers == 1:
                        sec_score += 4
                        one_chords.append(chord)
                    elif fingers == 2 and diff <= 1:
                        sec_score += 3
                        two_chords.append(chord)
                    elif fingers == 2 and diff == 2:
                        sec_score += 2
                        two_far_chords.append(chord)
                    elif fingers == 3 and diff <= 2:
                        sec_score += 1
                        three_chords.append(chord)
                    else:
                        other_chords.append(chord)
                if have:
                    all_results.append([notes(tuning), tuning, tuning_max_fingers, tuning_max_diff, tuning_max_fret, tuning_max_fret-tuning_min_fret, zero, one, two, two_far, three, other, sec_count, sec_score, zero_chords, one_chords, two_chords, two_far_chords, three_chords, other_chords, sorted(tab.items())])

#for a in sorted(all_results, key=lambda x:(x[6]+x[7]+x[8]+x[9],x[6]+x[7]+x[8],x[6]+x[7],x[6],x[9],-x[2],-x[3],-x[4], -x[5], x[12], x[13], x[1])):
for a in sorted(all_results, key=lambda x: (x[6] + x[7] + x[8], x[6] + x[7], x[6], x[8], x[9], -x[2], -x[3], -x[4], -x[5], x[12], x[13], x[1])):
    print(a)
