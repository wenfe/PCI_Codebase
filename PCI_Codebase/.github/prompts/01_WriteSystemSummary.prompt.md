# System-Dokumentation Prompt

Es soll ein neues Dokument "01_SystemSummary.md" im Ordner "docs" angelegt werden. Das Ziel dieses Dokuments ist es eine Dokumentation des Quellcodes im Ordner "src" zu erstellen als technisches Einstiegsdokument für Entwickler und technische Architekten.
Das Dokument soll eine Übersicht über die 5 - 20 Hauptkomponenten des Systems geben.

Erstelle abschließend eine csv-Datei, die alle Komponenten des Systems auflistet. Die Datei soll den Namen "SystemComponents.csv" haben und im Ordner "docs" abgelegt werden.

## Fachliche Anforderungen

### SystemSummary

- Erzeuge eine Dokumentation zum System.
- Liste die Komponenten des Systems auf, incl. der Komponentenarten (Liste siehe unten).
- Beschreibe fachlich wozu die Komponente dient.
- Führe keine technischen Details oder Quellcode auf. Eine Liste von den ABAP- und DDIC-Artefakten darf enthalten sein, aber keine Details oder Beschreibungen.
- WICHTIG: Beschreibe keine Weiterentwicklungen oder zukünftigen Planungen! Beschreibe keine Betriebsszenarien.

### SystemComponents

Es sollen nur die Hauptkomponenten aufgeführt werden, keine Unterkomponenten.
Die Datei soll die folgenden Spalten enthalten: Paket, Bezeichnung, Komponentenart, Beschreibung, Kapitelnummer in "01_SystemSummary.md" (durch Semikolon getrennt).

### Was ist eine Komponente?

Eine Softwarekomponente ist ein abgrenzbarer, wiederverwendbarer Teil eines Softwaresystems, der eine klar definierte Funktionalität bereitstellt und über definierte Schnittstellen mit anderen Komponenten kommuniziert. Sie umfasst nicht nur technische Artefakte wie Module, Klassen oder Services, sondern auch deren fachliche Gruppierung nach zusammengehörigen Geschäftsprozessen, Funktionsbereichen oder Verantwortlichkeiten.

### Mögliche Komponentenarten

Beachte, dass CLAS und INTF, FUGR und FUBA nicht eindeutig zugeordnet werden können - die Zuordnung erfolgt nach dem dominanten Charakter der Komponente. Ähnlich bei PROG.

1. **Presentation Layer Components**
   GUI, SAPGUI, Transaktionen und die direkt angrenzende Logik
2. **Business Logic Components**
   Tiefergehende Logik, Services, BAPIs.

3. **Data Management Components** → nicht tiefer zergliedern
   Tabelle, Views, CDS-Views, Datenbankzugriffskomponenten

4. **Integration and Communication Components** → zergliedern je Schnittstelle - eine Ebene tiefer
   Alle Arten von Schnittstellen, IDocs, BAPIs, RFCs, Webservices, ALE, EDI. Auch Formulare und Ausgabemedien (Smartforms, Sapscripts, Adobe Forms, etc.)

5. **Infrastructure Components**
   Beispiele:
   - Packages (DEVC) - Development Packages
   - Transport Requests - Workbench/Customizing
   - Software Components (COMP) - Namespaces
   - Transport Layer - Transportschichten
   - Number Range Objects (NROB) - Nummernkreise
   - Authorization Objects (SUSO) - Berechtigungsobjekte
   - Roles (AGR) - Sammelrollen
   - Profiles (PROF) - Berechtigungsprofile
   - Background Jobs - Batch-Verarbeitung
   - Variants (VAR) - Selektionsbildschirm-Varianten
   - Logical Systems - ALE-Konfiguration
   - Configuration Objects - IMG-Knoten
   - Archiving Objects (ARCH) - Datenarchivierung

## Stilistische Anforderungen

- Die Dokumentation soll im Markdown-Format erstellt werden.
- Lege die Dokumentation als `01_SystemSummary.md` im Ordner `docs` ab.
- Erzeuge den Ordner `docs`, falls dieser noch nicht existiert.
- Es dürfen keine Informationen über Datenbanktabellen oder spezielle Klassen auftauchen. Paketnamen dürfen auftauchen.

## Ausschluss

Wenn ABAP-Pakete nicht betrachtet wurden, dann liste diese auf. Versuche, die Gründe dafür zu vermerken, aber vermeide es Pakete nicht zu betrachten. Vermerke dies in der 01_SystemSummary.md.

Wichtig: Ignoriere den Ordner `neu`!
