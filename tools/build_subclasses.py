#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Subclass generator (appends to src/features and src/subclasses). Batch-based."""
import json, os, re, hashlib
import os as _os
SRC=_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),"src"); MODULE="sledopyt-kasoda"
SOURCE={"custom":"Альтернативный Следопыт (Kasoda) v1.1","rules":"2024","revision":1}
_B62="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def mid(key):
    h=int(hashlib.md5(key.encode("utf-8")).hexdigest(),16); o=""
    while len(o)<16: o+=_B62[h%62]; h//=62
    return o[:16]
def fuid(fid): return f"Compendium.{MODULE}.features.Item.{fid}"
def spuid(sid): return f"Compendium.laaru-dnd5-hw.spells.Item.{sid}"
MODES={"CUSTOM":0,"MULTIPLY":1,"ADD":2,"DOWNGRADE":3,"UPGRADE":4,"OVERRIDE":5}
def C(k,m,v,p=20): return {"key":k,"mode":MODES[m],"value":str(v),"priority":p}
def ae(name,img,changes,transfer=True,disabled=False,descr=""):
    return {"_id":mid("AE"+name),"name":name,"img":img,"type":"base","changes":changes,
        "disabled":disabled,"transfer":transfer,
        "duration":{"startTime":None,"seconds":None,"rounds":None,"turns":None},
        "description":descr,"origin":None,"tint":"#ffffff","statuses":[],"flags":{}}
def P(*xs): return "".join(f"<p>{x}</p>" for x in xs)
def build_uses(u): return {"spent":0,"max":u["max"],"recovery":[{"period":u["period"],"type":"recoverAll","formula":""}]}
def build_activity(aid,activation,consume,template):
    tt=template or {}
    tmpl={"count":"","contiguous":False,"type":tt.get("type",""),"size":tt.get("size",""),
          "width":"","height":"","units":(tt.get("units","ft") if tt.get("type") else "")}
    at,av=activation if activation else ("action",1)
    return {aid:{"_id":aid,"type":"utility",
        "activation":{"type":at,"value":av,"condition":"","override":False},
        "consumption":{"targets":([{"type":"itemUses","target":"","value":"1","scaling":{"mode":"","formula":""}}] if consume else []),
            "scaling":{"allowed":False,"max":""},"spellSlot":False},
        "description":{"chatFlavor":""},
        "duration":{"concentration":False,"value":"","units":"","special":"","override":False},
        "effects":[],"range":{"units":"","special":"","override":False},
        "target":{"template":tmpl,"affects":{"count":"","type":"","choice":False,"special":""},"prompt":True,"override":False},
        "uses":{"spent":0,"max":"","recovery":[]},
        "roll":{"formula":"","name":"","prompt":False,"visible":False},"sort":0}}

def write_feat(key,name,level,img,html,effects=None,uses=None,activation=None,template=None,spells=None,sort=None):
    fid=mid(key+"FEAT"); effects=effects or []
    for e in effects: e["_key"]="!items.effects!"+fid+"."+e["_id"]
    adv=[]
    if spells:
        items=[{"optional":False,"uuid":spuid(s)} for s in spells]
        adv=[{"_id":mid("advSPL"+key+"".join(spells)),"type":"ItemGrant","level":1,"title":"Заклинания","icon":None,"value":{},
              "configuration":{"items":items,"optional":False,
                "spell":{"preparation":"always","ability":["wis"],"uses":{"max":"","per":"","requireSlot":False}}}}]
    item={"_id":fid,"name":name,"type":"feat","img":img,
        "system":{"description":{"value":html,"chat":""},"source":SOURCE,
            "identifier":re.sub(r'[^a-z0-9]+','-',key.lower()),
            "type":{"value":"class","subtype":""},"requirements":f"Следопыт {level}",
            "properties":[],"advancement":adv},
        "effects":effects,"folder":None,"sort":sort or level*1000,
        "flags":{MODULE:{"level":level}},"_stats":{"systemId":"dnd5e"},"_key":"!items!"+fid}
    if uses: item["system"]["uses"]=build_uses(uses)
    if uses or template:
        item["system"]["activities"]=build_activity(mid("ACT"+key),activation,bool(uses),template)
    fn=re.sub(r'[^0-9A-Za-zА-Яа-я]+','_',name).strip('_')
    json.dump(item,open(f"{SRC}/features/{fn}_{fid}.json","w"),ensure_ascii=False,indent=1)
    return fid

