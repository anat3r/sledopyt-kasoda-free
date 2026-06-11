#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC=_os.path.join(ROOT,"src")
# Single source of truth: module id is read from module.json so that grant UUIDs
# (Compendium.<MODULE>.features...) always match what validate.mjs expects on this branch.
MODULE=json.load(open(_os.path.join(ROOT,"module.json"),encoding="utf-8"))["id"]
SOURCE={"custom":"Альтернативный Следопыт (Kasoda) v1.1","rules":"2024","revision":1}
import hashlib
_B62="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def mid(key):
    h=int(hashlib.md5(key.encode("utf-8")).hexdigest(),16)
    out=""
    while len(out)<16:
        out+=_B62[h%62]; h//=62
    return out[:16]
def feat_uuid(fid): return f"Compendium.{MODULE}.features.Item.{fid}"
FIGHTING_STYLES=["8YwPFv3UAPjWVDNf","zSlV0O2rQMdoq6pB","hCop9uJrWhF1QPb4","mHcSjcHJ8oZu3hkb","3QhKQxdimzqS2pVq","IYzoDJqUku3FyBn2","RanCqqgLtHzIs5WB"]
MODES={"CUSTOM":0,"MULTIPLY":1,"ADD":2,"DOWNGRADE":3,"UPGRADE":4,"OVERRIDE":5}
def C(key,mode,value,priority=20): return {"key":key,"mode":MODES[mode],"value":str(value),"priority":priority}
def ae(name,img,changes,transfer=True,disabled=False,descr=""):
    return {"_id":mid("AE"+name),"name":name,"img":img,"type":"base","changes":changes,
            "disabled":disabled,"transfer":transfer,
            "duration":{"startTime":None,"seconds":None,"rounds":None,"turns":None},
            "description":descr,"origin":None,"tint":"#ffffff","statuses":[],"flags":{}}
FEATURES=[]
def feat(key,name,level,ident,img,html,effects=None,spells=None,uses=None,activation=None,template=None):
    FEATURES.append(dict(key=key,name=name,level=level,ident=ident,img=img,html=html,
        effects=effects or [],spells=spells or [],uses=uses,activation=activation,template=template))

def build_uses(u):
    return {"spent":0,"max":u["max"],"recovery":[{"period":u["period"],"type":"recoverAll","formula":""}]}

def build_activity(act_id,activation,consume_uses,template):
    tt=template or {}
    tmpl={"count":"","contiguous":False,"type":tt.get("type",""),"size":tt.get("size",""),
          "width":"","height":"","units":(tt.get("units","ft") if tt.get("type") else "")}
    atype,aval=activation if activation else ("action",1)
    return {act_id:{"_id":act_id,"type":"utility",
        "activation":{"type":atype,"value":aval,"condition":"","override":False},
        "consumption":{"targets":([{"type":"itemUses","target":"","value":"1","scaling":{"mode":"","formula":""}}] if consume_uses else []),
            "scaling":{"allowed":False,"max":""},"spellSlot":False},
        "description":{"chatFlavor":""},
        "duration":{"concentration":False,"value":"","units":"","special":"","override":False},
        "effects":[],"range":{"units":"","special":"","override":False},
        "target":{"template":tmpl,"affects":{"count":"","type":"","choice":False,"special":""},"prompt":True,"override":False},
        "uses":{"spent":0,"max":"","recovery":[]},
        "roll":{"formula":"","name":"","prompt":False,"visible":False},"sort":0}}
def spell_grant_adv(spell_ids,title="Заклинания"):
    items=[{"optional":False,"uuid":f"Compendium.laaru-dnd5-hw.spells.Item.{sid}"} for sid in spell_ids]
    return {"_id":mid("advSPL"+title+"".join(spell_ids)),"type":"ItemGrant","level":1,"title":title,"icon":None,"value":{},
            "configuration":{"items":items,"optional":False,
                "spell":{"preparation":"always","ability":["wis"],"uses":{"max":"","per":"","requireSlot":False}}}}
def P(*xs): return "".join(f"<p>{x}</p>" for x in xs)

