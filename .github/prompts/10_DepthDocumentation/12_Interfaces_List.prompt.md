````prompt
# Interfaces-Identifikation und Prompt-Generierung

## Ziel

Identifiziere alle eingehenden und ausgehenden Schnittstellen (Interfaces) des ZBV-Systems, gruppiere sie nach Richtung und Komponenten und erstelle für jede Schnittstelle eine individuelle Einzeildokumentation-Prompt-Datei im Ordner `12_Interfaces`.
Verwende Informationen aus den bestehenden Dokumenationen im `docs/`-Verzeichnis. Erst wenn das nicht reicht, dann verewnde den Quellcode im `src/`-Verzeichnis.
---

## Modus & Arbeitsbereich

- **Modus:** `agent`
- **Arbeitsbereich:** `@workspace`

---

## Phase 1: Schnittstellen identifizieren

### Schritt 1.1: Relevante Dateitypen und Orte durchsuchen

Durchsuche den `src/` Ordner und die `docs/` nach Hinweisen auf Schnittstellenbezeichner, RFCs, BAPIs, Webservices, IDocs, FTP/CSV-Exports, REST- oder SOAP-Clients/Server, RFC-Clients und andere Integrationspunkte.

Beispielhafte Powershell-Kommandos (nur als Hinweis, Agent sollte im `@workspace` lesen):

```powershell
Get-ChildItem -Path "src" -Recurse -Include "*.xml","*.tran.xml","*.aqsg.xml","*.prog.abap","*.abap","*.xml" | Select-String -Pattern "RFC|BAPI|IDOC|SOAP|REST|SERVICE|ENDPOINT|CLIENT|CALL FUNCTION|HTTP|POST|PUT|GET|SFTP|FTP|FILE" -SimpleMatch
Get-ChildItem -Path "docs" -Recurse -Filter "*.md" | Select-String -Pattern "Interface|Schnittstelle|RFC|BAPI|IDoc|Webservice|Endpoint|REST|SOAP|FTP|CSV"
````

### Schritt 1.2: Extrahiere für jede gefundene Schnittstelle folgende Basisdaten

- **Interface-Name / Kennung**
- **Richtung:** `incoming` (eingehend) oder `outgoing` (ausgehend)
- **Typ:** `RFC/BAPI`, `IDoc`, `SOAP`, `REST`, `FTP/CSV`, `File`, `DB-View`, `Queue` (z.B. JMS), `Other`
- **Quell-/Ziel-System** (falls ersichtlich)
- **Betroffene Komponenten / Ordner** (z.B. `src/adm/`, `src/hr/`)
- **Verwendete Dateien/Programme:** referenzierte ABAP-Programme, XML-Definitionen, Service-Definitionen
- **Kurzbeschreibung / Zweck**
- **Authentifizierung / Security Hinweise** (z.B. RFC user, HTTPS, Certificates)

Speichere alle Treffer in einer Übersichtsliste im Format:

```markdown
## Interfaces-Übersicht

| Interface | Richtung | Typ | System  | Komponenten | Dateien | Kurzbeschreibung |
| --------- | -------- | --- | ------- | ----------- | ------- | ---------------- |
| {NAME}    | incoming | RFC | SAP-EXT | src/upd/    | src/... | {Kurztext}       |
```

---

## Phase 2: Einzeilige Prompt-Dateien erzeugen

### Schritt 2.1: Zielordner erstellen

Erzeuge den Ordner für die Interface-Prompts:

```
mkdir -p .github/prompts/3_DepthDocumentation/12_Interfaces
```

### Schritt 2.2: Template für jede Schnittstelle

Für jede identifizierte Schnittstelle erstelle eine Datei mit dem Namen `{00NN}_{INTERFACE_NAME}.prompt.md` (laufende Nummer zweistellig) im Ordner `12_Interfaces`. Verwende dieses Einzeilen-Template (Agent-Modus):

```
Modus: agent
Arbeitsbereich: @workspace

Analysiere die oben genannte Schnittstelle im Codebestand von `@workspace`. Beachte die folgenden Punkte
- präzise technische Identifikation (Name, Typ, Richtung)
- involvierte Dateien/Programme (Pfad relativ zu `@workspace`)
- Input/Output-Variablen mit Typ
- Beschreibung Funktionalität
- Einbettung der Schnittstelle in den Prozess

Wenn noch nicht vorhanden, dann lege eine Datei `Interfaces_Overview.md` im Ordner `docs/12_Interfaces/` an mit einer Tabelle aller Schnittstellen.

Füge dort dann eine Zeile für diese Schnittstelle hinzu im Format:
# Interface: {INTERFACE_NAME} | Richtung: {incoming|outgoing} | Typ: {TYPE} | System: {SYSTEM} | Dateien: {FILES} | Kurz: {SHORT_DESCRIPTION}

```

### Schritt 2.3: Qualitätskriterien

- Jeder Prompt-Dateiname muss eindeutig sein und das Interface in Kurzform enthalten.
- Die Einzeilige Ausgabe muss in Pipe-separiertem Format erfolgen (siehe Template).
- Wenn unklare oder mehrere Varianten existieren, erzeuge für jede Variante eine eigene Prompt-Datei.

---

## Phase 3: Ergebnisablage und Weiterverwendung

- Übersichtstabelle speichern als `#newfile:../../docs/03_ComponentDocumentation/12_Interfaces/Interfaces_Overview.md`.
- Jede einzelne Prompt-Datei in ` .github/prompts/3_DepthDocumentation/12_Interfaces/` erzeugen.
- Hinweise zur Ausführung: Die Agenten-Prompts können sequenziell ausgeführt werden, eine pro Schnittstelle, um konsistente Einzeiler zu produzieren.

---

## Hinweise für den Agenten

- Verwende nur Dateien innerhalb von `@workspace`.
- Wenn sensible Verbindungsdaten (Passwörter, Keys) auftauchen, gib niemals Werte aus, sondern notiere nur 'sensitive'.
- Markiere unsichere oder nicht authentifizierte Endpunkte deutlich in der Kurzbeschreibung.

```

```
