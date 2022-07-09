embed <drac2>
#featureToggle
NewRes = True
NewEnchantList = True

#Campaign Toggle
Tides = True
ITM = False

# Logical check's intial setting False
ftCheck = False
halfLuck = False
reliableTalent = False
ftUse = False
divUse = False

#setting variables
craftLog    = load_json(get('craftLogs','{"projects": [{"name":"","resource":{"mundane":"","common":"", "uncommon":"","rare":""},"total":"","crafted":"","tFinish":"","helper":[{"name":"","stat":""}]}]}')).projects
projectList = load_json(get('enchantProjects','{"projects": [{"name":"","resource":{"mundane":"","common":"", "uncommon":"","rare":""},"success":{"craft":"","enchant":""},"total":{"craft":"","enchant":""},"crafted":"","tStart":"","isActive":""}]}')).projects
if NewEnchantList == True:
    weaponData = load_json(get_gvar("252ff665-22d8-4545-99b1-3508a17be6af"))
else:
    weaponData  = load_json(get_gvar("11a44ab2-e839-4f2d-bb8e-9635c689ddab"))
a, out, ch  = argparse(&ARGS&), [''], character()
lvl = level
cc = "Daily Work"
CR = "Number of Resources"
munRes = "Mundane Resource"
cMagRes = "Common Magic Resource"
uMagRes = "Uncommon Magic Resource"
rMagRes = "Rare Magic Resource"
cd = "Days Enchanting"
munResInd = "<:RS_Mundane:927670058564616233>"
cMagResInd = "<:RS_Common:927670058916913162>"
uMagResInd = "<:RS_Uncommon:927670058963075112>"
rMagResInd = "<:RS_Rare:927670058866573342>"
race = ch.race
ft = "Founder's Token"
div = "Divine Inspiration"

#[1] IF YOU ARE ASSISTING SOMEONE ELSE'S PROJECT
isAssist = a.last('t')

if not ch.cc_exists(cc):
    ch.create_cc(cc,0,1,'long','bubble')
    ch.set_cc(cc,1)
v = ch.cc_exists(cc) and ch.get_cc(cc) >= 1

#Inputs
toolUsed = a.last('u',"default")
item     = a.last('c',"active")
target   = a.last('t') if a.last('t') else None
customMats = int(a.last('m')) if a.last('m') else ""

#channel Data
runIn = ctx.channel.name
all_channels = load_json(get_gvar("13e52647-498e-4c11-925d-e5228bcc7de4")) # move channels to a gvar

channels = all_channels.dev

user_channels = []

if ITM:
    # ITM channels
    user_channels = all_channels.itm
elif Tides:
    # ITM channels
    user_channels = all_channels.tides
else:
    return f''' -title "**Function ERROR**" -f ":no_entry_sign: Daily Collect Error|Contact the Technomancers immediately as something within this code needs to be checked before running it again. (Unable to determine which campaign applies)" '''

allowedChannel = (runIn in channels) or (runIn in user_channels) or runIn.endswith("-craft-rolls") or runIn.endswith("-square-market") or runIn.endswith("-rolls-🚧")

#Priority error checks such as no Daily Work, etc before any other Errors..
if not allowedChannel:
    for x in user_channels:
        out.append(f"* #{x}")

    text = "\n".join(out)

    return f''' -title "{name} attempts to perform their daily work." -f ':no_entry_sign: Daily Tasking Error| This command can only be ran in the appropriate channels. This is restricted to:\n {text}' '''

if not v:
    return f''' -title ":x: Error: No more Daily Work uses!" -desc "{name} has already done their {cc} for this day. If this is truly incorrect, make sure to take a long rest before running this again." -f "{cc}|{ch.cc_str(cc)}" '''
if a.last('t') and not a.last('c'):
    return f''' -title ":x: Error: No item name input found!" -desc "Assisting other players need an item input. Please try again and make sure you run `!enchant -c \\"item name\\" -t @playerName.`" '''


#---------------------------------------------------------------------------ITEM SECTION
#ItemInput[1]: if no -c input from user
if item == "active":
    if projectList[0].name != "":
        for project in projectList:
            if project.isActive == "True":
                item = str(project.name)
    else:
        return f''' -title ":x: Error: You don't have any Active Project!" -desc "Please, make sure you have an active project before running `!enchant`. You can check your current Active Project by running `!enchant status`.\n\nCreate a new project by running `!enchant -c \"itemName\"`. Or you can also switch between projects by running `!enchant -c \"itemName\"` if the item is already on your project list." -f "{cc}|{ch.cc_str(cc)}" '''

#ItemInput[2]: -c input exists 
else:
    hit   = ''
    match = []
    for itemName in weaponData:
        if item.lower() == itemName.lower():
            hit      = itemName
        elif item.lower() in itemName.lower():
            itemName = itemName.replace("'", "‘")
            match.append(f"{itemName}")
    
    if hit != '':
        item = hit
    elif match == []:
        return f''' -title ":x: Error: No enchantable item matches!" -desc "**Your Input**: {item}\nPlease make sure the item you wish to enchant is listed in the Guide!" -f "{cc}|{ch.cc_str(cc)}" '''
    elif len(match) == 1:
        item = match[0].replace("‘","'")
    else:
        matchDisp   = ''  
        for x in match:
            xDisp    = f'{x}:\n `!enchant -c \\"' + f'{x}' + '\\"`\n\n'
            matchDisp += xDisp 
        
        #limits the display list to x characters
        if len(match) > 5:
            return f''' -title ":x: Error: Too many enchantable item matches found!" -desc "**Your Input:** {item}\n**Matches Found:** {len(match)} items\n\nPlease specify your item name better based on what written in the Guide." -f "{cc}|{ch.cc_str(cc)}" ''' 
        else:    
            return f''' -title "Multiple enchantable item matches found!" -desc "**Your Input:** {item}\n**Matches Found:** {len(match)} items\n\n**Please use one of the following commands:**\n {matchDisp.replace("‘","'")}\n***Note**: item matches are pulled from all enchantable items regardless your character Skill Level, Proficiency, and Resources.*"'''