feat("spellcasting","Заклинания",1,"zaklinaniya","icons/magic/nature/root-vine-entangle-foot-green.webp",
P("Вы научились использовать магическую сущность природы для сотворения заклинаний.",
"<strong>Ячейки заклинаний.</strong> В таблице класса указано, сколько у вас ячеек для заклинаний 1-го уровня и выше. Вы восстанавливаете их, завершая Долгий отдых.",
"<strong>Подготовленные заклинания.</strong> Для начала выберите два заклинания Следопыта 1-го уровня (рекомендуются <em>Лечение ран</em> и <em>Опутывающий удар</em>). Число подготовленных растёт по таблице класса.",
"<strong>Замена.</strong> Завершая Долгий отдых, можно заменить число заклинаний, равное модификатору Мудрости (минимум 1).",
"<strong>Заклинательная характеристика.</strong> Мудрость. Можно использовать Друидическую фокусировку."))

adapt_fx=[
 ae("Адаптация: Арктика","icons/magic/water/snowflake-ice-snow-white.webp",[C("system.traits.dr.value","ADD","cold")],False,True,"Сопротивление Холодом."),
 ae("Адаптация: Болота","icons/magic/nature/root-vine-caduceus-healing.webp",[C("system.traits.dr.value","ADD","poison")],False,True,"Сопротивление Ядом."),
 ae("Адаптация: Пустыня","icons/magic/fire/flame-burning-embers-orange.webp",[C("system.traits.dr.value","ADD","fire")],False,True,"Сопротивление Огнём."),
 ae("Адаптация: Подземье","icons/magic/perception/eye-ringed-glow-angry-large-red.webp",[C("system.attributes.senses.darkvision","UPGRADE","60")],False,True,"Тёмное зрение 60 фт."),
 ae("Адаптация: Горы","icons/magic/movement/trail-streak-zigzag-yellow.webp",[C("system.attributes.movement.climb","ADD","15")],False,True,"Скорость лазания."),
 ae("Адаптация: Побережье","icons/magic/water/wave-water-blue.webp",[C("system.attributes.movement.swim","ADD","15")],False,True,"Скорость плавания."),
]
feat("adaptation","Сверхъестественная адаптация",1,"sverhadaptaciya","icons/magic/nature/leaf-glow-triple-green.webp",
P("Всякий раз, оканчивая Долгий отдых, вы можете адаптироваться к местности, в которой находитесь. На 11-м уровне можно выбрать вторую местность. Эффекты длятся до конца следующего Долгого отдыха.")
+"<p><strong>После Долгого отдыха включите соответствующий переключаемый эффект биома</strong> в этой особенности. Биомы:</p><ul>"
+"<li><strong>Арктика.</strong> Сопротивление Холоду; нет вреда от температур не ниже −52 °C; преимущество при перемещении по льду.</li>"
+"<li><strong>Болота.</strong> Сопротивление Ядом; преимущество против Отравленного и немагических болезней.</li>"
+"<li><strong>Горы.</strong> Акклиматизация к высоте; игнор сильного ветра на Внимательность; скорость лазания = скорости передвижения (или +15 фт).</li>"
+"<li><strong>Леса.</strong> Игнор осадков и густой растительности на Внимательность; преимущество на Скрытность; обнаружение растений с «Обманчивой внешностью».</li>"
+"<li><strong>Подземье.</strong> Тёмное зрение 60 фт (или +30 фт); нет помехи на Восприятие из-за тусклого света; преимущество на Скрытность во Тьме.</li>"
+"<li><strong>Пустыня.</strong> Сопротивление Огнём; нет вреда от температур не выше 52 °C; чувство существ под песком в 30 фт.</li>"
+"<li><strong>Побережье/моря.</strong> Бой под водой без неудобств; задержка дыхания 10 мин; скорость плавания = скорости передвижения (или +15 фт).</li></ul>"
+"<p><strong>В адаптированной местности:</strong></p><ul>"
+"<li>Удвоенный Бонус мастерства для проверок Инт и Мдр, связанных с местностью.</li>"
+"<li>Труднопроходимая местность не замедляет группу; группа не может заблудиться (кроме как из-за магии).</li>"
+"<li>Преимущество на поиск пищи (вдвое больше).</li>"
+"<li>При выслеживании: +5 к Выживанию; при успехе — точное количество, размеры и давность прохода существ.</li></ul>", adapt_fx)

