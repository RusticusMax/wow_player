from lxml import html
import requests
import sys  # contains stderr object for debug output

# TODO: Create excel file directly with openpyxl module/with graph

# Changed remote repo name: "git remote set-url origin 'https://RusticusMax@bitbucket.org/RusticusMax/wow_player_histo.git'"
# Variables 
# Debug flag.  Set to non zero for debug
DEBUG_OUT=1          
# Number of players to process
PLAYER_MAX=901
# Number of players to count for each histogram bucket dictionary
HISTO_WIDTH=20 #int(PLAYER_MAX/HISTO_BAR_COUNT)   
# number of histogram bars - and HISTO_WIDTH-1 to PLAYER_MAX to deal with possible truncation by int()``
HISTO_BAR_COUNT=int((PLAYER_MAX+HISTO_WIDTH-1)/HISTO_WIDTH)
# Only include data for the top n classes in histogram to reduce noise in graph
HISTO_TOP_X=10




# Dictionary for counting classes
class_list = { " Windwalker Monk":0,        " Holy Paladin":0,          " Frost Death Knight":0,
               " Restoration Druid":0,      " Survival Hunter":0,       " Frost Mage":0,
               " Restoration Shaman":0,     " Retribution Paladin":0,   " Shadow Priest":0,
               " Arms Warrior":0,           " Elemental Shaman":0,      " Feral Druid":0,
               " Balance Druid":0,          " Destruction Warlock":0,   " Affliction Warlock":0,
               " Subtlety Rogue":0,         " Mistweaver Monk":0,       " Unholy Death Knight":0,
               " Assassination Rogue":0,    " Protection Paladin":0,    " Discipline Priest":0,
               " Enhancement Shaman":0,     " Arcane Mage":0,           " Demonology Warlock":0,
               " Guardian Druid":0,         " Havoc Demon Hunter":0,    " Fire Mage":0,
               " Marksmanship Hunter":0,    " Holy Priest":0,           " Outlaw Rogue":0,
               " Beast Mastery Hunter":0,   " Protection Warrior":0,    " Blood Death Knight":0,
               " Vengeance Demon Hunter":0, " Fury Warrior":0,          " Brewmaster Monk":0,
               " Preservation Evoker":0,    " Devastation Evoker":0,   " Augmentation Evoker":0, }

# todo:    create cleaa list objects to better handle paralle arrays 
 
# create an array of dictionaries for histogram data
# copy each (so we don't end up with an array of references) class_list dictionary for each histo bar
histo_buckets = [class_list.copy()  for x in range(HISTO_BAR_COUNT)]

player_current=0 # init current player counter so we will know when to stop
page_count=1 # So we can request the right page of data from blizz web site, since we have to do it a page at a time.


# Read in a page and loop through all entries on the page and update counts
while player_current <  PLAYER_MAX:
    page = requests.get('https://worldofwarcraft.com/en-us/game/pvp/leaderboards/3v3?page=' + str(page_count)) # slurp page from internet
    tree = html.fromstring(page.content)  # 

    # extract player name, realm and charater class (stored in level field)
    players = tree.xpath('//div[@class="Character-name"]/text()')
    realms = tree.xpath('//div[@class="Character-realm"]/text()')
    player_class = tree.xpath('//div[@class="Character-level"]/text()')   # How does this  extract the actual name, and not also the level number?

    # did we get data?  If not skip. 
    # CODE - need to check for infinite empty pages.  What if we never get xpath data?)
    if(len(players) == 0):
        break
    # for each element of data on this page process it.
    for i in range(0, len(players)):
        if player_current <  PLAYER_MAX:
            player_current += 1

            # Clean up realm names for URL (need to deal with unicode(?) and special charaters
            safe_realm = realms[i].replace("'", "")
            safe_realm = safe_realm.replace(" ", "")
            # Printing unicode chars can cause exception on console

            if(DEBUG_OUT):
                try:
                    print(player_current, players[i], safe_realm, '[' + player_class[i] + ']', file=sys.stderr)
                except Exception as e:
                    oops = e
            class_list[player_class[i]] += 1
            # inc appropriate histogram bucket
            histo_buckets[int((player_current-1)/HISTO_WIDTH)][player_class[i]] += 1

    page_count += 1

if(DEBUG_OUT):
    print("player count", player_current)

# Sort by counts and print highest to lowest
for class_item in sorted(class_list.keys(), key=lambda class_str: class_list[class_str], reverse=True):
    if(class_list[class_item] > 0):
        print(class_list[class_item], "\t", class_item)

# Dump histogram data
# creat list of top n classes
histo_top_classes=[] 
for class_item in sorted(class_list.keys(), key=lambda class_str: class_list[class_str], reverse=True):
    if(len(histo_top_classes) < HISTO_TOP_X):
        histo_top_classes.append(class_item) 

# header (may need to sort to ensure each dictionary is ordered the same,  atm each run has differnt order, but same for each dictionary in any run)
print("Rank,", end='')
# for histo_item in histo_buckets[0]:
for histo_item in histo_top_classes:
    print(histo_item, ',', end='')
print()

# Print actual histogram data
# Hist range is the ending rank of the current hist bucket range.    0-20,  21,40
histo_range = HISTO_WIDTH
# for each dictionary in the arry process that batch of counts 
for histo_bar in histo_buckets:
    print(histo_range-HISTO_WIDTH+1, " ", histo_range, ',', end='')
    for histo_item in histo_top_classes:
        print(histo_bar[histo_item],  ',', end='')
    print() # end of line
    histo_range += HISTO_WIDTH  # go to the next histogram range
 


