# Gutenberg2Epub

Gutenberg2Epub ist eine Python-GUI-Anwendung, mit der man [Project Gutenberg-de](https://www.projekt-gutenberg.org) Bücher in das EPUB-E-Book-Format konvertieren kann. Die Anwendung besteht aus mehreren Modulen, die HTML-Inhalte scrapen, verarbeiten und EPUB-E-Books erstellen.

## Erste Schritte

1. Lade die Datei `Gutenberg2Epub.exe` aus dem [Releases](https://github.com/JohnButzel/gutenberg2epub/releases) Abschnitt herunter.
2. Führe die Datei `Gutenberg2Epub.exe` aus, um die GUI-Anwendung zu starten.

## Verwendung der GUI

1. Gib die Project Gutenberg URL in das bereitgestellte Textfeld ein.
2. Wähle das Ausgabeverzeichnis mit der "Durchsuchen"-Schaltfläche aus oder behalte das Standardverzeichnis bei.
3. Klicke auf die Schaltfläche "Buch laden", um den Konvertierungsprozess zu starten.
4. Eine Nachricht wird angezeigt, die auf die erfolgreiche Konvertierung des E-Books hinweist.

## Kommandozeilenschnittstelle (CLI)

Zusätzlich kannst du die Kommandozeilenschnittstelle verwenden, um dasselbe Ergebnis zu erzielen. Hier ist wie:

1. Öffne eine Eingabeaufforderung oder ein Terminal.
2. Führe den folgenden Befehl aus:

```bash
python cli.py <url>
```
oder
```bash
python cli.py <url> -d <Directory>
```
Ersetze `<url>` durch die URL des Project Gutenberg-Inhalts, den du konvertieren möchtest.

Ersetze `<Directory>` durch den Pfad, wo das Buch gespeichert werden soll.

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

### Kommandozeilenschnittstelle (cli.py)

Das Modul für die Kommandozeilenschnittstelle bietet eine einfache Kommandozeilenschnittstelle, um den gesamten Konvertierungsprozess auszuführen. Es nimmt die URL als Argument und automatisiert den Abruf und Konvertierungsprozess.



## Lizenz

Dieses Projekt steht unter der CC BY-NC-Lizenz - siehe die Datei [LICENSE](LICENSE) für Details.
