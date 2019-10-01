import pymysql.cursors
from pychord import Chord
from collections import Counter
from itertools import chain, combinations
import matplotlib.pyplot as plt
import os

limit_notes = None
fold_voicing = False
top = 20
max_len = 15

def plot(name, data, colors=None, font_size=14, total=False):
    objects, values = zip(*data)
    fig, ax = plt.subplots()
    ax.invert_yaxis()
    ax.axis('off')
    ax.barh(range(len(objects)), values, color=colors, alpha=0.7)
    rects = ax.patches
    offset = ax.get_xlim()[1]*0.02
    try:
        is_pct = all(0<=value<=1 for value in values)
    except:
        is_pct = False
    r = fig.canvas.get_renderer()
    max_text = 0
    for rect, object, value in zip(rects, objects, values):
        text = ax.text(offset, rect.get_y() + rect.get_height() *0.55, object, ha='left', va='center', size=font_size)
        width = rect.get_width()
        text_width = ax.get_xlim()[1]*text.get_window_extent(r).width/ax.get_window_extent(r).width+offset*1.5
        if text_width>max(width,max_text):
            max_text = text_width
    y = 0
    for rect, object, value in zip(rects, objects, values):
        width = rect.get_width()
        prev_y = y
        y = rect.get_y() + rect.get_height() *0.55
        ax.text(max(width,max_text) + offset*1.5, y, '%.1f%%'%(value*100) if is_pct else value, ha='left', va='center', size=font_size)
    fig.suptitle(os.path.basename(name), x=0.55, size=20)
    if total:
        total = sum(values)
        ax.text(offset, y + (y-prev_y)*1.5, 'Total:  ' + ('%.1f%%'%(total*100) if is_pct else str(total)), ha='left', va='center', size=11)
    fig.savefig(name.lower().replace(' ','_')+'.svg')

#note: added the following to QUALITY_DICT in pychord\constants\qualities.py
# ('add2', (0, 2, 4, 7)),
# ('madd2', (0, 2, 3, 7)),
# ('add4', (0, 4, 5, 7)),
# ('madd4', (0, 3, 5, 7)),
# ('m6', (0, 3, 7, 9)),
# ('7sus2', (0, 2, 7, 10)),
# ('madd9', (0, 3, 7, 14)),
# ('6sus2', (0, 2, 7, 9)),
# ('6sus4', (0, 5, 7, 9)),

def fix(chord):
    chord = chord.replace('ADD', 'add').replace('7b', '7-').replace('7#', '7+').replace('dim7', 'dim6').replace('maj7', 'M7').replace('maj9', 'M9').replace('m11', '11').replace('B#','C').replace('E#','F').replace('Cb','B').replace('Fb','E').replace('m#','#m').replace('mb','bm').replace('7m','m7').replace('(', '').replace(')', '')
    if chord.endswith('sus7'):
        chord = chord.replace('sus7', '7sus4')
    if chord.endswith('7sus'):
        chord = chord.replace('7sus', '7sus4')
    elif chord.endswith('sus'):
        chord = chord.replace('sus','5')
    return chord

db = pymysql.connect(host="localhost", user="root", passwd="", db="UltimateGuitarTabs")
cur = db.cursor()

cur.execute("select chords from chords")
instances_per_song = [[fix(chord) for chord in row[0].split(',') if chord] for row in cur.fetchall()]
instances_per_song = [instances for instances in instances_per_song if len(instances)>0]
chords_per_song = [set(instances) for instances in instances_per_song]
count_instances = Counter(chord for instances in instances_per_song for chord in instances)

base_chords_to_comps = {}
bad_chords = {}
fold_chords = {}
seen_comps_to_chords = {}
for chord, cnt in sorted(count_instances.items(), key=lambda x:(-x[1],x[0])):
    try:
        comps = tuple(Chord(chord).components(visible=False))
        if fold_voicing:
            comps = tuple(sorted(set(n%12 for n in comps)))
    except:
        bad_chords[chord] = cnt
        continue
    if comps in seen_comps_to_chords:
        fold_chords[chord] = seen_comps_to_chords[comps]
    else:
        base_chords_to_comps[chord] = comps
        seen_comps_to_chords[comps] = chord

