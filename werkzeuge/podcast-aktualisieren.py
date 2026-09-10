#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traegt die Folgen des Podcasts "Menschen mit Wirkung" in podcast.html ein.

Holt den Podigee-Feed und schreibt daraus die aufklappbare Folgenliste.
Setzt beim ersten Lauf ausserdem das noetige CSS und JavaScript ein.
Alle drei Bloecke sind durch Marker begrenzt und werden bei jedem
weiteren Lauf nur ersetzt - Gestaltungsaenderungen am CSS bleiben also
erhalten, solange die Marker stehen bleiben.

Aufruf aus dem Projektordner:
    python3 werkzeuge/podcast-aktualisieren.py

Nur schauen, nichts schreiben:
    python3 werkzeuge/podcast-aktualisieren.py --probe
"""

import html
import re
import shutil
import sys
import urllib.request
from pathlib import Path

FEED = "https://impact4entrepreneurship.podigee.io/feed/mp3"
SEITE = "https://impact4entrepreneurship.podigee.io/"
ZIEL = Path(__file__).resolve().parent.parent / "podcast.html"

# Nachtraege: Text, der in den Podigee-Shownotes fehlt, aber auf der Webseite
# stehen soll. Aufbau:  "Anfang des Folgentitels": [(suchen, ersetzen), ...]
# Normalerweise leer - besser direkt bei Podigee pflegen, dann stimmt es auch
# bei Spotify und Apple. Steht der Text spaeter im Feed, Eintrag hier loeschen,
# sonst erscheint er doppelt.
NACHTRAEGE = {}

M_HTML = ("<!-- PODCAST -->", "<!-- /PODCAST -->")
M_CSS = ("/* PODCAST-CSS */", "/* /PODCAST-CSS */")
M_JS = ("<!-- PODCAST-JS -->", "<!-- /PODCAST-JS -->")

MONATE = {"Jan": "Januar", "Feb": "Februar", "Mar": "März", "Apr": "April",
          "May": "Mai", "Jun": "Juni", "Jul": "Juli", "Aug": "August",
          "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "Dezember"}

# Nur der Abspieler. Das uebrige Aussehen der Folgenliste steht fest in podcast.html.
CSS = """/* Abspieler */
.spieler {
    display: flex; align-items: center; gap: 15px;
    background: var(--flieder-hell); border-radius: 100px; padding: 10px 20px 10px 10px;
  }
.spieler-knopf {
    width: 42px; height: 42px; border-radius: 50%; border: none;
    background: var(--lila); color: #fff; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex: none; transition: 0.2s ease; font-size: 15px; line-height: 1;
  }
.spieler-knopf:hover { background: var(--tief); transform: scale(1.06); }
.spieler-knopf:focus-visible { outline: 2px solid var(--tief); outline-offset: 3px; }
.spieler-balken {
    flex: 1; height: 6px; background: rgba(91, 21, 109, 0.16);
    border-radius: 100px; cursor: pointer; position: relative; min-width: 60px;
  }
.spieler-fuellung {
    height: 100%; width: 0; background: var(--lila);
    border-radius: 100px; transition: width 0.1s linear;
  }
.spieler-balken:focus-visible { outline: 2px solid var(--lila); outline-offset: 4px; }
.spieler-zeit {
    font-size: 0.84rem; color: var(--lila); font-weight: 600;
    font-variant-numeric: tabular-nums; white-space: nowrap;
  }