#with item set up; 
#PLAYER TIER SECTION
# check tier against item
wSkill   = weaponData[item].skillLevel
tierList = load_json(get_gvar("85a93538-02c0-4277-97b2-23691449f0e1"))
cDisc    = str(ctx.author.id)
n = [ 0 for x in tierList.townfolk if x in cDisc] + [ 1 for x in tierList.tradesperson if x in cDisc] + [ 2 for x in tierList.adventurer if x in cDisc] + [ 3 for x in tierList.folkHero if x in cDisc] + [ 4 for x in tierList.heroOfTheRealm if x in cDisc] + [ 5 for x in tierList.taleweaver if x in cDisc] + [ 6 for x in tierList.masterOfTheRealm if x in cDisc] + [ 7 for x in tierList.realmweaver if x in cDisc] + [ 8 for x in tierList.legendaryHero if x in cDisc] + [ 9 for x in tierList.worldweaver if x in cDisc] + [ 10 for x in tierList.smithgardians if x in cDisc]
tier = ["townsfolk", "tradesperson", "adventurer", "folkHero", "heroOfTheRealm", "taleweaver", "masterOfTheRealm", "realmweaver", "legendaryHero", "worldweaver", "smithgardians"][n[0]]
if NewEnchantList == False:
    if wSkill == "Minor Enchant":
        if n[len(n)-1] < 6:
            return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their tier level is too low to make the item, which requires the {wSkill} skill level." -f "**Tier breakdown vs. Enchant Skill Level**:\n Master of the Realm and higher-> Minor Enchant\n Legendary Hero -> Major Enchantment" ''' 
    elif wSkill == "Major Enchant":
        if n[len(n)-1] < 8:
            return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their tier level is too low to make the item, which requires the {wSkill} skill level." -f "**Tier breakdown vs. Enchant Skill Level**:\n Master of the Realm and higher-> Minor Enchant\n Legendary Hero -> Major Enchantment" '''
if NewEnchantList == True:
    if wSkill == "Common Enchant":
        if n[len(n)-1] < 3:
            return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their tier level is too low to make the item, which requires the {wSkill} skill level." -f "**Tier breakdown vs. Enchant Skill Level**:\n Hero of the Realm and higher -> Common Enchant\n Master of the Realm and higher-> Uncommon Enchant\n Legendary Hero -> Rare Enchantment" ''' 
    if wSkill == "Uncommon Enchant":
        if n[len(n)-1] < 6:
            return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their tier level is too low to make the item, which requires the {wSkill} skill level." -f "**Tier breakdown vs. Enchant Skill Level**:\n Hero of the Realm and higher -> Common Enchant\n Master of the Realm and higher-> Uncommon Enchant\n Legendary Hero -> Rare Enchantment" ''' 
    elif wSkill == "Rare Enchant":
        if n[len(n)-1] < 8:
            return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their tier level is too low to make the item, which requires the {wSkill} skill level." -f "**Tier breakdown vs. Enchant Skill Level**:\n Hero of the Realm and higher -> Common Enchant\n Master of the Realm and higher-> Uncommon Enchant\n Legendary Hero -> Rare Enchantment" ''' 
        

#Item Enchantment setup; 
#Is the "crafting" done and therefore an enchant roll?
kind = "Crafting"
projFound = False

# total crafting time
ctotal = int(weaponData[item].craftingTime)
# total enchanting time
etotal = int(weaponData[item].enchantingTime)

#total task time
taskTotal = ctotal + etotal

if ctotal==0:
    kind = "Enchanting"
else:
    for project in projectList:
        if project.name == item:
            if int(project.success.craft) >= int(project.total.craft):
                kind = "Enchanting"
                        


#---------------------------------------------------------------------------TOOLS SECTION
#get proficiency and expertise for tools.
toolProf = get("pTools", "{}")
toolExpt = get("eTools", "{}")
    
