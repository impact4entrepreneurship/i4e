# Werkzeuge

## Podcast-Folgen aktualisieren

Auf der Startseite gibt es den Abschnitt **„Menschen mit Wirkung"** mit allen
Podcast-Folgen zum Aufklappen. Die Seite ist statisch – neue Folgen erscheinen
also **nicht von selbst**, wenn du sie bei Podigee veröffentlichst.

### Wenn eine neue Folge online ist

Terminal öffnen und diese Befehle eingeben:

```bash
cd ~/Desktop/COWORK/Impact4Entrepreneurship
git pull
python3 werkzeuge/podcast-aktualisieren.py
```

Das Skript holt die Folgen vom Podigee-Feed und schreibt die Liste neu.
Danach veröffentlichen:

```bash
git add -A && git commit -m "Podcast: neue Folge ergänzt" && git push
```

Nach ein bis zwei Minuten ist es live unter
https://impact4entrepreneurship.github.io/i4e/

> **Das `git pull` am Anfang ist wichtig.** Wird an der Seite auch von anderer
> Stelle gearbeitet, ist der lokale Ordner sonst veraltet – und ein Push würde
> abgelehnt oder überschriebe neuere Arbeit.

### Erst nachschauen, nichts ändern

```bash
python3 werkzeuge/podcast-aktualisieren.py --probe
```

Zeigt, wie viele Folgen der Feed hat und was sich ändern würde.

### Was das Skript macht

Es lädt `https://impact4entrepreneurship.podigee.io/feed/mp3` und pflegt in
`index.html` drei Bereiche, jeweils zwischen Markern:

| Marker | Inhalt |
|---|---|
| `/* PODCAST-CSS */` … `/* /PODCAST-CSS */` | Gestaltung im `<style>`-Block |
| `<!-- PODCAST -->` … `<!-- /PODCAST -->` | die Folgenliste |
| `<!-- PODCAST-JS -->` … `<!-- /PODCAST-JS -->` | Abspieler-Steuerung |

Zusätzlich ergänzt es einmalig den Navigationspunkt „Podcast".
Vor jedem Schreiben legt es eine Sicherung als `index.html.sicherung` an
(die wird von Git ignoriert).

**Wichtig:** Die Marker nicht löschen – ohne sie findet das Skript die Stellen
nicht mehr.

### Wenn etwas schiefgeht

```bash
cp index.html.sicherung index.html     # Sicherung zurückspielen
git checkout index.html                # oder alles Unveröffentlichte verwerfen
```

### Gestaltung ändern

Das CSS steht zwischen den `PODCAST-CSS`-Markern in `index.html`. Ändere es
dort **nicht**, wenn du das Skript weiter nutzen willst – es wird bei jedem
Lauf überschrieben. Passe stattdessen den `CSS`-Block oben in
`podcast-aktualisieren.py` an. Dasselbe gilt für das JavaScript.

Verwendete Farbvariablen der Seite: `--lila-tief`, `--lila-dunkel`,
`--lila-akzent`, `--flieder`, `--flieder-hell`, `--grund`, `--weiss`,
`--text-sanft`.

### Warum ein eigener Abspieler

Der eingebettete Podigee-Player ist schwarz und lässt sich von außen nicht
umfärben – die Farbe steckt in den Podigee-Kontoeinstellungen. Im violetten
Layout wirkte er wie ein Fremdkörper. Der eigene Abspieler lädt dieselbe
getrackte Audiodatei von `audio.podigee-cdn.net`, die Abrufe zählt Podigee
also weiterhin mit.

Eigenschaften:

- Audio lädt erst beim Klick (`preload="none"`) – sonst zöge jeder
  Seitenaufruf bei 21 Folgen Dutzende Megabyte
- es spielt immer nur eine Folge; startet man eine zweite, wird die erste
  zurückgesetzt
- Zuklappen einer Folge stoppt die Wiedergabe
- bedienbar per Tastatur: Leertaste startet und pausiert, Pfeiltasten
  springen 15 Sekunden

### Offener Punkt

Das Podcast-Cover bei Podigee ist noch im alten I4E-Design (Anthrazit/Grün/
Türkis) und passt nicht zur violetten Seite. Es ist deshalb bewusst nicht
eingebunden. Bei Gelegenheit neu gestalten.