def A_grant(level,fids,title):
    return {"_id":mid("subG"+str(level)+title)[:16],"type":"ItemGrant","level":level,"title":title,"icon":None,"value":{},
        "configuration":{"items":[{"uuid":fuid(f),"optional":False} for f in fids],"optional":False,
            "spell":{"ability":[""],"uses":{"max":"","per":"","requireSlot":False},"prepared":0}}}
def A_choice(level,fids,title,hint=""):
    return {"_id":mid("subC"+str(level)+title)[:16],"type":"ItemChoice","title":title,"icon":None,"hint":hint,
        "value":{"added":{},"replaced":{}},
        "configuration":{"choices":{str(level):{"count":1,"replacement":False}},"allowDrops":True,"type":"feat",
            "pool":[{"uuid":fuid(f)} for f in fids],
            "spell":{"ability":[""],"uses":{"max":"","per":"","requireSlot":False},"prepared":0},
            "restriction":{"type":"","subtype":"","level":"","list":[]}}}
def A_spellgrant(level,sids,title):
    return {"_id":mid("subSPL"+str(level)+title),"type":"ItemGrant","level":level,"title":title,"icon":None,"value":{},
        "configuration":{"items":[{"optional":False,"uuid":spuid(s)} for s in sids],"optional":False,
            "spell":{"preparation":"always","ability":["wis"],"uses":{"max":"","per":"","requireSlot":False}}}}

def write_subclass(ident,name,img,desc,advancement):
    sid=mid("SUBCLASS"+ident)
    item={"_id":sid,"name":name,"type":"subclass","img":img,
        "system":{"description":{"value":desc,"chat":""},"source":SOURCE,
            "identifier":ident,"classIdentifier":"sledopyt",
            "spellcasting":{"progression":"none","ability":""},"advancement":advancement},
        "effects":[],"folder":None,"sort":0,"flags":{},"_stats":{"systemId":"dnd5e"},"_key":"!items!"+sid}
    json.dump(item,open(f"{SRC}/subclasses/{re.sub(chr(92)+'W+','_',name)}_{sid}.json","w"),ensure_ascii=False,indent=1)
    return sid

# ============================ BATCH 1: ОХОТНИК ============================
ico="icons/skills/targeting/"
hunter={}
hunter["weakness"]=write_feat("hunter-weakness","Охотник: Поиск слабостей",3,ico+"crosshair-pointed-orange.webp",
P("Когда вы выбираете существо своей Добычей, вы узнаёте, есть ли у него Иммунитеты, Сопротивления или Уязвимости, и какие именно.",
"Когда вы попадаете атакой оружием по Добыче, вы можете лишить её Сопротивления к виду урона по вашему выбору до начала вашего следующего хода.",
"Начиная с 11-го уровня, вы также можете лишить цель Иммунитета к одному состоянию или ослабить её Иммунитет к виду урона до Сопротивления."))

hunter["colossus"]=write_feat("hunter-colossus","Охотник: Убийца колоссов",3,ico+"target-strike-triple-orange.webp",
P("<em>Вариант «Тактика охоты».</em>",
"Когда вы попадаете атакой оружием по Добыче, которая больше вас как минимум на 1 категорию размера, это оружие наносит цели дополнительно 1d8 урона за каждую категорию разницы.",
"Например, будучи Среднего размера, по существу Огромного размера вы нанесёте 2d8 дополнительного урона."))

hunter["horde"]=write_feat("hunter-horde","Охотник: Сокрушитель орд",3,ico+"target-strike-triple-blue.webp",
P("<em>Вариант «Тактика охоты».</em>",
"Когда вы совершаете бросок Инициативы, вы можете не выбирать Добычу, чтобы сосредоточиться на множестве врагов.",
"Когда вы совершаете атаку оружием по существу, вы можете совершить ещё одну атаку тем же оружием против другого существа в пределах 10 футов от первоначальной цели и в пределах досягаемости оружия, которое вы ещё не атаковали в этот ход."))