#check Tool vs. Item allowable tool
wTool      = weaponData[item].tools
attribute = 0
p = False
e = False
attDisp = ""
tool = ""
toolList   = [" Alchemist's Supplies", " Brewer's Supplies", " Calligrapher's Supplies", " Carpenter's Tools", " Cobbler's Tools", " Cook's Utensils", " Glassblower's Tools", " Herbalism Kit", " Jeweler's Tools", " Leatherworker's Tools", " Mason's Tools", " Painter's Supplies", " Poisoner's Kit", " Potter's Tools", " Smith's Tools", " Tinker's Tools", "Weaver's Tools", "Woodcarver's Tools"] 
if wTool != "": #wTool = "" means no profs needed, 
    #ToolsInput[1]: Input -u exists
    if a.last('u'):    
        # Set up tools & skills
        ##tl.strip() -- Very important to get rid of trailing spaces for comparisons. 
        #supports toolsets by lowercase and by uppercase. 
        for tl in toolList:
            if toolUsed.lower() in tl.lower():
                toolUsed = tl.strip()
            
        if toolUsed.lower() in " carpenter's tools, mason's tools, smith's tools":
            tool = toolUsed
            attDisp   = "(STR)"
            attribute = strengthMod
        elif toolUsed.lower() in " alchemist's supplies, jeweler's Tools, poisoner's kit, tinker's tools":
            tool = toolUsed
            attDisp   = "(INT)"
            attribute = intelligenceMod
        elif toolUsed.lower() in " cobbler's tools, glassblower's tools, leatherworker's tools, painter's supplies, potter's tools, weaver's tools, woodcarver's tools":
            tool = toolUsed
            attDisp   = "(DEX)"
            attribute = dexterityMod
        elif toolUsed.lower() in " brewer's supplies, calligrapher's supplies, cook's utensils, herbalism kit":
            tool = toolUsed
            attDisp   = "(WIS)"
            attribute = wisdomMod
        else:
            return f''' -title ":x: Error: Invalid tool name!" -desc "The following list of tool names is acceptable for the command: smith, alchemist, brewer, woodcarver, potter, glassblower, calligrapher, carpenter, cobbler, cook, jeweler, leatherworker, mason, painter, tinker, weaver, poisoner, herbalism."  -f "{cc}|{ch.cc_str(cc)}" ''' 
                    
        if tool not in wTool:
            return f''' -title ":x: Error: Incorrect tool usage!" -desc "{name} attempts to craft a {item} using {tool}, however that tool is not able to craft that item.\nThe following tools can be used to create a {item}: {wTool}" -f "{cc}|{ch.cc_str(cc)}" '''

    #ToolsInput[2]: Input not exists, automate tools
    else:
    #create an array consists of tools needed to create the item

        toolNeed   = []
    
    #turns wTool into an array, and trims any extra spaces.  
        wToolList = wTool.split(",")
        for tl in wToolList:
            toolNeed.append(tl.strip())
    
    #find the highest score (attribute+prof/expt) of tool usage
        toolScore = []
        attList   = []
        attText   = []
        for tl in toolNeed:
            if tl in "Alchemist's Supplies, Jeweler's Tools, Poisoner's Kit, Tinker's Tools":
                attText.append("(INT)")
                attribute = intelligenceMod if not a.last('a') else attribute
                toolScore.append(attribute+proficiencyBonus*2 if tl in toolExpt else attribute+proficiencyBonus if tl in toolProf else 0)
                attList.append(attribute)
            elif tl in "Brewer's Supplies, Calligrapher's Supplies, Cook's Utensils, Herbalism Kit":
                attText.append("(WIS)")
                attribute = wisdomMod if not a.last('a') else attribute
                toolScore.append(attribute+proficiencyBonus*2 if tl in toolExpt else attribute+proficiencyBonus if tl in toolProf else 0)
                attList.append(attribute)
            elif tl in "Carpenter's Tools, Mason's Tools, Smith's Tools":
                attText.append("(STR)")
                attribute = strengthMod if not a.last('a') else attribute
                toolScore.append(attribute+proficiencyBonus*2 if tl in toolExpt else attribute+proficiencyBonus if tl in toolProf else 0)
                attList.append(attribute)
            elif tl in "Cobbler's Tools, Glassblower's Tools, Leatherworker's Tools, Painter's Supplies, Potter's Tools, Weaver's Tools, Woodcarver's Tools":
                attText.append("(DEX)")
                attribute = dexterityMod if not a.last('a') else attribute
                toolScore.append(attribute+proficiencyBonus*2 if tl in toolExpt else attribute+proficiencyBonus if tl in toolProf else 0)
                attList.append(attribute)
            else:
                attText.append(" ")
                toolScore.append(0)
                attList.append(0)
    

    
    #grab the tool/attribute that has the highest score
    maxValue = max(toolScore)
    maxIndex = toolScore.index(maxValue)
    tool     = toolNeed[maxIndex]
    attribute= attList[maxIndex]
    attDisp  = attText[maxIndex]
    
   #If tools required not proficient
    toolNeedDisp    = "- "+"\n - ".join(toolNeed)
    if max(toolScore) == 0:
        return f''' -title ":x: Error: Not proficient in required tools!" -desc "**Item to enchant:** {item}\n**Requires crafting with tools before enchanting. Required tool proficiency:**\n{toolNeedDisp}\n\n{name} doesn't have proficiency nor expertise in any of the tools needed to craft a(n) '{item}'!" -f "Your tool proficiencies:|**Prof**: {"None" if toolProf =="{}" else toolProf}\n**Expt**: {"None" if toolExpt=="{}" else toolExpt}" -f "Adding Tool Proficiency|`!tool pro \\"tool name\\"`|inline" -f "Adding Tool Expertise|`!tool exp \\"tool name\\"`|inline" -f "{cc}|{ch.cc_str(cc)}" '''

    #check tool profs
    p = False
    e = False
    if tool in toolExpt:
        e =  True
        eBonus = proficiencyBonus*2
    else:
        if tool in toolProf:
            p =  True   
            pBonus = proficiencyBonus
        else:
            return f''' -title ":x: Error: Not proficient in selected tools!" -desc "**Tool input:**\n{toolUsed}\n\n{name} doesn't have proficiency nor expertise in {toolUsed}!" -f "Your tool proficiencies:|**Prof**: {"None" if toolProf =="{}" else toolProf}\n**Expt**: {"None" if toolExpt=="{}" else toolExpt}" -f "Adding Tool Proficiency|`!tool pro \\"tool name\\"`|inline" -f "Adding Tool Expertise|`!tool exp \\"tool name\\"`|inline" -f "{cc}|{ch.cc_str(cc)}" '''
#end of code to be run when tools are needed

#[1] Crafting time, Enchanting Time and Resources
adv,dis,fireRune = "adv" in a and not "dis" in a,"dis" in a and not "adv" in a, "fireRuneCheck" in a
if NewRes == True:
    munResNeeded = weaponData[item].resources.mundane if not customMats or customMats == "True" else customMundaneMats
    cMagResNeeded = weaponData[item].resources.common if not customMats or customMats == "True" else customCommonMats
    uMagResNeeded = weaponData[item].resources.uncommon if not customMats or customMats == "True" else customUncommonMats
    rMagResNeeded = weaponData[item].resources.rare if not customMats or customMats == "True" else customRareMats
else:
    resNeeded = weaponData[item].resources if not customMats or customMats == "True" else customMats
craftTime = int(weaponData[item].craftingTime)
enchantTime = int(weaponData[item].enchantingTime)
successCraft = 0
successEnchant = 0
adjCraftTime = ceil(craftTime/2)
adjEnchantTime = enchantTime

#enchanting bonus
sc = True if ch.spellbook.dc else False
spellAttack = 0
if sc:
    spellAttack = ch.spellbook.sab if ch.spellbook.sab  != None else 0
nonSpellBonus = max(intelligenceMod,wisdomMod,charismaMod)
enchantBonus = max(spellAttack,nonSpellBonus)

#setting up resources held variable. Errors out with "0" if cc doesn't exist.  
#errors out even if 
#does project exist:
exist = False
for project in projectList:
    if project.name == item:
        exist = True
resHeld = 0
if isAssist:
    # do nothing
    isAssist = isAssist
