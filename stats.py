import pymysql.cursors
from pychord import Chord
from collections import Counter

db = pymysql.connect(host="localhost", user="root", passwd="", db="UltimateGuitarTabs")
cur = db.cursor()

cur.execute("select chords from chords")
instances_per_song = [row[0].split(',') for row in cur.fetchall()]
chords_per_song = [set(instances) for instances in instances_per_song]
count_instances = Counter(chord for instances in instances_per_song for chord in instances)

base_chords = set()
bad_chords = set()
fold_chords = {}
seen_comps_to_chords = {}
for chord, cnt in sorted(count_instances.items(), key=lambda x:(-x[1],x[0])):
    if chord in base_chords or chord in bad_chords or chord in fold_chords:
        continue
    try:
        comps = tuple(sorted(set(Chord(chord).components())))
    except:
        bad_chords.add(chord)
        continue
    if comps in seen_comps_to_chords:
        fold_chords[chord] = seen_comps_to_chords[comps]
    else:
        base_chords.add(chord)
        seen_comps_to_chords[comps] = chord

folded_per_song = [set(fold_chords[chord] if chord in fold_chords else chord for chord in chords) for chords in chords_per_song if all(chord not in bad_chords for chord in chords)]
print('base chords=%d, folded chords=%d, bad chords=%d, bad songs=%d/%d (%.1f%%)'%(len(base_chords),len(fold_chords),len(bad_chords),len(chords_per_song)-len(folded_per_song),len(chords_per_song),(len(chords_per_song)-len(folded_per_song))/len(chords_per_song)*100))

max_needed = Counter(len(a) for a in folded_per_song)
print(max_needed)

count_chords = Counter(chord for chords in folded_per_song for chord in chords)
print(count_chords)

print(sorted([(chords,cnt) for chords,cnt in Counter(tuple(sorted(chords)) for chords in folded_per_song if 3<=len(chords)<=6).items() if cnt>10], key=lambda x:(-x[1],x[1])))

have_chords = set(['C', 'D', 'Em', 'G', 'Am', 'F', 'A', 'Bm', 'Dm', 'E', 'F#m'])
count_have = sum(chords<=have_chords for chords in folded_per_song)
print(have_chords, '%d/%d %.1f%%'%(count_have,len(folded_per_song),count_have/len(folded_per_song)*100))