feat("endlesshunt","Бесконечная охота",1,"beskonechnaya-ohota","icons/skills/targeting/crosshair-bars-yellow.webp",
P("Когда вы совершаете бросок Инициативы, вы можете объявить видимое существо своей <strong>Добычей</strong> до конца боя. Если её хиты падают до 0, в начале следующего хода можно выбрать новую Добычу.",
"Пока существо — Добыча, оно не получает преимуществ от состояния Невидимый в пределах <strong>[[/r @scale.sledopyt.quarry-sense]] фт</strong> (15/30/60/90 фт на 1/5/11/17 уровнях).",
"Вы понимаете общий смысл слов Добычи.",
"Попадая по Добыче атакой оружием, вы дополнительно наносите <strong>[[/r @scale.sledopyt.hunt-die]]</strong> урона («Кость охоты» d4→d6→d8→d10).",
"Если бой кончился, а Добыча жива — можно запомнить её как цель Охоты: преимущество на Выживание для выслеживания и Интеллект для сведений; в 1 миле ощущаете слабое присутствие.",
"Можно помнить целей Охоты: <strong>[[/r @scale.sledopyt.quarry-targets]]</strong> (2; +1 на 5/11/17 уровнях). Сверх лимита — забываете одну."))

feat("weaponmastery","Оружейное мастерство",1,"oruzhejnoe-masterstvo","icons/weapons/swords/swords-short.webp",
P("Вы можете использовать свойства мастерства двух видов оружия, которыми владеете, по вашему выбору.",
"Завершая Долгий отдых, можно изменить выбранные виды оружия."))

feat("explorer","Искусный исследователь",2,"iskusnyj-issledovatel","icons/tools/navigation/map-marked-green.webp",
P("<strong>Компетенция.</strong> Выберите навык, которым владеете. Бонус мастерства удваивается для проверок этим навыком.",
"<strong>Языки.</strong> Изучаете два языка.",
"На <strong>9-м уровне</strong> — ещё один навык для Компетенции и ещё один язык."))

feat("primalawareness","Первозданная осведомлённость",3,"pervozdannaya-osvedomlennost","icons/magic/perception/eye-tendrils-web-purple.webp",
P("Действием вы сосредотачиваетесь на познании пространства. 10 минут вы ощущаете существ одного вида в 1 миле (6 миль — в адаптированной местности): Аберрации, Драконы, Исчадия, Небожители, Нежить, Феи или Элементали.",
"В 500 фт (1000 фт в адаптированной местности) узнаёте направление к ним. Цель Охоты рядом — узнаёте о ней независимо от вида.",
"Добавляете модификатор Мудрости к Интеллекту (Расследование).",
"<em>Использований: 1 + мод. Мудрости; восстановление после Долгого отдыха.</em>"),
uses={"max":"1 + @abilities.wis.mod","period":"lr"},activation=("action",1))

feat("extraattack","Дополнительная атака",5,"dopolnitelnaya-ataka","icons/skills/melee/weapons-crossed-swords-pink.webp",
P("Когда в свой ход вы совершаете действие Атака, вы можете совершить две атаки вместо одной."))

allterrain_fx=[ae("Вездеход","icons/magic/movement/trail-streak-impact-blue.webp",
 [C("system.attributes.movement.walk","ADD","10"),C("system.attributes.movement.climb","ADD","15"),C("system.attributes.movement.swim","ADD","15")],
 True,False,"Пока без Тяжёлого доспеха: +10 фт скорости; лазание/плавание = ходьбе.")]
feat("allterrain","Вездеход",6,"vezdehod","icons/magic/movement/trail-streak-zigzag-teal.webp",
P("Пока вы не носите Тяжёлых доспехов, ваша скорость увеличивается на 10 футов, и вы получаете скорость лазания и плавания, равную скорости ходьбы.",
"<em>Переключаемый эффект уже добавляет +10 фт. Отключите его, если надели Тяжёлый доспех.</em>"),allterrain_fx)

feat("survivalmaster","Мастер выживания",9,"master-vyzhivaniya","icons/skills/wounds/injury-pain-body-orange.webp",
P("Вы совершаете с Преимуществом проверки Инициативы и спасброски Ловкости против видимых эффектов (заклинания, ловушки). Нельзя быть Ослеплённым, Оглушённым или Недееспособным."))