elif NewRes == True:
    if ch.cc_exists(munRes):
        munResHeld = ch.get_cc(munRes)
        rType = munRes
        rIndicator = munResInd
    if weaponData[item].resources.mundane > munResHeld and exist == False:
        return f''' -title "{rIndicator} Error: Insufficient {rType}s!" -desc "{item} Requires the item to be crafted first. You do not have enough {rType}s to start a(n) {item}; you need {munResNeeded} to do so, and you have {munResHeld} {rType}s on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    if lvl > 4:
        if ch.cc_exists(cMagRes):
            rType = cMagRes
            cMagResHeld = ch.get_cc(cMagRes)
            rIndicator = cMagResInd
        if weaponData[item].resources.common > cMagResHeld and exist == False:
            return f''' -title "{rIndicator} Error: Insufficient {rType}s!" -desc "{item} Requires the item to be crafted first. You do not have enough {rType}s to start a(n) {item}; you need {cMagResNeeded} to do so, and you have {cMagResHeld} {rType}s on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    else:
        cMagResHeld = 0 
    if lvl > 9:
        if ch.cc_exists(uMagRes):
            rType = uMagRes
            rIndicator = uMagResInd
            uMagResHeld = ch.get_cc(uMagRes) 
        if weaponData[item].resources.uncommon > uMagResHeld and exist == False:
            return f''' -title "{rIndicator} Error: Insufficient {rType}s!" -desc "{item} Requires the item to be crafted first. You do not have enough {rType}s to start a(n) {item}; you need {uMagResNeeded} to do so, and you have {uMagResHeld} {rType}s on your person." -f "{cc}|{ch.cc_str(cc)}" ''' 
    else:
        uMagResHeld = 0
    if lvl > 14:
        if ch.cc_exists(rMagRes):
            rType = rMagRes
            rMagResHeld = ch.get_cc(rMagRes)
            rIndicator = rMagResInd            
        if weaponData[item].resources.rare > rMagResHeld and exist == False:
            return f''' -title "{rIndicator} Error: Insufficient {rType}s!" -desc "{item} Requires the item to be crafted first. You do not have enough {rType}s to start a(n) {item}; you need {rMagResNeeded} to do so, and you have {rMagResHeld} {rType}s on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    else:
        rMagResHeld = 0
else:
    if ch.cc_exists("Number of Resources"):
        resHeld = ch.get_cc("Number of Resources")  
    if weaponData[item].resources > resHeld and exist == False:
        return f''' -title ":x: Error: Insufficient resources!" -desc "{item} Requires the item to be crafted first. You do not have enough resources to start a(n) {item}; you need {resNeeded} to do so, and you have {resHeld} on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    
if kind == "Enchanting":
    DC = 15
else:
    DC = 12 if n[0] < 4 else 10


#[2] CVAR Time variables
anchorPts   = 1627232400 #Jul 26, 00:00:00 (GMT+7)
timeHrs     = (time()-anchorPts)/3600
tStart      = (''+timeHrs).split('.')[0]
pjCraft = "self"

#[3] other variables needed to declare for enchantProjects CVAR
pjSwitch    = False
n           = 0
for project in projectList:
    n += 1
    if project.name == item:
        pjCount     = n-1
        pjSwitch    = True
        successCraft     = int(project.success.craft)
        successEnchant = int(project.success.enchant)
        adjCraftTime= int(project.total.craft)
        adjEnchantTime= int(project.total.enchant)

#-----------------------------ROLL CHECK VARIABLES------------------------
#[0] Reliable Talent
RgLevel        = int(get('RogueLevel',0))
rTalentDisp    = ""
if RgLevel >10:
    reliableTalent = True
if reliableTalent: 
    rTalentDisp    = "Reliable Talent|Whenever you make an ability check that lets you add your Proficiency Bonus, you can treat a d20 roll of 9 or lower as a 10." 

#[1] Halfling Luck
halfling =  ["Lightfoot Halfling","Stout Halfling","Ghostwise Halfling","Lotusden Halfling","Mark of Healing Halfling","Mark of Hospitality Halfling"] 
hLuck = ""
if race in halfling:
    halfLuck = True
    hLuck = "Halfling Luck|When you roll a 1 on the d20 for an attack roll, ability check, or saving throw, you can reroll the die and must use the new roll."

#[2] Crafting time and Resources
adv,dis,fireRune,SGL = "adv" in a and not "dis" in a,"dis" in a and not "adv" in a, "fireRuneCheck" in a, "sgl" in a

#[3] Founder's Token
# create founder's token and check if runnable
ftDisp = ""
for x in tierList.founder:
    if x == cDisc:
        # Founder Token token creation, set, and check
        if not ch.cc_exists(ft):
            ch.create_cc(ft,0,1,"long","bubble")
            ch.set_cc(ft,1, True)
        ftCheck = ch.cc_exists(ft)
        ftActive = ch.get_cc(ft)>=1
if "founder".lower() in a:
    ftUse = True
    if ftCheck:
        if ftActive:
            ch.mod_cc(ft,-1)
            adv = True
            ftDisp = "Founder's Token|Thank you for supporting RealmSmith from the beginning of the server, Take advantage on this roll in our appreciation." 
        else: 
            ftDisp = ":no_entry_sign: Founder's Token Error|Thank you for supporting RealmSmith from the beginning of the server, you have already used your token today, if this is in error please contact a Realmwatcher or Avrae Technomancer for assistance in a possible re-roll."
else:
    ftDisp = ""
#[4] Divine Inspiration
# check if Divine Inspiration is runnable
if "dInspiration".lower() in a or "dInspiration" in a or "dinspiration" in a:
    divCheck = ch.cc_exists(div)
    divActive = ch.get_cc(div)==1
    divUse = True
    if divCheck:
        if divActive:
            ch.mod_cc(div,-1)
            adv = True
            divDisp = "Divine Inspiration|The six have provided you this daily inspiration by your generousity at their temple in Herethis."
        else: 
            divDisp = ":no_entry_sign: Function Error|You have either taken a long rest, or do not have a Divine Inspiration. A divine inspiration is obtained at the Temple of the Six for 5 gold."
    else:
        divDisp = ":no_entry_sign: Function Error|You have either taken a long rest, or do not have a Divine Inspiration. A divine inspiration is obtained at the Temple of the Six for 5 gold."
else:
    divDisp = ""

#kind = "Enchanting", "Crafting"; enchantBonus
#[4] roll check variables
if reliableTalent:
    craftd20String   = "2d20kh1mi10+" if adv else "2d20kl1mi10+" if dis else "1d20mi10+"
elif halfLuck:
    craftd20String   = "2d20kh1ro1+" if adv else "2d20kl1ro1+" if dis else "1d20ro1+" 
else:
    craftd20String   = "2d20kh1+" if adv else "2d20kl1+" if dis else "1d20+"
craftRoll   = craftd20String +str(attribute) + (( f'+{pBonus}' if p and not e else " ")+(" [proficiency]" if p and not e else " ")) + (( f'+{eBonus}' if e else " ")+(" [expertise]" if e else " ")) + (( f'+{proficiencyBonus}' if fireRune else " ")+(" [Fire Rune]" if fireRune else " "))


enchantd20String   = "2d20kh1+" if adv else "2d20kl1+" if dis else "1d20+"
enchantRoll =  enchantd20String + str(enchantBonus) + (( f'+{proficiencyBonus}' if fireRune else " ")+(" [Fire Rune]" if fireRune else " "))
if kind == "Enchanting":
    check   = vroll(enchantRoll)