print(sorted(bad_chords.items(), key=lambda x: (-x[1],x[0])))
folded_per_song = [set(fold_chords[chord] if chord in fold_chords else chord for chord in chords) for chords in chords_per_song if all(chord not in bad_chords for chord in chords)]
folded_instances_per_song = [[fold_chords[chord] if chord in fold_chords else chord for chord in instances] for instances in instances_per_song if all(chord not in bad_chords for chord in set(instances))]
print('base chords=%d, folded chords=%d, bad chords=%d, bad songs=%d/%d (%.1f%%) good_songs=%d'%(len(base_chords_to_comps),len(fold_chords),len(bad_chords),len(chords_per_song)-len(folded_per_song),len(chords_per_song),(len(chords_per_song)-len(folded_per_song))/len(chords_per_song)*100, len(folded_per_song)))
print('duplicate songs by instances: %d'%(len(folded_instances_per_song)-len(set(tuple(song) for song in folded_instances_per_song))))

if limit_notes:
    folded_per_song = [chords for chords in folded_per_song if all(len(base_chords_to_comps[chord])<=limit_notes for chord in chords)]
    folded_instances_per_song = [instances for instances in folded_instances_per_song if all(len(base_chords_to_comps[chord]) <= limit_notes for chord in set(instances))]
    print('limit_notes=%d: %d'%(limit_notes, len(folded_per_song)))

count_chords = Counter(chord for chords in folded_per_song for chord in chords)
print(count_chords)
all_colors = plt.get_cmap('tab20').colors
sorted_chords = sorted([(chord,cnt/len(folded_per_song)) for chord,cnt in count_chords.items()], key=lambda x:(-x[1],x[0]))
color_dict = {chord[0]: color for chord,color in zip(sorted_chords,all_colors)}
sorted_chords = sorted_chords[:13]
os.makedirs('assets', exist_ok=True)
plot(os.path.join('assets','Chord prevalence by songs'), sorted_chords, [color_dict[chord[0]] for chord in sorted_chords])

instances = [chord for chords in folded_instances_per_song for chord in chords]
count_folded_instances = Counter(instances)
print(count_instances)
print(len(instances))
sorted_instances = sorted([(chord,cnt/len(instances)) for chord,cnt in count_instances.items()], key=lambda x:(-x[1],x[0]))[:13]
plot(os.path.join('assets','Chord prevalence by chord instance'), sorted_instances, [color_dict[chord[0]] for chord in sorted_instances], total=True)

max_needed = Counter(len(a) for a in folded_per_song)
print(max_needed)
plot(os.path.join('assets','Number of distinct chords by songs'), sorted([(num_chords,cnt/len(folded_per_song)) for num_chords,cnt in max_needed.items()], key=lambda x:(-x[1],x[0]))[:14], 'violet', 13)

chord_sets = sorted([(' '.join(chords),cnt/len(folded_per_song)) for chords,cnt in Counter(tuple(sorted(chords, key=lambda x:(x[0] in ('A','B'), x[0], x[-1]!='b', x[-1]=='#', x[-1]=='m', x))) for chords in folded_per_song).items() if cnt>80], key=lambda x:(-x[1],x[1]))
print(chord_sets)
plot(os.path.join('assets','Chord set prevalence by songs'), chord_sets[:14], 'tan', 13)

print(sorted([(chords,cnt) for chords,cnt in Counter(tuple(sorted(chords)) for chords in folded_per_song if 3<=len(chords)<=6).items() if cnt>10], key=lambda x:(-x[1],x[1])))

have_chords = ['A', 'Am', 'A7', 'Am7','A7sus4','AmM7','AM7','Asus4','A9','Bbdim','C', 'C7', 'C7sus4','CM7','C6','Csus4','Caug','C9','C#mM7','C#dim','Dsus2','Dsus4','Eaug','Em7','EmM7','F','Fadd9','G6','Gdim','Gsus2','G#aug'] # 'Cadd9Fsus2','F6sus2'
assert all(chord in base_chords_to_comps or chord in fold_chords for chord in have_chords)
have_chords_set = set(have_chords)
count_have = sum(chords<=have_chords_set for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))

have_chords = ['C', 'Cm', 'Csus4', 'C5', 'D', 'Dm', 'Dsus4', 'D5', 'Eb', 'Em', 'F', 'F#m', 'G', 'Gm', 'Gsus4', 'G5', 'A', 'Am', 'Asus2', 'A5']
#have_chords = ['C', 'Cm', 'C5', 'D', 'Dm', 'Dsus2', 'Dsus4', 'Em', 'F', 'F#m', 'G', 'Gm', 'Gsus4', 'G5', 'A', 'Am', 'Asus2', 'D5', 'Asus4']
#have_chords = ['Am', 'C', 'D', 'Em', 'F', 'G']
assert all(chord in base_chords_to_comps or chord in fold_chords for chord in have_chords)
have_chords_set = set(have_chords)
count_have = sum(chords<=have_chords_set for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))

