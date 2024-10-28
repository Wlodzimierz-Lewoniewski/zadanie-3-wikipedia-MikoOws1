import re
import requests

def pobierz_pierwsze_dwa_art(nazwa_kat):
    url_kat = f'https://pl.wikipedia.org/wiki/Kategoria:{nazwa_kat.replace(" ", "_")}'
    odp = requests.get(url_kat)
    zaw_html = odp.text

    wzorzec = r'<div class="mw-category-group">.*?<ul>(.*?)</ul>.*?</div>'
    dopas = re.findall(wzorzec, zaw_html, re.DOTALL)

    arty = []
    for dop in dopas:
        linki = re.findall(r'<li><a href="(/wiki/[^"]+)" title="([^"]+)">', dop)
        for href, tyt in linki:
            url_art = 'https://pl.wikipedia.org' + href
            arty.append({'tytul': tyt, 'url': url_art})
            if len(arty) >= 2:
                return arty
    return arty

def pobierz_div_zaw(zaw_html):
    wzorzec = r'<div id="mw-content-text".*?>(.*?)<div id="catlinks"'
    dopas = re.search(wzorzec, zaw_html, re.DOTALL)
    if dopas:
        return dopas.group(1)
    return ''

def wyciagnij_linki_wew(zaw_html, limit=5):
    zaw = pobierz_div_zaw(zaw_html)
    wzorzec = r'<a[^>]*href="/wiki/([^":#]+)"[^>]*title="([^"]+)"[^>]*>'
    linki = re.findall(wzorzec, zaw)
    linki_wew = []
    for href, tyt in linki:
        linki_wew.append(tyt)
        if len(linki_wew) >= limit:
            break
    return linki_wew

def wyciagnij_url_obr(zaw_html, limit=3):
    zaw = pobierz_div_zaw(zaw_html)
    wzorzec = r'<img[^>]*src="([^"]+)"[^>]*>'
    obrazy = re.findall(wzorzec, zaw)
    url_obr = []
    for src in obrazy:
        if src.startswith('//'):
            url_obr.append(src)
        elif src.startswith('/'):
            url_obr.append('https://pl.wikipedia.org' + src)
        else:
            url_obr.append(src)
        if len(url_obr) >= limit:
            break
    return url_obr

def wyciagnij_zew_zrodla(zaw_html, limit=3):
    wzorzec_przypisy = r'<ol class="references">(.*?)</ol>'
    przypisy = re.findall(wzorzec_przypisy, zaw_html, re.DOTALL)
    zrodla = []
    if przypisy:
        linki = re.findall(r'<a[^>]*href="(http[^"]+)"[^>]*>', przypisy[0])
        for href in linki:
            zrodla.append(href)
            if len(zrodla) >= limit:
                break
    return zrodla

def wyciagnij_kat(zaw_html, limit=3):
    wzorzec = r'<div id="catlinks".*?<ul>(.*?)</ul>.*?</div>'
    dopas = re.findall(wzorzec, zaw_html, re.DOTALL)
    kat = []
    if dopas:
        linki = re.findall(r'<a [^>]*title="Kategoria:([^"]+)"[^>]*>', dopas[0])
        for kategoria in linki:
            kat.append(kategoria)
            if len(kat) >= limit:
                break
    return kat

def przetworz_art(arty):
    for art in arty:
        odp = requests.get(art['url'])
        zaw_html = odp.text

        linki_wew = wyciagnij_linki_wew(zaw_html)
        url_obr = wyciagnij_url_obr(zaw_html)
        zew_zrodla = wyciagnij_zew_zrodla(zaw_html)
        kat = wyciagnij_kat(zaw_html)

        if linki_wew:
            print(' | '.join(linki_wew))
        else:
            print()
        if url_obr:
            print(' | '.join(url_obr))
        else:
            print()
        if zew_zrodla:
            print(' | '.join(zew_zrodla))
        else:
            print()
        if kat:
            print(' | '.join(kat))
        else:
            print()

if __name__ == "__main__":
    nazwa_kat = input()
    arty = pobierz_pierwsze_dwa_art(nazwa_kat)
    przetworz_art(arty)
