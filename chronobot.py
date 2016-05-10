# -*- coding: utf-8 -*-

import requests
import urllib
from bs4 import BeautifulSoup


def add_entry(name_given, event_given, year_given, month_given, day_given):
    #name_given = 'Fred_Kaplan'
    #event_given = """* [[1955]] / [[Japon]]. [[Nicolas Bouvier]] s'arrête pendant un an au [[Japon]] à son retour de voyage et travail comme journaliste indépendant. Il y retournera de 1964 à 1966 et en 1970 [http://letemps.archives.world/page/GDL_1961_03_11/17/nicolas%20bouvier] | [http://letemps.archives.world/page/JDG_1994_09_07/25/nicolas%20bouvier] | [http://letemps.archives.world/page/GDL_1967_01_31/10/nicolas%20bouvier]"""
    #year_given = 2994
    #month_given = None
    #day_given = None

    name = name_given.replace('_', ' ') #normalement, pas utile

    tuple = dateToPage(year_given, month_given, day_given)
    page = tuple[0]
    type_de_page = tuple[1]
    print(page)
    
    createPageIfNotExists(year_given, month_given, day_given, type_de_page)
    
    if type_de_page == 3:
        addDayToMonth(year_given, month_given, day_given)

    req3 = '?format=json&action=query&prop=revisions&rvprop=content|timestamp&titles=' + page
    r = requests.post(baseUrl + 'api.php' + req3)

    for page2 in r.json()['query']['pages']:
        for rev in r.json()['query']['pages'][page2]['revisions']:
            content = rev['*']

            x = content.find('=== [[' + name + ']] ===')

            if (x != -1):
                y = content.find('===', x + 1)
                pos = y + 3

                z = content[:pos] + '\n' + event_given + content[pos:]

            else:
                if type_de_page == 3:
                    z = content + '\n\n' + '=== [[{0}]] ===\n'.format(name) + event_given
                elif type_de_page == 2:
                    ins = content.find('== Jours du mois ==')
                    z = content[:ins-1] + '\n=== [[{0}]] ===\n'.format(name) + event_given + '\n' + content[ins-1:]
                elif type_de_page == 1:
                    ins = content.find("== Mois de l'année ==")
                    z = content[:ins-1] + '\n=== [[{0}]] ===\n'.format(name) + event_given + '\n' + content[ins-1:]

                print(z)


            headers = {'content-type':'application/x-www-form-urlencoded'}
            payload = {'action': 'edit', 'assert': 'user', 'format': 'json', 'text': z, 'summary': summary,
                       'title': page, 'token': edit_token}
            r4 = requests.post(baseurl + 'api.php', headers = headers, data = payload, cookies = edit_cookie)
    
    
    return
    
def addDayToMonth(year_given, month_given, day_given):
    pageMonth = dateToPage(year_given, month_given, None)[0]
    pageDay = dateToPage(year_given, month_given, day_given)[0]
    req3 = '?format=json&action=query&prop=revisions&rvprop=content|timestamp&titles=' + pageMonth
    r = requests.post(baseUrl + 'api.php' + req3)

    for page2 in r.json()['query']['pages']:
        for rev in r.json()['query']['pages'][page2]['revisions']:
            content = rev['*']
            if not pageDay in content:
                content += "\n* [[" + pageDay + "|" + str(day_given) + " " + months[month_given-1] + "]]"
                
                headers = {'content-type':'application/x-www-form-urlencoded'}
                payload = {'action': 'edit', 'assert': 'user', 'format': 'json', 'text': content, 'summary': summary,
                           'title': pageMonth, 'token': edit_token}
                r4 = requests.post(baseurl + 'api.php', headers = headers, data = payload, cookies = edit_cookie)
    
def dateToPage(year_given, month_given, day_given): #Retourne un tuple (page, type_de_page)
    if day_given == None and month_given == None:
        type_de_page = 1
        page = str(year_given)
    elif day_given == None:
        type_de_page = 2
        month = months[month_given - 1]

        page = month + '_' + str(year_given)
    else:
        type_de_page = 3
        month = months[month_given-1]

        page = str(day_given) + '_' + month + '_' + str(year_given)
        
    return (page, type_de_page)