.spieler.laedt .spieler-knopf { opacity: 0.55; cursor: progress; }"""

JS = """<script>
  /* Podcast-Abspieler: ein Audio-Element fuer alle Folgen, laedt erst auf Klick */
  (function () {
    var lauf = null;
    var au = new Audio();
    au.preload = 'none';

    function zeit(s) {
      s = Math.floor(s || 0);
      var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
      return h ? h + ':' + String(m).padStart(2, '0') + ':' + String(r).padStart(2, '0')
               : m + ':' + String(r).padStart(2, '0');
    }
    function anzeige(sp, akt, ges) {
      sp.querySelector('.spieler-fuellung').style.width = ges ? (akt / ges * 100) + '%' : '0%';
      sp.querySelector('.spieler-zeit').innerHTML = zeit(akt) + '&nbsp;/&nbsp;' + zeit(ges);
      sp.querySelector('.spieler-balken').setAttribute('aria-valuenow', Math.floor(akt));
    }
    function zurueck(sp) {
      if (!sp) return;
      sp.classList.remove('laedt');
      sp.querySelector('.spieler-knopf').innerHTML = '&#9654;';
      anzeige(sp, 0, +sp.dataset.dauer);
    }
    function starte(sp) {
      if (lauf && lauf !== sp) zurueck(lauf);
      if (lauf === sp && !au.paused) {
        au.pause();
        sp.querySelector('.spieler-knopf').innerHTML = '&#9654;';
        return;
      }
      if (lauf !== sp) {
        lauf = sp;
        sp.classList.add('laedt');
        au.src = sp.dataset.src;
      }
      au.play().then(function () {
        sp.classList.remove('laedt');
        sp.querySelector('.spieler-knopf').innerHTML = '&#10073;&#10073;';
      }).catch(function () {
        sp.classList.remove('laedt');
        sp.querySelector('.spieler-zeit').textContent = 'Wiedergabe nicht möglich';
      });
    }

    au.addEventListener('timeupdate', function () {
      if (lauf) anzeige(lauf, au.currentTime, au.duration || +lauf.dataset.dauer);
    });
    au.addEventListener('ended', function () { zurueck(lauf); lauf = null; });

    document.querySelectorAll('.spieler').forEach(function (sp) {
      sp.querySelector('.spieler-knopf').addEventListener('click', function () { starte(sp); });

      var balken = sp.querySelector('.spieler-balken');
      function springe(anteil) {
        var ges = (lauf === sp && au.duration) ? au.duration : +sp.dataset.dauer;
        if (lauf !== sp) starte(sp);
        au.currentTime = Math.max(0, Math.min(ges, anteil * ges));
        anzeige(sp, au.currentTime, ges);
      }
      balken.addEventListener('click', function (ev) {
        var r = balken.getBoundingClientRect();
        springe((ev.clientX - r.left) / r.width);
      });
      balken.addEventListener('keydown', function (ev) {
        var ges = +sp.dataset.dauer;
        if (ev.key === 'ArrowRight') { ev.preventDefault(); springe((au.currentTime + 15) / ges); }
        else if (ev.key === 'ArrowLeft') { ev.preventDefault(); springe((au.currentTime - 15) / ges); }
        else if (ev.key === ' ' || ev.key === 'Enter') { ev.preventDefault(); starte(sp); }
      });
    });

    /* Zuklappen stoppt die Wiedergabe */
    document.querySelectorAll('.folge').forEach(function (f) {
      f.addEventListener('toggle', function () {
        if (!f.open) {
          var sp = f.querySelector('.spieler');
          if (lauf === sp) { au.pause(); zurueck(sp); lauf = null; }
        }
      });
    });
  })();
