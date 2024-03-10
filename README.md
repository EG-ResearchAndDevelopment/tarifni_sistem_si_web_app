# TarifniSistem
Repozitorij izračunain simulacije novega tarifnega sistema.

Trenutni repozitorij omogoča, da si posameznih izračuna ceno po novem tarifnem sistemu, poleg tega pa analizira, kako na ceno vpliva postavitev sončne elektrarne ali toplotne črpalke. Glavna ideja je, da se naredi primerjava med novim in starim omrežninskim sistemom. Uporabnik vpiše svoje podatke in si izračuna, kateri tarifni sistem je za njega bolj ugoden.

## Lokacija spletne aplikacije

Aplikacija je dostopna na spletnem naslovu: [Tarifni sistem](https://tarifni-sistem-simulator.azurewebsites.net/80)

## Navodila za uporabo

1. Uporabnik naj si na [MojElektro](https://mojelektro.si/login) naloži 15 minutne podatke o porabi.
2. Uporabnik lahko naloži tudi 15 minutne podatke v drugi obliki, vendar pa je potrebno imeti imena stolpcev, ki so prikazana v točki _POMOČ_.
3. Izpolni ostale podatke o odjemalcu.
4. Uporabniku se izpiše/izriše, kakšna cena bi bila v novem tarifnem sistemu in kakšna je v obstoječem tarifnem sistemu.

## Navodila za namestitev

1. Namestitev repozitorija:
```
git clone
```

2. Namestitev knjižnic:
```
pip install -r requirements.txt
```

3. Poženite datoteko app.py:
```
python app.py
```

## Opis datotek


## Avtorji

Delo je bilo podprto s strani podjetja [Elektro Gorenska](https://www.elektro-gorenjska.si/).

Avtorji projekta:
- [Blaž Dobravec](https://github.com/blazdob)
- [Tijaš-Tugo Štrbenc](https://github.com/TtijasS)
- [Matej Oblak](https://github.com/MatejGitOblak)
- [Bine Flajnik](https://github.com/Bine-f)

## Opozorilo!

Informacija o ceni po novem tarifnem sistemu je izključno informativne narave ter ne predstavlja pravno zavezujočega dokumenta ali izjave družbe Elektro Gorenjska, d. d.. Na podlagi te informacije ne nastanejo nikakršne obveznosti ali pravice, niti je ni mogoče uporabiti v katerem koli postopku uveljavljanja ali dokazovanja morebitnih pravic ali zahtevkov. 
Elektro Gorenjska, d. d. ne jamči ali odgovarja za vsebino, pravilnost ali točnost informacije. Uporabnik uporablja prejeto informacijo na lastno odgovornost in je odgovornost družbe Elektro Gorenjska, d. d. za kakršno koli neposredno ali posredno škodo, stroške ali neprijetnosti, ki bi lahko nastale uporabniku zaradi uporabe te informacije, v celoti izključena.
 
Dodatne informacije lahko pridobite na blaz.dobravec@elektro-gorenjska.si.