feat("naturetongue","Язык природы",9,"yazyk-prirody","icons/magic/nature/leaf-juggle-humanoid-green.webp",
P("Вы можете неограниченно накладывать <em>Разговор с животными</em> и <em>Разговор с растениями</em>. Эти заклинания выдаются как всегда подготовленные (Мудрость) при получении этой особенности."),spells=["OjL2GAHKM47DrEtD","0c8C5FLHXNg8830T"])

feat("relentless","Неустанный охотник",10,"neustannyj-ohotnik","icons/magic/control/buff-strength-muscle-damage-red.webp",
P("Вы можете завершить Долгий отдых после 4 часов сна, оставаясь в сознании.",
"Концентрация не прерывает Короткий и Долгий отдых. В конце Короткого отдыха истощение −1, если вы не концентрировались на заклинании."))

feat("vanish","Мастер исчезновения",13,"master-ischeznoveniya","icons/magic/perception/silhouette-stealth-shadow.webp",
P("Вы можете совершать действие Засада Бонусным действием.",
"Оказавшись на линии обзора существа, вы можете Реакцией стать Невидимым до конца своего следующего хода.",
"<em>Использований: Бонус мастерства; восстановление после Долгого отдыха.</em>"),
uses={"max":"@prof","period":"lr"},activation=("reaction",1))

feat("hunterfocus","Охотничья концентрация",14,"ohotnichya-koncentraciya","icons/magic/control/buff-flight-wings-blue.webp",
P("Пока вы концентрируетесь на заклинании Следопыта, в начале своего хода можно получить одно преимущество:",
"<strong>Выносливость охотника.</strong> 1d10 + мод. Мудрости временных хитов (мин. 1) ИЛИ окончить на себе Отравленный, Ослеплённый или Оглохший.",
"<strong>Меткость охотника.</strong> Перед атакой по Добыче добавьте мод. Мудрости к броску атаки или урона."))

wild_fx=[ae("Дикие чувства","icons/magic/perception/eye-ringed-glow-angry-large-teal.webp",[C("system.attributes.senses.blindsight","UPGRADE","60")],True,False,"Слепое зрение 60 фт.")]
feat("wildsenses","Дикие чувства",17,"dikie-chuvstva","icons/magic/perception/eye-slit-orange.webp",
P("Вы получаете Слепое зрение радиусом 60 футов.",
"Бонусным действием можно заменить его на Истинное зрение 30 фт на 10 минут.",
"<em>Использований: 1; восстановление после Короткого/Долгого отдыха (либо за ячейку 1-го уровня и выше — вручную).</em>"),effects=wild_fx,uses={"max":"1","period":"sr"},activation=("bonus",1))

apex_fx=[ae("Вершина пищевой цепи — против Добычи","icons/skills/targeting/target-strike-triple-blue.webp",[C("flags.dnd5e.weaponCriticalThreshold","DOWNGRADE","18")],False,True,"Крит 18–20. Включать только при атаках по Добыче.")]
feat("apex","Вершина пищевой цепи",18,"vershina-pishchevoj-cepi","icons/creatures/abilities/mouth-teeth-rows-red.webp",
P("Совершая действие Атака против своей Добычи, вы можете совершить три атаки вместо двух.",
"Ваши атаки против Добычи критуют при «18–20».",
"<em>Переключаемый эффект задаёт крит 18–20 — включайте только при атаках по Добыче.</em>"),apex_fx)

feat("epicboon","Эпический дар",19,"epicheskij-dar","icons/magic/light/explosion-star-glow-blue-purple.webp",
P("Вы получаете Эпический дар на ваш выбор, требованиям которого соответствуете.",
"<em>Перетащите выбранный Эпический дар из компендиума черт на лист.</em>"))

