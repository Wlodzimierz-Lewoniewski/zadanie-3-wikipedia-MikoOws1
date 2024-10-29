import re
import requests
import itertools

wzor_wpisy = r'<li[^>]*>.*<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*</li>'
szlink_wpis = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
pics_wpisy = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
linki_zew = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
kat_strony = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'

def zlacz_linie(lista):
    polaczone = ' | '.join(lista)
    print(polaczone)

def fragment_html(html_str: str) -> str:
    return html_str[html_str.find('<div id="mw-content-text"'):html_str.find('<div id="catlinks"')]

def przypisy_html(html_str: str) -> str:
    html_str = html_str[html_str.find('id="Przypisy"'):]
    html_str = html_str[:html_str.find('<div class="mw-heading')]
    return html_str

def html_kategorie(html_str: str) -> str:
    return html_str[html_str.find('<div id="catlinks"'):]

def szukaj_wzorce(wzorzec: str, tekst: str, flagi: int = 0, limit: int = 5) -> list:
    return [dopasowanie.groups() for dopasowanie in itertools.islice(re.finditer(wzorzec, tekst, flags=flagi), limit)]

def generuj_url(nazwa_kat: str) -> str:
    sformatowana_kat = nazwa_kat.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{sformatowana_kat}'

def uzyskaj_artykuly(nazwa_kat: str, limit: int = 3) -> list[tuple[str, str]]:
    adres_kategorii = generuj_url(nazwa_kat)
    odp = requests.get(adres_kategorii)
    html_str = odp.text
    return szukaj_wzorce(wzor_wpisy, html_str, limit=limit)

def uzyskaj_html_artykul(artykul_url: str) -> str:
    odp = requests.get("https://pl.wikipedia.org" + artykul_url)
    return odp.text

def znajdz_linki_w_artykule(html_tresc: str, limit: int = 5) -> list[tuple[str, str]]:
    tresc_glowna = fragment_html(html_tresc)
    return szukaj_wzorce(szlink_wpis, tresc_glowna, limit=limit)

def znajdz_obrazki(html_tresc: str, limit: int = 3) -> list:
    tresc_glowna = fragment_html(html_tresc)
    return szukaj_wzorce(pics_wpisy, tresc_glowna, limit=limit)

def znajdz_linki_zewnetrzne(html_tresc: str, limit: int = 3) -> list:
    sekcja_przypisy = przypisy_html(html_tresc)
    return szukaj_wzorce(linki_zew, sekcja_przypisy, limit=limit)

def znajdz_kategorie(html_tresc: str, limit: int = 3) -> list:
    sekcja_kat = html_kategorie(html_tresc)
    return szukaj_wzorce(kat_strony, sekcja_kat, limit=limit)

def glowna():
    kat_in = input().strip()
    artykuly = uzyskaj_artykuly(kat_in)
    for art_link, art_tytul in artykuly:
        tresc_artykul = uzyskaj_html_artykul(art_link)
        
        wew_linki = znajdz_linki_w_artykule(tresc_artykul)
        zlacz_linie([tytul for _, tytul in wew_linki])
        
        obrazy = znajdz_obrazki(tresc_artykul)
        zlacz_linie([url for url, in obrazy])
        
        zew_linki = znajdz_linki_zewnetrzne(tresc_artykul)
        zlacz_linie([url for url, in zew_linki])
        
        kategorie = znajdz_kategorie(tresc_artykul)
        zlacz_linie([nazwa.replace('Kategoria:', '') for _, nazwa in kategorie])
    
if __name__ == '__main__':
    glowna()