</script>"""


def feld(muster, text, standard=""):
    treffer = re.search(muster, text, re.S)
    if not treffer:
        return standard
    return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", treffer.group(1))).strip()


def datum_de(roh):
    t = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", roh)
    return f"{int(t.group(1))}. {MONATE.get(t.group(2), t.group(2))} {t.group(3)}" if t else ""


def dauer_txt(sekunden):
    sekunden = int(sekunden or 0)
    st, rest = divmod(sekunden, 3600)
    mi, se = divmod(rest, 60)
    return f"{st}:{mi:02d}:{se:02d}" if st else f"{mi}:{se:02d}"


def hole_folgen():
    with urllib.request.urlopen(FEED, timeout=30) as antwort:
        xml = antwort.read().decode("utf-8", "replace")
    folgen = []
    for eintrag in re.findall(r"<item>(.*?)</item>", xml, re.S):
        mp3 = feld(r'<enclosure[^>]*url="([^"]+)"', eintrag)
        if not mp3:
            continue
        folgen.append({
            "titel": feld(r"<title>(.*?)</title>", eintrag),
            "datum": feld(r"<pubDate>(.*?)</pubDate>", eintrag),
            "dauer": feld(r"<itunes:duration>(.*?)</itunes:duration>", eintrag, "0"),
            "mp3": mp3,
            "text": re.sub(r"<[^>]+>", "", feld(r"<description>(.*?)</description>", eintrag)).strip(),
        })
    for f in folgen:
        for anfang, ersetzungen in NACHTRAEGE.items():
            if f["titel"].startswith(anfang):
                for suchen, ersetzen in ersetzungen:
                    f["text"] = f["text"].replace(suchen, ersetzen)
    return folgen


def verlinke(text):
    """Macht aus bereits HTML-maskiertem Text klickbare Links."""
    return re.sub(
        r"(https?://[^\s<]+?)([.,;:!?)]*)(?=\s|$)",
        r'<a href="\1" target="_blank" rel="noopener">\1</a>\2',
        text,
    )


def baue_html(folgen):
    karten = []
    for f in folgen:
        titel = html.escape(f["titel"], quote=True)
        absatz = "\n          ".join(
            f"<p>{verlinke(html.escape(teil.strip(), quote=True))}</p>"
            for teil in re.split(r"\n\s*\n|\n", f["text"]) if teil.strip()
        )
        sek = int(f["dauer"] or 0)
        karten.append(f"""      <details class="folge">
        <summary>
          <span class="datum">{html.escape(datum_de(f['datum']))}</span>
          <span class="name">{titel}</span>
          <span class="laenge">{dauer_txt(sek)}</span>
          <span class="zeichen" aria-hidden="true">+</span>
        </summary>
        <div class="inhalt">
          {absatz}
          <div class="spieler" data-src="{html.escape(f['mp3'], quote=True)}" data-dauer="{sek}">
            <button class="spieler-knopf" type="button" aria-label="Folge abspielen: {titel}">&#9654;</button>
            <div class="spieler-balken" role="slider" tabindex="0" aria-label="Position in der Folge"
                 aria-valuemin="0" aria-valuemax="{sek}" aria-valuenow="0"><div class="spieler-fuellung"></div></div>
            <span class="spieler-zeit">0:00&nbsp;/&nbsp;{dauer_txt(sek)}</span>
          </div>
        </div>
      </details>""")

    # Ueberschrift und Einleitung stehen fest in podcast.html - hier nur die Liste.
    return f"""{M_HTML[0]}
    <div class="folgen">
{chr(10).join(karten)}
    </div>
{M_HTML[1]}"""


def setze_block(text, marker, inhalt, anker, davor=True):
    """Ersetzt den Block zwischen den Markern oder fuegt ihn beim Anker ein."""
    start, ende = marker
    block = f"{start}\n{inhalt}\n{ende}" if not inhalt.startswith(start) else inhalt
    if start in text and ende in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(ende), lambda _: block, text, count=1, flags=re.S), "ersetzt"
    if anker not in text:
        sys.exit(f"ABBRUCH: Einfuegepunkt {anker!r} nicht gefunden.")
    neu = block + "\n\n" + anker if davor else anker + "\n\n" + block
    return text.replace(anker, neu, 1), "eingefuegt"


def main():
    nur_probe = "--probe" in sys.argv
    if not ZIEL.exists():
        sys.exit(f"ABBRUCH: {ZIEL} nicht gefunden.")

    print(f"Hole Feed: {FEED}")
    folgen = hole_folgen()
    if not folgen:
        sys.exit("ABBRUCH: Der Feed enthaelt keine Folgen mit Audiodatei.")
    print(f"  {len(folgen)} Folgen, neueste: {folgen[0]['titel'][:55]}")

    quelle = ZIEL.read_text(encoding="utf-8")
    neu = quelle
    schritte = []

    # 1) CSS vor dem Media-Query-Block bzw. vor dem Ende des <style>
    anker_css = ".folge audio{width:100%;max-width:520px;margin-top:8px;}"
    neu, was = setze_block(neu, M_CSS, CSS.rstrip(),
                           anker_css if anker_css in neu else "</style>", davor=False)
    schritte.append(f"CSS {was}")

    # 2) Folgenliste zwischen die Marker
    html_block = baue_html(folgen)
    neu, was = setze_block(neu, M_HTML, html_block, '    <div class="folgen">')
    schritte.append(f"Folgenliste {was} ({len(folgen)} Folgen)")

    # 3) JavaScript vor </body>
    neu, was = setze_block(neu, M_JS, JS, "</body>")
    schritte.append(f"JavaScript {was}")

    # 4) Anzahl der Folgen im Einleitungstext und in der Seitenbeschreibung
    anzahl_neu, treffer = re.subn(r"(?<=Alle )\d+(?= Folgen)", str(len(folgen)), neu)
    if treffer and anzahl_neu != neu:
        neu = anzahl_neu
        schritte.append(f"Anzahl der Folgen auf {len(folgen)} gesetzt ({treffer} Stellen)")

    if neu == quelle:
        print("Keine Aenderung noetig - podcast.html ist bereits aktuell.")
        return

    if nur_probe:
        print("PROBE, nichts geschrieben. Geplant:")
        for s in schritte:
            print("  -", s)
        return

    shutil.copy2(ZIEL, ZIEL.with_suffix(".html.sicherung"))
    ZIEL.write_text(neu, encoding="utf-8")
    for s in schritte:
        print("  ", s)
    print(f"\nGeschrieben. Sicherung: {ZIEL.with_suffix('.html.sicherung').name}")
    print("Nicht vergessen: git add -A && git commit && git push")


if __name__ == "__main__":
    main()
