import requests
from bs4 import BeautifulSoup

def pobierz_pierwsze_dwa_artykuly(nazwa_kategorii):
    url_kategorii = f'https://pl.wikipedia.org/wiki/Kategoria:{nazwa_kategorii.replace(" ", "_")}'
    odpowiedz = requests.get(url_kategorii)
    soup = BeautifulSoup(odpowiedz.content, 'html.parser')
    mw_strony = soup.find('div', {'id': 'mw-pages'})
    artykuly = []
    if not mw_strony:
        return artykuly
    for ul in mw_strony.find_all('ul'):
        for li in ul.find_all('li'):
            a_tag = li.find('a', href=True)
            if a_tag:
                tytul_artykulu = a_tag.get('title')
                url_artykulu = 'https://pl.wikipedia.org' + a_tag.get('href')
                artykuly.append({'tytul': tytul_artykulu, 'url': url_artykulu})
                if len(artykuly) >= 2:
                    return artykuly
    return artykuly

def wyciagnij_linki_wewnetrzne(soup, limit=5):
    linki = []
    div_tresci = soup.find('div', {'id': 'mw-content-text'})
    if not div_tresci:
        return linki
    for a_tag in div_tresci.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/wiki/') and ':' not in href[6:]:
            tytul_linku = a_tag.get('title')
            if tytul_linku:
                linki.append(tytul_linku.strip())
                if len(linki) >= limit:
                    break
    linki = list(set(linki))  
    linki.sort()  
    return linki

def wyciagnij_url_obrazkow(soup, limit=3):
    obrazki = []
    div_tresci = soup.find('div', {'id': 'mw-content-text'})
    if not div_tresci:
        return obrazki
    for img_tag in div_tresci.find_all('img'):
        img_src = img_tag.get('src')
        if img_src:
            if img_src.startswith('//'):
                img_src = img_src
            elif img_src.startswith('/'):
                img_src = 'https://pl.wikipedia.org' + img_src
            obrazki.append(img_src.strip())
            if len(obrazki) >= limit:
                break
    obrazki = list(set(obrazki)) 
    obrazki.sort() 
    return obrazki

def wyciagnij_zrodla_zewnetrzne(soup, limit=3):
    zrodla = []
    przypisy = soup.find('ol', {'class': 'references'})
    if not przypisy:
        return zrodla
    for li in przypisy.find_all('li'):
        for a_tag in li.find_all('a', href=True):
            href = a_tag['href'].replace("&amp;", "&")
            if href.startswith('http'):
                zrodla.append(href.strip())
                if len(zrodla) >= limit:
                    break
        if len(zrodla) >= limit:
            break
    zrodla = list(set(zrodla))  
    zrodla.sort()  
    return zrodla

def wyciagnij_kategorie(soup, limit=3):
    kategorie = []
    div_kategorii = soup.find('div', {'id': 'catlinks'})
    if not div_kategorii:
        return kategorie
    for a_tag in div_kategorii.find_all('a'):
        nazwa_kategorii = a_tag.get_text()
        if nazwa_kategorii != 'Kategorie':
            kategorie.append(nazwa_kategorii.strip())
            if len(kategorie) >= limit:
                break
    kategorie = list(set(kategorie))  
    kategorie.sort()  
    return kategorie

def przetworz_artykuly(artykuly):
    for artykul in artykuly:
        odpowiedz = requests.get(artykul['url'])
        soup = BeautifulSoup(odpowiedz.content, 'html.parser')
        linki_wewnetrzne = wyciagnij_linki_wewnetrzne(soup)
        url_obrazkow = wyciagnij_url_obrazkow(soup)
        zrodla_zewnetrzne = wyciagnij_zrodla_zewnetrzne(soup)
        kategorie = wyciagnij_kategorie(soup)
        if linki_wewnetrzne:
            print(' | '.join(linki_wewnetrzne))
        else:
            print()
        if url_obrazkow:
            print(' | '.join(url_obrazkow))
        else:
            print()
        if zrodla_zewnetrzne:
            print(' | '.join(zrodla_zewnetrzne))
        else:
            print()
        if kategorie:
            print(' | '.join(kategorie))
        else:
            print()

if __name__ == "__main__":
    nazwa_kategorii = input()
    artykuly = pobierz_pierwsze_dwa_artykuly(nazwa_kategorii)
    przetworz_artykuly(artykuly)
