from pychord import Chord
from pychord.constants import VAL_NOTE_DICT
import itertools

#chords = ['A', 'Am', 'C', 'D', 'Dm', 'Em', 'F', 'F#m', 'G']
#secondary_chords = ['E', 'Bm', 'B','Bb', 'C#m', 'F#', 'Gm']

chords = ['Am', 'C', 'D', 'Em', 'F', 'G']
secondary_chords = ['A', 'E', 'Bm', 'B','Bb', 'C#m', 'Dm', 'F#', 'F#m', 'Gm', 'Cm', 'Eb', 'Dsus2', 'Dsus4', 'Asus2', 'Asus4', 'A5', 'D5', 'G5', 'E5', 'C5',  'B5', 'F5', 'F#5','Gsus4', 'Csus4']

num_str = 3
max_fingers = 4
max_diff = 3
max_fret = 7
inversion = True

def comps(chord):
    components = Chord(chord).components(visible=False)
    if inversion:
        return sorted(set([n%12 for n in components]))
    return components

for chord in chords:
    print(chord, Chord(chord).components(), comps(chord))

def way_len(way):
    pos = [w for w in way if w]
    return len(pos), max(max(pos)-min(pos),1) if pos else 1, max(way), -(min(pos) if pos else max_fret+1)

def find_all(chord, strings):
    chord = comps(chord)
    if len(chord)==num_str-2:
        all_chords = [a for n in chord for m in chord for a in itertools.permutations(chord+[n]+[m])]
    elif len(chord)==num_str-1:
        all_chords = [a for n in chord for a in itertools.permutations(chord+[n])]
    elif len(chord)==num_str:
        all_chords = itertools.permutations(chord)
    else:
        raise Exception('len(chord)=%d but num_str=%d'%(len(chord),num_str))
    all_chords = set(all_chords)
    all_ways = set()
    for c in all_chords:
        if all(c[i] in strings[i] for i in range(num_str)):
            candidate = tuple(strings[i].index(c[i]) for i in range(num_str))
            pos = [n for n in candidate if n]
            if not pos or (len(pos)<=max_fingers and max(pos)-min(pos)<=max_diff):
                all_ways.add(candidate)
    return sorted([(way, way_len(way)) for way in all_ways], key=lambda x: x[1])

def find_min(chord, strings):
    all_ways = find_all(chord, strings)
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
                strings = [[(a%12 if inversion else a) for a in (range(n,n+max_fret+1))] for n in tuning]
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
                    best = find_min(chord, strings)
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
