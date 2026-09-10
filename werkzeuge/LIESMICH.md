# Werkzeuge

## Podcast-Folgen aktualisieren

Die Podcast-Seite **`podcast.html`** listet alle Folgen von „Menschen mit
Wirkung" zum Aufklappen. Die Seite ist statisch – neue Folgen erscheinen
also **nicht von selbst**, wenn du sie bei Podigee veröffentlichst.

> Seit dem 10.09.2026 pflegt das Skript `podcast.html` (vorher `index.html`,
> wo der Podcast früher auf der Startseite stand).

### Wenn eine neue Folge online ist

Terminal öffnen und diese Befehle eingeben:

```bash
cd ~/Desktop/COWORK/Impact4Entrepreneurship
git pull
python3 werkzeuge/podcast-aktualisieren.py
```

Das Skript holt die Folgen vom Podigee-Feed und schreibt drei Dinge neu:
die **Folgenliste**, das **JavaScript des Abspielers** und die **Anzahl der
Folgen** im Einleitungstext. Danach veröffentlichen:

```bash
git add -A && git commit -m "Podcast: neue Folge ergänzt" && git push
```

Nach ein bis zwei Minuten ist es live unter
https://impact4entrepreneurship.de/podcast.html

### Was das Skript nicht anfasst

Überschrift, Einleitung und Gestaltung der Seite stehen fest in
`podcast.html`. Das Skript ersetzt nur, was zwischen diesen Markern steht:

| Marker | Inhalt |
|---|---|
| `<!-- PODCAST -->` … `<!-- /PODCAST -->` | die Folgenliste |
| `/* PODCAST-CSS */` … `/* /PODCAST-CSS */` | das Aussehen des Abspielers |
| `<!-- PODCAST-JS -->` … `<!-- /PODCAST-JS -->` | der Abspieler selbst |

**Diese sechs Marker müssen stehen bleiben.** Gehen sie verloren – etwa beim
Umbau der Seite –, findet das Skript seinen Platz nicht mehr. Genau das ist
im Sommer 2026 zweimal passiert: Danach fehlten Abspieler und JavaScript,
und die Folgen mussten von Hand nachgetragen werden.

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