feat("huntingrounds","Охотничьи угодья",20,"ohotnichi-ugodya","icons/magic/nature/tree-spirit-green.webp",
P("Выбирая Добычу, вы можете призвать призрачную дымку, воссоздающую дикую местность. Для вас и Добычи она заменяет реальность; другие видят сквозь неё.",
"30-футовая Эманация от вас, перемещается с вами. 1 минута или пока вы не Недееспособны / не окончите эффект.",
"Для Добычи это Труднопроходимая местность. Покидая её, Добыча совершает спасбросок Харизмы против СЛ ваших заклинаний; при успехе перемещение в этот ход не ограничено.",
"Пока Добыча внутри: ваши атаки по ней — с Преимуществом; её спасброски против ваших заклинаний/умений — с Помехой.",
"<em>Использований: 1; восстановление после Долгого отдыха (либо за ячейку 4-го уровня и выше — вручную). При использовании ставит шаблон 30 фт (Эманация) на курсор.</em>"),
uses={"max":"1","period":"lr"},activation=("special",None),template={"type":"radius","size":"30"})

# ---------- write feature items ----------
os.makedirs(f"{SRC}/features",exist_ok=True); os.makedirs(f"{SRC}/class",exist_ok=True)
fid_map={}
for f in FEATURES:
    fid=mid(f["key"]+"FEAT"); fid_map[f["key"]]=fid
    for _e in f["effects"]:
        _e["_key"]="!items.effects!"+fid+"."+_e["_id"]
    item={"_id":fid,"name":f["name"],"type":"feat","img":f["img"],
        "system":{"description":{"value":f["html"],"chat":""},"source":SOURCE,
            "identifier":f["ident"],"type":{"value":"class","subtype":""},
            "requirements":f"Следопыт {f['level']}","properties":[],
            "advancement":([spell_grant_adv(f["spells"])] if f["spells"] else [])},
        "effects":f["effects"],"folder":None,"sort":f["level"]*1000,
        "flags":{MODULE:{"level":f["level"]}},"_stats":{"systemId":"dnd5e"},"_key":"!items!"+fid}
    if f.get("uses"):
        item["system"]["uses"]=build_uses(f["uses"])
    if f.get("uses") or f.get("template"):
        aid=mid("ACT"+f["key"])
        item["system"]["activities"]=build_activity(aid,f.get("activation"),bool(f.get("uses")),f.get("template"))
    fn=re.sub(r'[^0-9A-Za-zА-Яа-я]+','_',f["name"]).strip('_')
    json.dump(item,open(f"{SRC}/features/{fn}_{fid}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("features:",len(FEATURES))

# ---------- advancement builders ----------
def A_hp(): return {"_id":mid("advHP"),"type":"HitPoints","configuration":{},"value":{},"title":"","hint":""}
def A_trait(grants,choices=None,restriction=None,title=""):
    a={"_id":mid("advT"+title+("".join(grants)+("".join(p["pool"][0] for p in (choices or []) if p.get("pool")) ))[:8]),
       "type":"Trait","level":1,"title":title,"value":{"chosen":[]},
       "configuration":{"mode":"default","allowReplacements":False,"grants":grants,"choices":choices or []}}
    if restriction: a["classRestriction"]=restriction
    return a
def A_scale(ident,stype,scale,title):
    return {"_id":mid("advS"+ident),"type":"ScaleValue","value":{},"title":title,"classRestriction":"primary",
            "configuration":{"identifier":ident,"type":stype,"distance":{"units":"ft" if stype=="distance" else ""},"scale":scale}}
def A_asi(level):
    return {"_id":mid("advASI"+str(level)),"type":"AbilityScoreImprovement","level":level,"title":"",
            "configuration":{"points":2,"fixed":{},"cap":{},"locked":[]},"value":{"type":"asi"}}
def A_subclass():
    return {"_id":mid("advSUB"),"type":"Subclass","level":3,"title":"Подкласс","hint":"",
            "configuration":{},"value":{"document":None,"uuid":None}}
def A_grant(level,keys,title):
    items=[{"uuid":feat_uuid(fid_map[k]),"optional":False} for k in keys]
    return {"_id":mid("advG"+str(level)+title)[:16],"type":"ItemGrant","level":level,"title":title,"icon":None,"value":{},
            "configuration":{"items":items,"optional":False,"spell":{"ability":[""],"uses":{"max":"","per":"","requireSlot":False},"prepared":0}}}
def A_style():
    pool=[{"uuid":f"Compendium.laaru-dnd5-hw.classfeatures.Item.{u}"} for u in FIGHTING_STYLES]
    return {"_id":mid("advSTYLE"),"type":"ItemChoice","title":"Боевой стиль","icon":None,
            "hint":"Выберите один боевой стиль (или «Воин друид»).",
            "value":{"added":{},"replaced":{}},
            "configuration":{"choices":{"2":{"count":1,"replacement":False}},"allowDrops":True,"type":"feat",
                "pool":pool,"spell":{"ability":[""],"uses":{"max":"","per":"","requireSlot":False},"prepared":0},
                "restriction":{"type":"","subtype":"","level":"","list":[]}}}

adv=[]
adv.append(A_hp())
# proficiencies
adv.append(A_trait(["saves:con","saves:wis"],restriction="primary"))
adv.append(A_trait(["armor:lgt","armor:med","armor:shl"]))
adv.append(A_trait(["weapon:sim","weapon:mar"]))
adv.append(A_trait([],choices=[{"count":3,"pool":["skills:ath","skills:prc","skills:sur","skills:ani","skills:nat","skills:ins","skills:inv","skills:ste"]}],restriction="primary",title="Навыки следопыта"))
# scale values
adv.append(A_scale("hunt-die","dice",{"1":{"number":1,"faces":4,"modifiers":[]},"5":{"number":1,"faces":6,"modifiers":[]},"11":{"number":1,"faces":8,"modifiers":[]},"17":{"number":1,"faces":10,"modifiers":[]}},"Кость охоты"))
adv.append(A_scale("quarry-targets","number",{"1":{"value":2},"5":{"value":3},"11":{"value":4},"17":{"value":5}},"Цели Охоты"))
adv.append(A_scale("quarry-sense","distance",{"1":{"value":15},"5":{"value":30},"11":{"value":60},"17":{"value":90}},"Чутьё Добычи"))
# ASIs
for L in (4,8,12,16): adv.append(A_asi(L))
# subclass + fighting style
adv.append(A_subclass()); adv.append(A_style())
# item grants by level
adv.append(A_grant(1,["spellcasting","adaptation","endlesshunt","weaponmastery"],"Особенности 1 уровня"))
adv.append(A_grant(2,["explorer"],"Особенность"))
adv.append(A_grant(3,["primalawareness"],"Особенность"))
adv.append(A_grant(5,["extraattack"],"Особенность"))
adv.append(A_grant(6,["allterrain"],"Особенность"))
adv.append(A_grant(9,["survivalmaster","naturetongue"],"Особенности"))
adv.append(A_grant(10,["relentless"],"Особенность"))
adv.append(A_grant(13,["vanish"],"Особенность"))
adv.append(A_grant(14,["hunterfocus"],"Особенность"))
adv.append(A_grant(17,["wildsenses"],"Особенность"))
adv.append(A_grant(18,["apex"],"Особенность"))
adv.append(A_grant(19,["epicboon"],"Особенность"))
adv.append(A_grant(20,["huntingrounds"],"Особенность"))

CLASS_DESC=("<p>Вдали от суеты городов, в дебрях лесов и на просторах равнин следопыты несут свой вечный дозор. "
"Благодаря связи с природой они творят заклинания, оттачивая таланты и магию со смертельным упорством.</p>"
"<p><em>Альтернативный Следопыт от Kasoda, версия 1.1.</em></p>")

cls={"_id":mid("CLASSsledopyt"),"name":"Альтернативный Следопыт","type":"class",
 "img":"icons/creatures/mammals/elk-moose-marked-green.webp",
 "system":{"description":{"value":CLASS_DESC,"chat":""},"source":SOURCE,"identifier":"sledopyt",
   "levels":1,"hitDice":"d10","hitDiceUsed":0,"advancement":adv,
   "spellcasting":{"progression":"half","ability":"wis","preparation":{"formula":""}},
   "wealth":"7","primaryAbility":{"value":["dex","wis"],"all":False}},
 "effects":[],"folder":None,"sort":0,"flags":{},"_stats":{"systemId":"dnd5e"},"_key":"!items!"+mid("CLASSsledopyt")}
json.dump(cls,open(f"{SRC}/class/Альтернативный_Следопыт_{cls['_id']}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("class advancements:",len(adv))
print("OK")
