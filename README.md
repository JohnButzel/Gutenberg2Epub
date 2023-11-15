# Gutenberg2Epub

Gutenberg2Epub ist eine Python-GUI-Anwendung, mit der man [Projekt Gutenberg-de](https://www.projekt-gutenberg.org) Bücher in das EPUB-E-Book-Format konvertieren kann. Die Anwendung besteht aus mehreren Modulen, die HTML-Inhalte scrapen, verarbeiten und EPUB-E-Books erstellen.

## Erste Schritte

1. Lade die Datei `Gutenberg2Epub.exe` aus dem [Releases](https://github.com/JohnButzel/gutenberg2epub/releases) Abschnitt herunter.
2. Führe die Datei `Gutenberg2Epub.exe` aus, um die GUI-Anwendung zu starten.

## Verwendung der GUI

1. Gib die Project Gutenberg URL in das bereitgestellte Textfeld ein.
2. Wähle das Ausgabeverzeichnis mit der "Durchsuchen"-Schaltfläche aus oder behalte das Standardverzeichnis bei.
3. Klicke auf die Schaltfläche "Buch laden", um den Konvertierungsprozess zu starten.
4. Eine Nachricht wird angezeigt, die auf die erfolgreiche Konvertierung des E-Books hinweist.

## Verwendung der Kommandozeilenschnittstelle (CLI)

Du kannst die Kommandozeilenschnittstelle verwenden, um das Konvertieren von Project Gutenberg-Inhalten durchzuführen. Hier sind die Schritte und Befehle, um dies zu tun:

### Schritte

1. **Öffnen einer Eingabeaufforderung oder eines Terminals**: Starte deine bevorzugte Eingabeaufforderung oder ein Terminal auf deinem Computer.

2. **Ausführen des Befehls**: Verwende den folgenden Befehl, um das Konvertieren zu starten:

### Basisbefehl:

```bash
python Gutenberg2Epub_cli.py <url>
```

### Befehl mit benutzerdefiniertem Ausgabeverzeichnis:

```bash
python Gutenberg2Epub_cli.py <url> -o <Verzeichnis>
```

Ersetze `<url>` durch die URL des Project Gutenberg-Inhalts, den du konvertieren möchtest.

Falls du ein benutzerdefiniertes Ausgabeverzeichnis festlegen möchtest, ersetze `<Verzeichnis>` durch den Pfad, wo das Buch gespeichert werden soll.

### Optionen

- `-o, --output <Verzeichnis>`: Mit dieser Option kannst du das Ausgabeverzeichnis für das konvertierte Buch festlegen. Wenn diese Option nicht angegeben wird, wird das Buch im aktuellen Arbeitsverzeichnis gespeichert.

- `--cover <Pfad zur Titelseitenbild>`: Mit dieser Option kannst du eine Titelseite festlegen, die dem Buch hinzugefügt wird.

- `--delete-cover`: Diese Option entfernt das Titelseitenbild aus der Indexseite, sofern es vorhanden ist.

### Beispielanwendung

Angenommen, du möchtest das Buch von der folgenden Project Gutenberg-URL konvertieren: `https://www.projekt-gutenberg.org/autor/buch/`, und du möchtest das konvertierte Buch im Verzeichnis `/home/dein_benutzername/bücher/` speichern. Du möchtest auch ein benutzerdefiniertes Titelbild hinzufügen und das vorhandene Titelbild aus dem Buch entfernen. Du würdest den folgenden Befehl verwenden:

```bash
python Gutenberg2Epub_cli.py https://www.projekt-gutenberg.org/autor/buch/ -o /home/dein_benutzername/bücher/ --cover /pfad/zum/cover.png --delete-cover
```

Die CLI ermöglicht es dir, das Konvertieren von Project Gutenberg-Büchern bequem über die Kommandozeile durchzuführen, und bietet die Flexibilität, Titelseitenbilder hinzuzufügen oder zu entfernen. Beachte, dass du Python auf deinem Computer installiert haben musst, um diesen Befehl auszuführen.
## Installation und Anforderungen

Falls du die ausführbare Datei nicht verwenden möchtest, besteht die Möglichkeit, die Python-Skripte zu verwenden. Zur Ausführung der Python-Skripte benötigst du die folgenden Abhängigkeiten:

- Python 3.x
- Requests-Bibliothek
- Beautiful Soup-Bibliothek
- EbookLib-Bibliothek
- wxPython-Bibliothek (für die GUI)

Du kannst diese Abhängigkeiten mit dem folgenden Befehl installieren:

```bash
pip install requests beautifulsoup4 ebooklib wxpython
```


## Module

### GUI (gui.py)

Das Modul für die grafische Benutzeroberfläche (GUI) ermöglicht es dir, interaktiv die URL und das Ausgabeverzeichnis für die Konvertierung einzugeben. Die GUI wurde mit der wxPython-Bibliothek erstellt.

### Gutenberg Scraper (gscraper.py)

Das Gutenberg Scraper-Modul ist dafür verantwortlich, den HTML-Inhalt von der angegebenen Project Gutenberg-URL abzurufen. Es erstellt ein temporäres Verzeichnis, um die abgerufenen HTML-Dateien und Ressourcen zu speichern.

### HTML zu EPUB Konverter (converter.py)

Das HTML zu EPUB Converter-Modul nimmt den abgerufenen HTML-Inhalt und die Ressourcen und konvertiert sie in ein EPUB-E-Book. Es extrahiert Metadaten, erstellt ein Inhaltsverzeichnis und generiert die EPUB-Datei.

### Kommandozeilenschnittstelle (Gutenberg2Epub_cli.py)

Das Modul für die Kommandozeilenschnittstelle bietet eine einfache Kommandozeilenschnittstelle, um den gesamten Konvertierungsprozess auszuführen. Es nimmt die URL als Argument und automatisiert den Abruf und Konvertierungsprozess.



## Lizenz

Dieses Projekt steht unter der CC BY-NC-Lizenz - siehe die Datei [LICENSE](LICENSE) für Details.