def createPageIfNotExists(year_given, month_given, day_given, type_de_page):
    page = dateToPage(year_given, month_given, day_given)
    if not page.replace("_", " ") in pagesName :
        print("Page " + page + " created")
        content = getTemplate(year_given, month_given, day_given, type_de_page)
        headers={'content-type':'application/x-www-form-urlencoded'}
        payload={'action':'edit','assert':'user','format':'json','text':content,'summary':summary,'title':page,'token':edit_token}
        r4=requests.post(baseurl+'api.php',headers=headers,data=payload,cookies=edit_cookie)
        pagesName.append(page)
        
        if type_de_page == 2:
            createPageIfNotExists(year_given, None, None, 1)
        elif type_de_page == 3:
            createPageIfNotExists(year_given, month_given, None, 2)

def getTemplate(year_given, month_given, day_given, type_de_page):
    if type_de_page == 1: #année
    
        template = template_year1 + str(year_given) + template_year2
        for month in months:
            template += "\n==== [[" + month + " " + str(year_given) + "|" + month + "]] ===="
    elif type_de_page == 2: #mois
    
        template = template_month1
        if months[month_given-1][0] == "A" or months[month_given-1][0] == "O":
            template += "' "
        else :
            template += "e "
        template += months[month_given-1] + " [[" + str(year_given) + "]]" + template_month2
    
    else :
        
        template = template_day + str(day_given) + " [[" + months[month_given-1] + " " + str(year_given) + "|" + months[month_given-1] + "]] [[" + str(year_given) + "]]==\n"
            
    return template

def main():
    baseUrl='http://wikipast.world/wiki/'

    blackList = ['Accueil', 'Hypermot', 'ImageBot']
    whiteList= [] #['Herbert George Wells'] #juste pour tester avec certaines pages

    done = False
    lastEntry = None
    while not done:
        if lastEntry == None:
            pageList=requests.post(baseUrl + "api.php?action=query&list=allpages&aplimit=500&format=xml")
        else:
            pageList=requests.post(baseUrl + "api.php?action=query&list=allpages&aplimit=500&format=xml&apfrom=" + lastEntry)
            
        pageListSoup=BeautifulSoup(pageList.text, "html.parser")
        for primitive in pageListSoup.findAll("p"):
            name = primitive['title'].replace("\u2019", "'").replace("\u0153", "oe").replace("\u2026", "...").replace("\u201c", '"').replace("\u201d", '"')
            if name not in pagesName:
                pagesName.append(name)
        lastEntry = pagesName[-1]
        
        if len(pageListSoup.findAll("p")) < 500:
            done = True
     
    #Reset date pages
    for pageName in pagesName:
        tuple = ourTitleDate(pageName)
        if tuple[0]:
            """content = getTemplate(tuple[2], tuple[3], tuple[4], pageName, tuple[1])
            headers={'content-type':'application/x-www-form-urlencoded'}
            payload={'action':'edit','assert':'user','format':'json','text':content,'summary':summary,'title':pageName,'token':edit_token}
            r4=requests.post(baseurl+'api.php',headers=headers,data=payload,cookies=edit_cookie)
            print("Reset " + pageName)"""
            

    #Parsing
    count = 0
    for pageName in pagesName:
        #print(pageName)
        if not pageName in blackList and pageName in whiteList and not isTitleDate(pageName):
            print("#####" + pageName + "#####")
            result=requests.post(baseUrl + 'api.php?action=query&titles='+pageName+'&export&exportnowrap')
            pageSoup=BeautifulSoup(result.text, "html.parser")
            for primitive in pageSoup.findAll("text"):
                if primitive.string != None:
                    currentStr = primitive.string.replace("\u2019", "'").replace("\u0153", "oe").replace("\u2026", "...").replace("\u201c", '"').replace("\u201d", '"')
                    currentStr = str(currentStr)
                    for event in currentStr.split("\n"):
                        #print(event)

                        year = 0
                        month = 0
                        day = 0

                        step = 0
                        charCounter = 0
                        done = False
                        valid = False

                        while not done:
                            found = False
                            while len(event) > charCounter and not found:
                                if event[charCounter] != " ":
                                    char =  event[charCounter]
                                    found = True
                                charCounter += 1

                            if not found:
                                done = True
                            elif char == "*":
                                valid = True
                            elif char == "[":
                                valid = True # une date valide doit être précédée de * ou [
                            elif valid and isAInt(char) :
                                if step == 0:
                                    year = int(char) + 10 * year
                                elif step == 1:
                                    month = int(char) + 10 * month
                                elif step == 2:
                                    day = int(char) + 10 * day
                                else :
                                    raise Exception("Too many numbers here !")
                            elif valid and char == ".":
                                step += 1;
                            elif char == "|": #Thanks Marie Curie
                                step = 0
                                year = 0
                            else:
                                done = True

                        if len(str(day)) == 4: #merci Pétain, il faut inverser année et jour
                            year, day = day, year

                        month = month if month > 0 else None
                        day = day if day > 0 else None

                        #TODO : ajouter check validité

                        if year > 0:
                            add_entry(pageName, event, year, month, day)
                            print("Add entry for " + str(year) + "." + str(month) + "." + str(day) + " : " + pageName + "\n")
            print("")
            print("")

            count += 1
            if count > 0: #si jamais vous voulez pas tout parser
                break
                #pass

def isAInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def isTitleDate(dateString):
    if "." in dateString: #format : 1994.2.18, ou 1994.2
        list = dateString.split(".")
        return isAInt(list[0]) and len(list) <= 3
    elif isAInt(dateString) and len(dateString) == 4: #format : 1994
        return True
    else: #format : 18 Février 1994, ou Février 1994
        list = dateString.split(" ")
        if len(list) == 3 : #format : 18 Février 1994
            return isAInt(list[0]) and list[1] in months and isAInt(list[2])
        elif len(list) == 2 : #format : Février 1994
            return list[0] in months and isAInt(list[1])
        else :
            return False
            
def ourTitleDate(dateString): #retourne un tuple (is, type_de_page, year, month, day)
    if "." in dateString: #format : 1994.2.18, ou 1994.2
        return (False, 0, None, None, None)
    elif isAInt(dateString) and len(dateString) == 4 and int(dateString) < 2000: #format : 1994
        return (True, 1, int(dateString), None, None)
    else: #format : 18 Février 1994, ou Février 1994
        list = dateString.split(" ")
        if len(list) == 3 : #format : 18 Février 1994
            liste = [i for i,x in enumerate(months) if x == list[1]]
            if len(liste) > 0:
                return (isAInt(list[0]) and list[1] in months and isAInt(list[2]), 3, int(list[2]), liste[0]+1, int(list[0]))
            else:
                return (False, 0, None, None, None)
        elif len(list) == 2 : #format : Février 1994
            liste = [i for i,x in enumerate(months) if x == list[0]]
            if len(liste) > 0:
                return (list[0] in months and isAInt(list[1]), 2, int(list[1]), liste[0]+1, None)
            else:
                return (False, 0, None, None, None)
        else :
            return (False, 0, None, None, None)

            
baseUrl = 'http://wikipast.world/wiki/'
baseurl = 'http://wikipast.world/wiki/'

months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

template_year1 = "== Événements durant l'année "
template_year2 = " ==\n== Mois de l'année =="
template_month1 = "== Evénements durant le mois d" 
template_month2 = " ==\n== Jours du mois =="
template_day = "== Evénements du " 

user = 'ChronoBot'
passw = urllib.parse.quote('yolobotHUM369')

login_params = '?action=login&lgname=%s&lgpassword=%s&format=json' % (user, passw)

# Login request
r1 = requests.post(baseurl + 'api.php' + login_params)
login_token = r1.json()['login']['token']

# login confirm
login_params2 = login_params + '&lgtoken=%s' % login_token
r2 = requests.post(baseurl + 'api.php' + login_params2, cookies=r1.cookies)

# get edit token2
params3 = '?format=json&action=query&meta=tokens&continue='
r3 = requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
edit_token = r3.json()['query']['tokens']['csrftoken']

edit_cookie = r2.cookies.copy()
edit_cookie.update(r3.cookies)
summary = 'Maj by ChronoBot'
pagesName = []
main()