else:
    check = vroll(craftRoll)
crit    = check.result.crit
cStatus = ":x: **Check status:** Failed"

#[5] variables specific for displays/output
attDisp = f"({aId.upper()})" if a.last('a') else attDisp
matOR   = "" if not a.last('m') else f"custom material input"
ctmDisp = "" if not matOR else f"*This command is run with {matOR if matOR else ''}!*\n\n"
enchantRules = "In order to enchant a magic item you will be able to make a single check per long rest to see if you are successful in enchanting or not. Each day your character may make an ability check using your spellcasting ability. With a successful total roll of 15 or higher you succeed in enchanting for that day. Any class that does not specify a spellcasting ability may use either Intelligence, Wisdom or Charisma. As shown on the Enchanting Table below, certain items require a certain number of days worth of collecting, crafting and enchanting time in order to be successfully completed. Rolling a Natural 20 counts for two successful days of enchanting, whereas a Natural 1 results in a fail and adds an additional one day to the required days for crafting. "
craftRules = "In some cases, you must craft the item to be enchanted. In order to craft an item you will be able to make a single check per long rest to see if you are successful in crafting or not. Each day your character may make a Proficiency Check with the associated tools/kit. With a successful total roll of 12 or higher you succeed in crafting for that day. Heroes of the Realm and higher only require a successful total roll of 10 or higher. Rolling a Natural 20 counts for two successful days of crafting, whereas a Natural 1 results in an additional failed day above the one you rolled for."
delCvar = False