have_chords = ['C', 'Cm', 'Csus4', 'C5', 'D', 'Dm', 'Dsus4', 'D5', 'Eb', 'Em', 'F', 'F#m', 'G', 'Gm', 'Gsus4', 'G5', 'A', 'Am', 'Asus2', 'A5', 'Bm', 'B', 'E', 'Bb']
#have_chords = ['C', 'Cm', 'C5', 'D', 'Dm', 'Dsus2', 'Dsus4', 'Em', 'F', 'F#m', 'G', 'Gm', 'Gsus4', 'G5', 'A', 'Am', 'Asus2', 'D5', 'Asus4']
#have_chords = ['Am', 'C', 'D', 'Em', 'F', 'G']
assert all(chord in base_chords_to_comps or chord in fold_chords for chord in have_chords)
have_chords_set = set(have_chords)
count_have = sum(chords<=have_chords_set for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))

have_per_song = [chords for chords in folded_per_song if all(chord in have_chords for chord in chords)]
count_have = Counter(chord for chords in have_per_song for chord in chords)
print(count_have)

have_instances_per_song = [instances for instances in folded_instances_per_song if all(chord in have_chords for chord in set(instances))]
count_have_instances = Counter(chord for instances in have_instances_per_song for chord in instances)
print(count_have_instances)


have_chords = ['C', 'Am', 'D', 'F', 'F#m', 'G', 'Gm']
assert all(chord in base_chords_to_comps or chord in fold_chords for chord in have_chords)
have_chords_set = set(have_chords)
count_have = sum(chords<=have_chords_set for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))

have_chords = ['Em', 'G', 'A', 'Am', 'D', 'Dm', 'F', 'F#m']
assert all(chord in base_chords_to_comps or chord in fold_chords for chord in have_chords)
have_chords_set = set(have_chords)
count_have = sum(chords<=have_chords_set for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))


def powerset(iterable, max_len=None):
    s = list(iterable)
    if max_len is None:
        max_len = len(s)
    return chain.from_iterable(combinations(s, r) for r in range(1,max_len+1))

top_chords = [chord[0] for chord in sorted(count_chords.items(), key=lambda x: -x[1])][:top]
print(top_chords)

chord_to_next = {}
for song in folded_instances_per_song:
    for chord,next_chord in zip(song[:-1],song[1:]):
        if next_chord==chord:
            continue
        if chord not in chord_to_next:
            chord_to_next[chord] = Counter()
        chord_to_next[chord][next_chord] += 1
progressions1 = sorted([(chord, sorted(next_chords.items(), key=lambda x:-x[1])[0]) for chord, next_chords in chord_to_next.items()], key=lambda x: (-x[1][1], x[0], x[1][0]))[:30]
print(progressions1)
progressions = sorted([(chord + '  →  ' + next_chord[0], next_chord[1]/(len(instances)-len(folded_per_song))) for chord, next_chords in chord_to_next.items() for next_chord in next_chords.items()], key=lambda x: (-x[1], x[0]))[:60]
print(progressions)
plot(os.path.join('assets','Next chord prevalence by instance'), progressions[:18], [color_dict[chord[0].split(' ')[0]] for chord in progressions[:18]], total=True, font_size=11)

results = []
for i in range(1,min(max_len,len(top_chords))+1):
    subs = powerset(top_chords,i)
    best_sub = []
    best_count = 0
    for sub in subs:
        sub = sorted(sub, key=lambda x:(x[0] in ('A','B'), x[0], x[-1]!='b', x[-1]=='#', x[-1]=='m', x))
        sub_set = set(sub)
        sub = ' '.join(sub)
        count_have = sum(chords <= sub_set for chords in folded_per_song)
        if count_have>best_count:
            best_count = count_have
            best_sub = [sub]
        elif count_have==best_count:
            best_sub.append(sub)
    if best_count>0:
        print('%d %d %.1f%%'%(i, best_count, best_count / len(folded_per_song) * 100), sorted(best_sub))
        results.append(('%d:  %s'%(i, sorted(best_sub)[0]), best_count / len(folded_per_song)))

    if 5<i<14:
        plot(os.path.join('assets','k-length chord sets for maximum songs'), results[2:13][::-1], 'pink')
print('done')