swift_fx=[ae("Стремительный охотник","icons/magic/movement/trail-streak-impact-blue.webp",[C("system.attributes.movement.walk","ADD","10")],True,False,"+10 фт к скорости передвижения.")]
hunter["swift"]=write_feat("hunter-swift","Охотник: Стремительный охотник",7,"icons/magic/movement/feet-bare-light-blue.webp",
P("<em>Вариант «Стратегия охоты».</em>",
"Ваша скорость передвижения увеличивается на 10 футов, и вы можете Бонусным действием совершить Рывок, Отход или Засаду.",
"Когда вы попадаете атакой оружием по Добыче, которая не может вас видеть, вы наносите удвоенный урон от Бесконечной охоты."),effects=swift_fx)

hunter["army"]=write_feat("hunter-army","Охотник: Сокрушитель армий",7,"icons/equipment/shield/heater-steel-worn-grey.webp",
P("<em>Вариант «Стратегия охоты».</em>",
"Каждый раз, когда существо попадает по вам атакой, вы получаете бонус +2 к КД до начала вашего следующего хода.",
"Бонус к КД увеличивается до +3, если по вам попала ваша Добыча."))

hunter["magic"]=write_feat("hunter-magic","Охотник: Магия охоты",11,"icons/magic/symbols/runes-star-magenta.webp",
P("Когда вы попадаете атакой оружием по Добыче, вы можете Бонусным действием оставить на ней магическую метку, которая пропадёт в конце следующего хода существа. Выберите эффект метки:",
"<strong>Метка стайной охоты.</strong> Пока на существе есть метка, ваши союзники совершают броски атаки по цели с Преимуществом.",
"<strong>Метка уязвимости.</strong> Пока на существе есть метка, оно совершает спасброски выбранной характеристики с Помехой.",
"<strong>Метка сдерживания.</strong> Пока на существе есть метка, оно совершает все свои броски атаки с Помехой.",
"<em>Использований: модификатор Мудрости (мин. 1); восстановление после Долгого отдыха, плюс 1 использование при сотворении заклинания 3-го уровня и выше (вручную).</em>"),
uses={"max":"max(1, @abilities.wis.mod)","period":"lr"},activation=("bonus",1))

hunter["avatar"]=write_feat("hunter-avatar","Охотник: Аватар охоты",15,"icons/magic/light/explosion-star-glow-orange.webp",
P("Ваша Охотничья концентрация вышла на новый уровень. Её преимущества усиливаются:",
"<strong>Выносливость охотника.</strong> 1d12 + удвоенный модификатор Мудрости временных хитов (мин. 1) или окончание на себе одного из состояний: Отравленный, Ослеплённый, Оглохший, Испуганный, Очарованный, Ошеломлённый.",
"<strong>Меткость охотника.</strong> Бонус к броскам атаки и урона по Добыче, равный модификатору Мудрости.",
"Пока вы концентрируетесь на заклинании Следопыта, вы можете получать сразу оба преимущества Охотничьей концентрации."))

write_subclass("hunter","Охотник","icons/creatures/abilities/wolf-howl-moon-purple.webp",
P("Вы — Охотник, готовый всюду преследовать добычу, чтобы защитить природу и народы мира от гибельных сил."),
[A_grant(3,[hunter["weakness"]],"Поиск слабостей"),
 A_choice(3,[hunter["colossus"],hunter["horde"]],"Тактика охоты","Выберите один вариант (можно сменить на отдыхе)."),
 A_choice(7,[hunter["swift"],hunter["army"]],"Стратегия охоты","Выберите один вариант (можно сменить на отдыхе)."),
 A_grant(11,[hunter["magic"]],"Магия охоты"),
 A_grant(15,[hunter["avatar"]],"Аватар охоты")])
print("Hunter subclass + features written")