#---------------------------------------------------------------------------ROLL CHECKS
#[1] IF YOU ARE ASSISTING SOMEONE ELSE'S PROJECT
if isAssist:
    if "@" not in target:
        return f''' -title ":x: Error: Invalid player name input format!" -desc "Assisting other players need a target input format with @playerName to ping the player. Please try again and make sure you run `!enchant -c \\"item name\\" -t @playerName.`" '''
    #checking to see if helping is allowable, 
    if taskTotal < 14:
        return f''' -title ":x: Error: Crafting project '{item}' cannot be assisted!" -desc "Only Enchanting projects that require 14 days or more can be helped by another player of same tier. Please check the Guide section 'Crafting the Vistani Way' for more information. {item} default's crafting time is `{taskTotal}` days." '''
    ch.mod_cc(cc,-1,True)
    cmdStat = "fail"
    #roll results
    if crit == 2:
        cStatus     = ":x: **Check status:** Critical Fail"
        cmdStat     = "critfail"
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            cmdStat = "crits"
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            cmdStat = "success"
    
    #required variables for !enchant helped command
    cmdPing = "@" + ctx.author
    cmdHelp = f"Please make sure {target} run below command:\n ``!enchant helped -c \\\"{item}\\\" -t \\\"{name}\\\" -s {cmdStat} -p {cmdPing}``" if cmdStat != "fail" else "The check result is a failure. No command needed to run by the player you helped."
    
    out.append(f''' -title "{name} works to help with {kind} another crafter\'s {item} {"" if weaponData[item].tools == "" else "using their {tool}"}." ''')
    #Description output -- helping someone else's project
    if kind == "Enchanting":
        out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**Enchanting:** {check}\n{cStatus}\n**Crafter helped:** {target}" -f "Realmsmith's Enchanting Guide| {enchantRules}" -f "You are assisting another player|{cmdHelp}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
        if divUse:
            out.append(f''' -f "{divDisp}" ''')
            if divActive:
                out.append(f''' -f "{div} (-1)|{ch.cc_str(div)}" ''')
            else:
                out.append(f''' -f "{div}|{ch.cc_str(div)}" ''')
    else:
        out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**Tool check {attDisp}:** {check}\n{cStatus}\n**Crafter helped:** {target}" -f "Realmsmith's Crafting Guide| {craftRules}" -f "You are assisting another player|{cmdHelp}" ''')
        if halfLuck:
            out.append(f''' -f "{hLuck}" ''')
        if reliableTalent:
            out.append(f''' -f "{rTalentDisp}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
        if divUse:
            out.append(f''' -f "{divDisp}" ''')
            if divActive:
                out.append(f''' -f "{div} (-1)|{ch.cc_str(div)}" ''')
            else:
                out.append(f''' -f "{div}|{ch.cc_str(div)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''')
    return '\n'.join(out)    


#[1.1] CRAFT FOR SELF, IF THE PROJECT ALREADY EXISTS
elif pjSwitch == True:
    delCvar = False
    ch.mod_cc(cc,-1,True)
    
    #roll results
    if crit == 2:
        cStatus      = ":x: **Check status:** Critical Fail"
        if kind == "Enchanting":
            adjEnchantTime += 1
        else: 
            adjCraftTime += 1
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            if kind == "Enchanting":
                successEnchant += 2
            else:
                successCraft += 2
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            if kind == "Enchanting":
                successEnchant += 1
            else:
                successCraft += 1
    
#[1.1.1] if the project is completed
    if successEnchant >= adjEnchantTime:
        out.append(f''' -title "Congrats! {name} has completed enchanting an {item}!" -f ":grey_exclamation: Enchanting Complete | To add [item] to your inventory, you may add this to your Avrae bag using the !bag command, and you must add it to your equipment in Dndbeyond, if this effects character actions/spells you will want to run ``!update`` afterwards."''')
        #if the project is helped by another player, edit enchantHelpers CVAR, take data needed for craftLog
        if projectList[pjCount].crafted == "helped":
            helperList  = load_json(get('enchantHelpers','{"projects": [{"name":"","helper":[{"name":"","stat":["","",""]}]}]}')).projects
            hpCount     = len(helperList)
            for project in helperList:
                if project.name == item:
                    pjIndex     = helperList.index(project)
                    helpers     = ''
    #Get required helper info for craftLog    
                    for crafter in helperList[pjIndex].helper:
                        cont    = int(crafter.stat[0])+ int(crafter.stat[1])*2 - int(crafter.stat[2])
                        string  = '{"name": "'+ crafter.name +'","stat": "' + cont  + '"},'
                        helpers += string 
                    
                    delComma    = len(helpers)-1
                    helpers     = helpers[:delComma]
                    helper      = '"helper": [' + helpers + ']'  #this is for the craftLog
                    helperList.remove(project)
            
            if hpCount == 1:
                #it's the only one project that's helped in the list
                ch.delete_cvar("enchantHelpers")
            else:
                #reconstruct enchantProjects CVAR
                projects = ''
                for project in helperList:
                    helper    = "" + project.helper
                    string    = '{"name": "'+ project.name + '","helper":' + helper.replace("'", "^").replace('^','"') + '},'
                    projects += string
                                
                delComma    = len(projects)-1
                projects    = projects[:delComma]
                newE         = '{"projects": [' + projects + ']}'
                
                ch.set_cvar("enchantHelpers", newE)
                
    #Get required info for craftLog if there's no helper       
        else:
            helper  = '"helper": [{"name": "n/a","stat": "n/a"}]'  #this is for the craftLog
            
     #reconstruct data for craftLog CVAR
        hFinish = (time()-anchorPts)/3600
        dayWork = (hFinish - int(projectList[pjCount].tStart))//24
        tFinish = (''+dayWork).split('.')[0]
        if NewRes == True:
            newLog  = '{"name": "'+projectList[pjCount].name+'","resource":"'+projectList[pjCount].resource+'" ,"total": "'+(int(projectList[pjCount].total.craft) + int(projectList[pjCount].total.enchant)) +'","crafted": "'+projectList[pjCount].crafted+'","tFinish": "'+tFinish+'", '+helper+ '}'
            if craftLog[0].name == '':
                new = '{"projects": [' + newLog + ']}'
            else:
                projects= ''
                for project in craftLog:
                    helper   = "" + project.helper
                    string   = '{"name": "'+project.name+'","resource": "'+project.resource+'","total": "'+(int(projectList[pjCount].total.craft) + int(projectList[pjCount].total.enchant))+'","crafted": "'+project.crafted+'","tFinish": "'+project.tFinish+'","helper": '+helper.replace("'", "^").replace('^','"')+ '},'
                    projects += string
                new = '{"projects": [' + projects + newLog + ']}'
            ch.set_cvar("craftLogs", new)

        else:
            newLog  = '{"name": "'+projectList[pjCount].name+'","resource":"'+projectList[pjCount].resource+'","total": "'+(int(projectList[pjCount].total.craft) + int(projectList[pjCount].total.enchant)) +'","crafted": "'+projectList[pjCount].crafted+'","tFinish": "'+tFinish+'", '+helper+ '}' 
            if craftLog[0].name == '':
                new = '{"projects": [' + newLog + ']}'
            else:
                projects= ''
                for project in craftLog:
                    helper   = "" + project.helper
                    string   = '{"name": "'+project.name+'","resource": "'+project.resource+'","total": "'+(int(projectList[pjCount].total.craft) + int(projectList[pjCount].total.enchant))+'","crafted": "'+project.crafted+'","tFinish": "'+project.tFinish+'","helper": '+helper.replace("'", "^").replace('^','"')+ '},'
                    projects += string
                new = '{"projects": [' + projects + newLog + ']}'
            ch.set_cvar("craftLogs", new)
        
        #delete the current project and set project on the top of the list as active
        projectList.remove(projectList[pjCount])
        if len(projectList) == 0:
            delCvar  = True
            ch.delete_cvar("enchantProjects")

        else:
            pjActive = '{"name": "'+ projectList[0].name + '","resource": "'+ projectList[0].resource + '","success": {"craft": "'+ projectList[0].success.craft + '", "enchant": "' + projectList[0].success.enchant +'" }, "total": {"craft": "'+ projectList[0].total.craft + '", "enchant": "' + projectList[0].total.enchant +'" }, "crafted": "'+ projectList[0].crafted + '","tStart": "'+ projectList[0].tStart + '","isActive": "True"},'
            for project in projectList:
                projects    = ''
                if project.name == projectList[0].name:
                    string      = ''
                    projects   += string
                else:
                    string      = '{"name": "'+ project.name + '","resource": "'+ project.resource + '","success": {"craft": "'+ project.success.craft + '", "enchant": "' + project.success.enchant +'" }, "total": {"craft": "'+ project.total.craft + '", "enchant": "' + project.total.enchant +'" }, "crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                    projects   += string  
            newE = '{"projects": [' + pjActive + projects  + ']}'
            
            #delete a comma after last entry
            delComma = len(newE)-3
            newE      = newE[:delComma] + newE[-2:]
            ch.set_cvar("enchantProjects", newE)

          
#[1.1.2] if the project is not completed
    else:
        if kind == "Enchanting":
            if successEnchant == 0:
                out.append(f''' -title "{name} starts to work on enchanting {item}!" ''')
            else:
                out.append(f''' -title "{name} continues to work on enchanting {item}" ''')
        else:
            if successCraft >= adjCraftTime:
                if crit ==1 :
                        successCraft = adjCraftTime
                out.append(f''' -title "{name} finishes crafting {item} using their {tool}!" ''')
                out.append(f''' -f "This project is not over; {item} still needs to be enchanted" ''')

            else:
               out.append(f''' -title "{name} continues crafting {item} using their {tool}" ''')
        pjCraft = "self"
        #create cvar
        if NewRes == True:
            pjNew   = '{"name": "'+ item + '","resource": {"mundane": "'+ munResNeeded+ '", "common": "'+ cMagResNeeded+ '", "uncommon": "'+ uMagResNeeded+ '", "rare": "'+ rMagResNeeded+ '"},"success": {"craft": "'+ successCraft + '", "enchant": "' + successEnchant +'" }, "total": {"craft": "'+ adjCraftTime + '", "enchant": "' + adjEnchantTime +'" }, "crafted": "' + pjCraft + '","tStart": "'+ tStart + '","isActive": "True"},'
        else:
            pjNew   = '{"name": "'+ item + '","resource": "'+ resNeeded+ '","success": {"craft": "'+ successCraft + '", "enchant": "' + successEnchant +'" }, "total": {"craft": "'+ adjCraftTime + '", "enchant": "' + adjEnchantTime +'" }, "crafted": "' + pjCraft + '","tStart": "'+ tStart + '","isActive": "True"},'
            
        if projectList[0].name =="":
            newE = '{"projects": [' + pjNew + ']}'
        else:
            projects = ""    
            for project in projectList:
                if project.name == item:
                    string      = '{"name": "'+ project.name + '","resource": "'+ project.resource + '","success": {"craft": "'+ successCraft + '", "enchant": "' + successEnchant +'" }, "total": {"craft": "'+ adjCraftTime + '", "enchant": "' + adjEnchantTime +'" }, "crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "True"},'
                    projects   += string
                else:
                    string      = '{"name": "'+ project.name + '","resource": "'+ project.resource + '","success": {"craft": "'+ project.success.craft + '", "enchant": "' + project.success.enchant +'" }, "total": {"craft": "'+ project.total.craft + '", "enchant": "' + project.total.enchant +'" }, "crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                    projects   += string        
            newE      = '{"projects": [' + projects  + ']}'
    

            #delete a comma after last entry
            delComma = len(newE)-3
            newE      = newE[:delComma] + newE[-2:]
        ch.set_cvar("enchantProjects", newE)
    
   #OUTPUTS
    if NewRes == True:
        projectList = load_json(get('enchantProjects','{"projects": [{"name":"","resource":{"mundane:"", "common":"", "uncommon":"", "rare": ""},"success":{"craft":"","enchant":""},"total":{"craft":"","enchant":""},"crafted":"","tStart":"","isActive":""}]}')).projects
    else:
        projectList = load_json(get('enchantProjects','{"projects": [{"name":"","resource":"","success":{"craft":"","enchant":""},"total":{"craft":"","enchant":""},"crafted":"","tStart":"","isActive":""}]}')).projects
    pjList   = []
    for project in projectList:
        
        pjList.append(f"{project.name} <status: {int(project.success.craft) + int(project.success.enchant)}/{int(project.total.craft) + int(project.total.enchant)}> {'*(Active Project)*' if project.isActive == 'True' else ''}")
  
    pjDisp   = 'None\n*Create a new crafting project with `!enchant -c "item name"` before you run `!enchant` again.*' if delCvar == True else " - "+"\n - ".join(pjList)
  
    if craftTime == 0:
        pjStatus = f"{successEnchant}/{adjEnchantTime}"
    else:
        pjStatus = f"Crafting:{successCraft}/{adjCraftTime} Enchanting:{successEnchant}/{adjEnchantTime}"

  #description output --ongoing project not completed
    disp = "" 
    if kind == "Enchanting":
        disp = "Enchanting:"
    else:
        disp = "Tool check "+attDisp + ":"
    out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**{disp}** {check}\n{cStatus}\n**Project status:** {pjStatus}" -f ":scroll: Your current projects:|{pjDisp}" ''')
    if kind == "Enchanting":
        out.append(f'''-f "Realmsmith's Enchanting Guide| {enchantRules}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
        if divUse:
            out.append(f''' -f "{divDisp}" ''')
            if divActive:
                out.append(f''' -f "{div} (-1)|{ch.cc_str(div)}" ''')
            else:
                out.append(f''' -f "{div}|{ch.cc_str(div)}" ''')
    else:
        out.append(f'''-f "Realmsmith's Crafting Guide| {craftRules}" ''')
        if halfLuck:
            out.append(f''' -f "{hLuck}" ''')
        if reliableTalent:
            out.append(f''' -f "{rTalentDisp}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
        if divUse:
            out.append(f''' -f "{divDisp}" ''')
            if divActive:
                out.append(f''' -f "{div} (-1)|{ch.cc_str(div)}" ''')
            else:
                out.append(f''' -f "{div}|{ch.cc_str(div)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''')
    return '\n'.join(out)    
        
#[1.2] CRAFT FOR SELF, IF PROJECT NOT EXISTS: create a new project

# combined res check
if NewRes == True:
    if int(munResHeld) >= int(munResNeeded):
        munResCheck = True
    else:
        munResCheck = False
    if int(cMagResHeld) >= int(cMagResNeeded):
        cMagResCheck = True
    else:
        cMagResCheck = False
    if int(uMagResHeld) >= int(uMagResNeeded):
        uMagResCheck = True
    else:
        uMagResCheck = False
    if int(rMagResHeld) >= int(rMagResNeeded):
        rMagResCheck = True
    else:
        rMagResCheck = False
    resCheck = True if munResCheck == True and cMagResCheck == True and uMagResCheck == True and rMagResCheck == True else False
else:
    if int(resHeld) >= int(resNeeded):
        resCheck = True
    else:
        resCheck = False
    
if resCheck == True:
    #cc stuffs
    if NewRes == True:
        if munResNeeded > 0:
            ch.mod_cc(munRes,-munResNeeded,True)
        if cMagResNeeded > 0:
            ch.mod_cc(cMagRes,-cMagResNeeded,True)
        if uMagResNeeded > 0:
            ch.mod_cc(uMagRes,-uMagResNeeded,True)
        if rMagResNeeded > 0:
            ch.mod_cc(rMagRes,-rMagResNeeded,True)
    else:
        ch.mod_cc("Number of Resources",-resNeeded,True)
    ch.mod_cc(cc,-1,True)
    
    #roll results

    if crit == 2:
        cStatus      = ":x: **Check status:** Critical Fail"
        if kind == "Enchanting":
            adjEnchantTime += 1
        else: 
            adjCraftTime += 1
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            if kind == "Enchanting":
                successEnchant += 2
            else:
                successCraft += 2
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            if kind == "Enchanting":
                successEnchant += 1
            else:
                successCraft += 1

    
#[1.2.1] if new project completed as the same day it's started, no need Rearrange CVAR
#not a valid thing in the enchanting setup        
    

#[1.2.2] if new project still going    
    if kind == "Enchanting":
        if successEnchant == 0:
                out.append(f''' -title "{name} starts to work on enchanting {item}!" ''')
        else:
                out.append(f''' -title "{name} continues to work on enchanting {item}" ''')
    else:
        if successCraft >= adjCraftTime:
            if crit ==1 :
                successCraft = adjCraftTime
            else:
               out.append(f''' -title "{name} continues crafting {item} using their {tool}" ''')
    #create the project's CVAR    
    pjCraft = "self"
    if NewRes == True:
        pjNew   = '{"name": "'+ item + '", "resource": {"mundane": "'+munResNeeded+'", "common": "'+cMagResNeeded+'", "uncommon": "'+uMagResNeeded+'", "rare": "'+rMagResNeeded+'" },"success": {"craft": "'+ successCraft + '", "enchant": "' + successEnchant +'" }, "total": {"craft": "'+ adjCraftTime + '", "enchant": "' + adjEnchantTime +'" }, "crafted": "' + pjCraft + '","tStart": "'+ tStart + '","isActive": "True"},'
    else:
        pjNew   = '{"name": "'+ item + '","resource":"'+resNeeded+'","success": {"craft": "'+ successCraft + '", "enchant": "' + successEnchant +'" }, "total": {"craft": "'+ adjCraftTime + '", "enchant": "' + adjEnchantTime +'" }, "crafted": "' + pjCraft + '","tStart": "'+ tStart + '","isActive": "True"},'
        
    if projectList[0].name =="":
        newE = '{"projects": [' + pjNew + ']}'
    else:
        projects = ""
        for project in projectList:
                string = '{"name": "'+ project.name + '","resource": "'+ project.resource + '","success": {"craft": "'+ project.success.craft + '", "enchant": "' + project.success.enchant +'" }, "total": {"craft": "'+ project.total.craft + '", "enchant": "' + project.total.enchant +'" }, "crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                projects += string
        newE = '{"projects": [' + pjNew  + projects + ']}'
       
    #delete a comma afer last entry before set the CVAR    
    delComma = len(newE)-3
    newE      = newE[:delComma] + newE[-2:]
    ch.set_cvar("enchantProjects", newE)
    
    
   #OUTPUTS
    projectList = load_json(get('enchantProjects','{"projects": [{"name":"","resource":{"mundane":"","common":"", "uncommon":"","rare":""},"success":{"craft":"","enchant":""},"total":{"craft":"","enchant":""},"crafted":"","tStart":"","isActive":""}]}')).projects
    pjList  = []
    for project in projectList:
        pjList.append(f"{project.name} <status: {int(project.success.craft) + int(project.success.enchant)}/{int(project.total.craft) + int(project.total.enchant)}> {'*(Active Project)*' if project.isActive == 'True' else ''}")
    pjDisp  = 'None\n*Create a new enchanting project with `!enchant -c "item name"` before you run `!enchant` again.*' if projectList[0].name =="" else " - "+"\n - ".join(pjList)
    if craftTime == 0:
        pjStatus = f"{successEnchant}/{adjEnchantTime}"
    else:
        pjStatus = f"Crafting:{successCraft}/{adjCraftTime} Enchanting:{successEnchant}/{adjEnchantTime}"

    #DESCRIPTION OUTPUT -- new project still going 
    disp =""
    if kind == "Enchanting" :
        disp = "Enchanting:"
        if NewRes == False:
            rescDisp = "Resources Held (None Spent!):"
        else:
            munRescDisp = "Mundane Resources held (-"+ munResNeeded +"):"
            cMagRescDisp = "Common Magic Resources held (-"+ cMagResNeeded +"):"
            uMagRescDisp = "Uncommon Magic Resources held (-"+ uMagResNeeded +"):"
            rMagRescDisp = "Rare Magic Resources held (-"+ rMagResNeeded +"):"
    else:
        disp = "Tool check "+attDisp + ":"
        if NewRes == False:
            rescDisp = "Resources held (-"+ resNeeded +"):"
        else:
            munRescDisp = "Mundane Resources held (-"+ munResNeeded +"):"
            cMagRescDisp = "Common Magic Resources held (-"+ cMagResNeeded +"):"
            uMagRescDisp = "Uncommon Magic Resources held (-"+ uMagResNeeded +"):"
            rMagRescDisp = "Rare Magic Resources held (-"+ rMagResNeeded +"):"
            
    if NewRes == True:
        out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**{disp}** {check}\n{cStatus}\n**Project status:** {pjStatus}" ''')
        if munResNeeded > 0:
            out.append(f''' -f "{munResInd}**{munRescDisp}** {ch.cc_str(munRes)}" ''')
        if cMagResNeeded > 0:
            out.append(f''' -f "{cMagResInd}**{cMagRescDisp}** {ch.cc_str(cMagRes)}" ''')
        if uMagResNeeded > 0:
            out.append(f''' -f "{uMagResInd}**{uMagRescDisp}** {ch.cc_str(uMagRes)}" ''')
        if rMagResNeeded > 0:
            out.append(f''' -f "{rMagResInd}**{rMagRescDisp}** {ch.cc_str(rMagRes)}" ''')            
        out.append(f''' -f ":scroll: Your current projects:|{pjDisp}" ''')    
    else:
        out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**{disp}** {check}\n{cStatus}\n**Project status:** {pjStatus}\n**{rescDisp}** {ch.cc_str(CR)}" -f ":scroll: Your current projects:|{pjDisp}" ''')
    if kind == "Enchanting":
        out.append(f'''-f "Realmsmith's Enchanting Guide| {enchantRules}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
    else:
        out.append(f'''-f "Realmsmith's Crafting Guide| {craftRules}" ''')
        if halfLuck:
            out.append(f''' -f "{hLuck}" ''')
        if reliableTalent:
            out.append(f''' -f "{rTalentDisp}" ''')
        if ftUse:
            out.append(f''' -f "{ftDisp}" ''')
            if ftActive:
                out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
            else:
                out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
        if divUse:
            out.append(f''' -f "{divDisp}" ''')
            if divActive:
                out.append(f''' -f "{div} (-1)|{ch.cc_str(div)}" ''')
            else:
                out.append(f''' -f "{div}|{ch.cc_str(div)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''') 
else: 
    if NewRes == True:
        rCombineNeeded = "{munResInd} mundane resources {munResNeeded},{cMagResInd} common magic resources {cMagResNeeded}, {uMagResInd} uncommon magic resources {uMagResNeeded}, {rMagResInd} rare magic resources {rMagResNeeded}."
        rCombineHeld = "{munResInd}{munResHeld} mundane resources , {cMagResInd}{cMagResHeld} common magic resources, {uMagResInd}{uMagResHeld} uncommon magic resources, {rMagResInd}{rMagResHeld} rare magic resources."
        return f''' -title ":x: Error: Insufficient resource amounts!" -desc "You does not have enough resources to craft a(n) {item}; you need {rCombineNeeded} to do so, and you have {rCombineHeld} on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    if NewRes == False:
        return f''' -title ":x: Error: Insufficient resource amounts!" -desc "You does not have enough resources to craft a(n) {item}; you need {resNeeded} to do so, and you have {resHeld} on your person." -f "{cc}|{ch.cc_str(cc)}" '''
return '\n'.join(out)

</drac2>
-thumb https://media.discordapp.net/attachments/722314600623898674/923703977416204398/RS_dailyEnchanting.png
-color <color>

-footer '!enchant -c "item name" [-t @player]  | help'
