from pathlib import Path
import json
P=Path('docs/content.js');C=json.loads(P.read_text()[14:-1])
def ids(nums):return ['s'+str(i).zfill(2) for i in dict.fromkeys(nums)]
core={
'analist':list(range(1,13))+list(range(17,31))+[33,43,44,53,54,56],
'bilim':list(range(1,15))+list(range(17,37))+[41,42,43,44,45,47,53,54,55,56,61,62,64,65,67,69,70,85,88]+list(range(89,97))+list(range(105,109)),
'ml':list(range(1,15))+list(range(17,25))+[29,30,31,32,41,43,45,46,47,53,54,55,56,61,62,64,69]+list(range(89,109)),
'operasyon':list(range(1,15))+list(range(17,29))+[33,34,37,38,40,49,50,51,52,56,65,66,67,68,82]
}
for r in C['roles']:
 r['coreLessons']=ids(core[r['id']])
 chosen={next(l['module'] for l in C['lessons'] if l['id']==i) for i in r['coreLessons']}
 r['modules']+=sorted(chosen-set(r['modules']))
 r['priority']=[m for m in r['modules'] if m in chosen]
 r['selectionNote']='Çekirdek ders düzeyinde seçilmiştir; bir modülde bir dersin gerekli olması diğer üç dersin de zorunlu olduğu anlamına gelmez.'
P.write_text('window.COURSE='+json.dumps(C,ensure_ascii=False)+';',encoding='utf-8')
