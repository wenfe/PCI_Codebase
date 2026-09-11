# GUI-Identifikation und Dokumentations-Prompts-Generierung

## Ziel

Identifiziere alle GUI-Transaktionen (TCODE) im ZBV-System, gruppiere sie nach Komponenten und erstelle für jede GUI einen individuellen Dokumentations-Prompt, der detaillierte Mockups und Funktionsbeschreibungen generiert.

---

## Phase 1: GUI-Identifikation und Gruppierung

### Schritt 1.1: Transaktionscodes identifizieren

Durchsuche den `src/` Ordner nach allen Transaction-Code-Definitionen:

```powershell
# Alle .tran.xml Dateien finden
Get-ChildItem -Path "src" -Recurse -Filter "*.tran.xml" | Select-Object FullName, Directory
```

**Extrahiere für jede Transaktion:**

- **TCODE-Name** (aus `<TCODE>` Tag)
- **Programm-Name** (aus `<PGMNA>` Tag)
- **Beschreibung** (aus `<TTEXT>` Tag, falls vorhanden)
- **Komponente** (aus Ordnerstruktur: `src/adm/`, `src/usr/`, `src/upd/`, etc.)

### Schritt 1.2: Screen-Programme identifizieren

Finde alle Programme mit Dynpro-Screens:

```powershell
# Alle Screen-Definitionen finden
Get-ChildItem -Path "src" -Recurse -Filter "*.screen_*.abap" | Select-Object FullName
```

**Wichtige Screen-Typen:**

- `*.prog.screen_XXXX.abap` - Dynpro-Screens
- `*.fugr.screen_XXXX.abap` - Function Group Screens

### Schritt 1.3: Gruppierung nach Komponenten

Erstelle eine strukturierte Liste nach folgendem Schema:

```markdown
## GUI-Übersicht nach Komponenten

### 1. User & Identity Management (src/usr/)

| TCODE  | Programm             | Beschreibung                 | Screen(s)        | Typ    |
| ------ | -------------------- | ---------------------------- | ---------------- | ------ |
| YSU01  | YBCA1234_YSU01_01    | Benutzer pflegen             | 0100             | Dynpro |
| YSUI   | YBCA1234_YSUI        | Rolle zuordnen               | 0100, 0200       | Dynpro |
| YSUIC  | YBCA1234_YSUIC       | Rolle zuordnen (Collective)  | 0100, 0200       | Dynpro |
| YSUR   | YBCA1234_YSUR_00     | Rollenzuordnung anzeigen     | 0100             | Dynpro |
| YSURC  | YBCA1234_YSURC       | Rollenzuordnung prüfen       | 0100, 0101, 0102 | Dynpro |
| YP02   | YBCA1234_YP02        | Benutzeranalyse              | 0100             | Dynpro |
| YGETBV | YBCA1234_GET_ROLE_BV | Berechtigungsverantwortliche | -                | Report |
| YSUN   | YBCA1234_YSUN        | Benutzerinfo anzeigen        | -                | Report |

### 2. Compliance & Audit (src/adm/)

| TCODE     | Programm                | Beschreibung     | Screen(s) | Typ    |
| --------- | ----------------------- | ---------------- | --------- | ------ |
| YAUDCHECK | YBCA1234_CHECK_AUDITLOG | Audit-Log prüfen | -         | Report |
| YAUDN     | [zu identifizieren]     | [Beschreibung]   | -         | Report |

### 3. Integration Hub (src/upd/)

| TCODE               | Programm   | Beschreibung   | Screen(s) | Typ |
| ------------------- | ---------- | -------------- | --------- | --- |
| [zu identifizieren] | [Programm] | [Beschreibung] | -         | -   |

### 4. Stammdatenverwaltung (src/adm/)

| TCODE | Programm            | Beschreibung   | Screen(s) | Typ    |
| ----- | ------------------- | -------------- | --------- | ------ |
| YAPMA | [zu identifizieren] | [Beschreibung] | -         | Report |

### 5. Workload Counting (src/wl/)

| TCODE                | Programm             | Beschreibung                    | Screen(s) | Typ    |
| -------------------- | -------------------- | ------------------------------- | --------- | ------ |
| YBCA1234WL_DEL_EMPTY | YBCA1234WL_DEL_EMPTY | Leere Workload-Einträge löschen | -         | Report |

### 6. HR User Management (src/hr/)

| TCODE               | Programm   | Beschreibung   | Screen(s) | Typ |
| ------------------- | ---------- | -------------- | --------- | --- |
| [zu identifizieren] | [Programm] | [Beschreibung] | -         | -   |

### 7. Nashcon Interface (src/nash/)

| TCODE               | Programm   | Beschreibung   | Screen(s) | Typ |
| ------------------- | ---------- | -------------- | --------- | --- |
| [zu identifizieren] | [Programm] | [Beschreibung] | -         | -   |
```

**Speichere diese Übersicht in:**
`#newfile:../../docs/03_ComponentDocumentation/GUI_Overview.md`

---

## Phase 2: Prompt-Dateien-Generierung

### Schritt 2.1: Ordnerstruktur erstellen

Erstelle den Zielordner:

```bash
mkdir -p .github/prompts/3_DepthDocumentation/11_GUI_Prompts
```

### Schritt 2.2: Prompt-Template definieren

Verwende folgendes Template für jede GUI (basierend auf `01.04_CreateMockups.prompt.md`):

````markdown
# GUI-Dokumentation: {TCODE} - {Beschreibung}

**Transaktion:** {TCODE}  
**Programm:** {PROGRAMM_NAME}  
**Komponente:** {KOMPONENTE}  
**Typ:** {TYP} (Dynpro/Report/Function Group)

---

## Ziel

Erstelle eine vollständige GUI-Dokumentation für die Transaktion **{TCODE}** mit detaillierten UI-Mockups, Funktionsbeschreibungen und Ablaufdiagrammen.

---

## 1. Analyseaufgaben

### 1.1 Source-Code-Analyse

**Zu analysierende Dateien:**

- Hauptprogramm: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}.prog.abap`
- Screen-Definitionen: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}.prog.screen_*.abap`
- TOP-Include: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}_top.prog.abap`
- Form-Routinen: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}_f*.prog.abap`
- PBO-Module: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}_pbo_*.prog.abap`
- PAI-Module: `#file:../../../src/{ORDNER}/{PROGRAMM_NAME}_pai_*.prog.abap`

**Analysiere:**

1. **Selection-Screen Definitionen**

   - PARAMETERS
   - SELECT-OPTIONS
   - RADIOBUTTON GROUPS
   - Checkboxen
   - Pflichtfelder (OBLIGATORY)

2. **Screen-Felder** (aus screen\_\*.abap)

   - Feldnamen
   - Feldtypen (INPUT, OUTPUT, CHECKBOX, RADIOBUTTON)
   - Labels/Texte
   - Gruppierungen (FRAME)

3. **Ablauflogik**

   - AT SELECTION-SCREEN Ereignisse
   - Validierungen
   - Berechtigungsprüfungen
   - Datenabfragen

4. **Ausgabeformate**
   - ALV-Grids (Feldkatalog)
   - Listen (WRITE Statements)
   - Popup-Dialoge

---

## 2. Mockup-Erstellung

### 2.1 Hauptbildschirm (Selection-Screen oder Einstiegsmaske)

Erstelle ein detailliertes ASCII-Art Mockup nach diesem Muster:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ {TCODE} - {Beschreibung}                                        ⊠ □ ×  │
├─────────────────────────────────────────────────────────────────────────┤
│ System  Edit  Goto  Utilities  Environment  System  Help              │
├─────────────────────────────────────────────────────────────────────────┤
│ 📄 💾 🖨️ 📧 ✂️ 📋 ↩️ ↪️ 🔍 🔧 ❓                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Titel des ersten Abschnitts]                                          │
│  ───────────────────────────────────────────────────────────────────── │
│                                                                         │
│  Feld 1 *:        [________________]  🔍                                │
│  Feld 2:          [________________]                                    │
│                                                                         │
│  ┌─ Optionen ──────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  ☑️ Option 1                                                     │   │
│  │  ☐  Option 2                                                     │   │
│  │                                                                  │   │
│  │  ( ) Radiobutton 1     (•) Radiobutton 2     ( ) Radiobutton 3  │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [▶️ Ausführen]  [💾 Variante]  [🚫 Abbrechen]                          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ ► Bereit                                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Beschreibung des Hauptbildschirms:**

- **Zweck:** [Beschreibe den Zweck des Screens]
- **Eingabefelder:**
  - `Feld 1`: [Beschreibung, Datentyp, Pflichtfeld]
  - `Feld 2`: [Beschreibung, Datentyp]
- **Optionen:**
  - `Option 1`: [Was bewirkt diese Option?]
  - `Radiobutton-Gruppe`: [Welche Auswahlmöglichkeiten?]
- **Buttons:**
  - `Ausführen`: [Was passiert beim Klick?]
  - `Variante`: [Speichert Selektionsparameter]

---

### 2.2 Detailansicht / Arbeitsoberfläche

Wenn vorhanden (bei Dynpro-Dialogen), erstelle Mockup für Detailscreen:

```
╔═══════════════════════════════════════════════════════════════════════╗
║ {TCODE} - Detail: [Objektname]                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  ┌─ Tab 1: Stammdaten ─┬─ Tab 2: Details ──┬─ Tab 3: Historie ───┐  ║
║  │                                                                 │  ║
║  │  Feld A:  [Wert 1________]         Feld D:  [Wert 4________]  │  ║
║  │  Feld B:  [Wert 2________]         Feld E:  [Wert 5________]  │  ║
║  │  Feld C:  [Wert 3________]         Feld F:  [Wert 6________]  │  ║
║  │                                                                 │  ║
║  │  ┌─ Untergruppe ───────────────────────────────────────────┐   │  ║
║  │  │                                                          │   │  ║
║  │  │  Sub-Feld 1:  [___________]                             │   │  ║
║  │  │  Sub-Feld 2:  [___________]                             │   │  ║
║  │  │                                                          │   │  ║
║  │  └──────────────────────────────────────────────────────────┘   │  ║
║  │                                                                 │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║  [💾 Sichern]  [🗑️ Löschen]  [↩️ Zurück]  [🚫 Abbrechen]              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**Beschreibung der Detailansicht:**

- **Tab-Struktur:**
  - `Tab 1`: [Welche Daten werden angezeigt?]
  - `Tab 2`: [Zusätzliche Informationen]
  - `Tab 3`: [Historie/Änderungsverlauf]
- **Felder:** [Liste aller Felder mit Beschreibung]
- **Aktionen:** [Verfügbare Buttons und deren Funktion]

---

### 2.3 Ergebnisliste (ALV-Grid)

Für Reports mit Ausgabeliste:

| ☑️    | Spalte 1  | Spalte 2 | Spalte 3 | Spalte 4 | Spalte 5 | Status     |
| ----- | --------- | -------- | -------- | -------- | -------- | ---------- |
| ☑️    | Wert 1.1  | Wert 1.2 | Wert 1.3 | Wert 1.4 | Wert 1.5 | 🟢 OK      |
| ☐     | Wert 2.1  | Wert 2.2 | Wert 2.3 | Wert 2.4 | Wert 2.5 | 🟡 Warnung |
| ☐     | Wert 3.1  | Wert 3.2 | Wert 3.3 | Wert 3.4 | Wert 3.5 | 🔴 Fehler  |
| **Σ** | **Summe** | **XX**   | **YY**   | **ZZ**   | -        | -          |

**Beschreibung der Ergebnisliste:**

- **Spalten:**
  - `Spalte 1`: [Bedeutung, Datentyp]
  - `Spalte 2`: [Bedeutung, Datentyp]
  - `Status`: [Mögliche Werte und deren Bedeutung]
- **Funktionen:**
  - Sortierung: [Nach welchen Spalten?]
  - Filterung: [Welche Filter sind verfügbar?]
  - Summenzeilen: [Welche Aggregationen?]
  - Export: [Welche Formate?]

---

### 2.4 Fehlerzustände und Validierungen

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚠️  Fehlermeldung                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Beschreibung des Fehlers]                                         │
│                                                                     │
│  Feld: [Feldname]                                                   │
│  Wert: [Fehlerhafter Wert]                                          │
│                                                                     │
│  Erwartung: [Was wäre korrekt?]                                     │
│                                                                     │
│  [OK]                                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Typische Fehlerfälle:**

1. [Fehler 1]: [Beschreibung und Lösung]
2. [Fehler 2]: [Beschreibung und Lösung]
3. [Fehler 3]: [Beschreibung und Lösung]

---

## 3. Ablaufdiagramm

Erstelle ein Mermaid-Diagramm des Programmflusses:

```mermaid
flowchart TD
    Start([Start {TCODE}]) --> Selection[Selection-Screen anzeigen]
    Selection --> Input{Eingabe\nvollständig?}
    Input -->|Nein| Error1[Fehlermeldung]
    Error1 --> Selection
    Input -->|Ja| Auth{Berechtigung\nvorhanden?}
    Auth -->|Nein| Error2[Keine Berechtigung]
    Error2 --> End([Ende])
    Auth -->|Ja| Process[Daten verarbeiten]
    Process --> Query[Datenbankabfrage]
    Query --> Display{Ausgabe-\nformat?}
    Display -->|Liste| ALV[ALV-Grid anzeigen]
    Display -->|Detail| Screen[Detailscreen anzeigen]
    Screen --> Edit{Änderung?}
    Edit -->|Ja| Save[Daten speichern]
    Edit -->|Nein| Back[Zurück]
    Save --> Success[Erfolgsmeldung]
    Success --> End
    ALV --> End
    Back --> End
```

**Ablaufbeschreibung:**

1. **Start:** [Was passiert beim Transaktionsaufruf?]
2. **Validierung:** [Welche Prüfungen werden durchgeführt?]
3. **Verarbeitung:** [Hauptlogik des Programms]
4. **Ausgabe:** [Wie werden Ergebnisse präsentiert?]
5. **Ende:** [Wie wird die Transaktion beendet?]

---

## 4. Funktionsbeschreibung

### 4.1 Hauptfunktionalitäten

1. **[Funktion 1]**

   - **Beschreibung:** [Was macht diese Funktion?]
   - **Auslöser:** [Wie wird sie aktiviert?]
   - **Parameter:** [Welche Eingaben benötigt sie?]
   - **Ergebnis:** [Was ist die Ausgabe?]

2. **[Funktion 2]**
   - [Analog zu Funktion 1]

### 4.2 Tastenkombinationen / Shortcuts

| Taste  | Funktion  |
| ------ | --------- |
| F3     | Zurück    |
| F8     | Ausführen |
| Ctrl+S | Sichern   |
| Ctrl+F | Suchen    |

### 4.3 Berechtigungen

**Erforderliche Berechtigungsobjekte:**

- `{AUTH_OBJ_1}`: [Beschreibung]
- `{AUTH_OBJ_2}`: [Beschreibung]

**Prüfungen im Code:**

```abap
AUTHORITY-CHECK OBJECT '{AUTH_OBJ_1}'
  ID 'ACTVT' FIELD '03'.
```

---

## 5. Technische Details

### 5.1 Datenbankzugriffe

**Gelesene Tabellen:**

- `{TABLE_1}`: [Zweck des Zugriffs]
- `{TABLE_2}`: [Zweck des Zugriffs]

**Schreibzugriffe:**

- `{TABLE_3}`: [Art der Änderung (INSERT/UPDATE/DELETE)]

### 5.2 RFC-Calls / Function Modules

**Aufgerufene Funktionsbausteine:**

- `{FM_1}`: [Zweck]
- `{FM_2}`: [Zweck]

### 5.3 Performance-Aspekte

- **Kritische Queries:** [Langsame SELECT-Statements]
- **Optimierungspotenzial:** [Verbesserungsvorschläge]
- **Laufzeitverhalten:** [Typische Ausführungszeit]

---

## 6. Verlinkungen in Dokumentation

### 6.1 Update Komponenten-Dokumentation

Füge Verlinkung in entsprechende Komponentendokumentation ein:

**Datei:** `#file:../../../docs/03_ComponentDocumentation/{KOMPONENTEN_DOC}.md`

Ergänze im Abschnitt "GUI-Transaktionen":

```markdown
#### {TCODE} - {Beschreibung}

**Typ:** {Dynpro/Report}  
**Hauptprogramm:** `{PROGRAMM_NAME}`

**Zweck:** [Kurzbeschreibung]

**Detaillierte Dokumentation:** [GUI-Mockup {TCODE}](../../../.github/prompts/3_DepthDocumentation/11_GUI_Prompts/{TCODE}_Mockup.md)

**Hauptfunktionen:**

- [Funktion 1]
- [Funktion 2]
- [Funktion 3]

**Mockup-Vorschau:**
[Einbinden des Hauptbildschirm-Mockups]
```

### 6.2 Update GUI-Übersicht

Aktualisiere `docs/03_ComponentDocumentation/GUI_Overview.md`:

```markdown
- ✅ [{TCODE}](../../.github/prompts/3_DepthDocumentation/11_GUI_Prompts/{TCODE}_Mockup.md) - {Beschreibung}
```

---

## 7. Output-Dateien

Erstelle folgende Dateien:

1. **GUI-Mockup-Dokumentation:**
   `#newfile:../11_GUI_Prompts/{TCODE}_Mockup.md`

   - Enthält alle Mockups, Funktionsbeschreibungen und Diagramme

2. **Update GUI-Übersicht:**
   `#file:../../../docs/03_ComponentDocumentation/GUI_Overview.md`

   - Ergänze den Eintrag für diese GUI

3. **Update Komponenten-Dokumentation:**
   `#file:../../../docs/03_ComponentDocumentation/{KOMPONENTEN_DOC}.md`
   - Füge GUI-Sektion mit Verlinkung hinzu

---

## Qualitätskriterien

Stelle sicher, dass die Dokumentation folgende Kriterien erfüllt:

- ✅ **Vollständigkeit:** Alle Screens und Funktionen dokumentiert
- ✅ **Realitätsnähe:** Mockups sehen wie echtes SAP GUI aus
- ✅ **Beispieldaten:** Realistische Testdaten in Mockups
- ✅ **Lesbarkeit:** Klare Struktur und verständliche Beschreibungen
- ✅ **Verlinkungen:** Alle Cross-References korrekt gesetzt
- ✅ **Technische Tiefe:** Code-Analyse ausreichend detailliert
- ✅ **Ablauflogik:** Programmfluss nachvollziehbar dargestellt

---

## Hinweise

- Verwende die Mockup-Techniken aus `01.04_CreateMockups.prompt.md`
- Analysiere den ABAP-Code gründlich, um genaue Feldbeschreibungen zu erhalten
- Beachte Kommentare im Code für Kontextinformationen
- Prüfe auf mehrsprachige Textelemente
- Identifiziere alle Berechtigungsprüfungen
````

### Schritt 2.3: Prompts generieren

Für **jede identifizierte GUI** aus Phase 1:

1. Kopiere das Template
2. Ersetze alle Platzhalter (`{TCODE}`, `{PROGRAMM_NAME}`, etc.)
3. Passe Dateipfade an die tatsächliche Struktur an
4. Speichere als `.github/prompts/3_DepthDocumentation/11_GUI_Prompts/{TCODE}_Documentation.prompt.md`

**Beispiel-Dateinamen:**

- `YSU01_Documentation.prompt.md`
- `YSUI_Documentation.prompt.md`
- `YSURC_Documentation.prompt.md`
- `YAUDCHECK_Documentation.prompt.md`
- etc.

---

## Phase 3: Validierung und Verlinkung

### Schritt 3.1: Konsistenzprüfung

Prüfe für jeden generierten Prompt:

- ✅ Alle Dateipfade existieren
- ✅ TCODE ist korrekt
- ✅ Komponente ist zugeordnet
- ✅ Template vollständig ausgefüllt

### Schritt 3.2: Index-Datei erstellen

Erstelle eine Master-Index-Datei:

`#newfile:11_GUI_Prompts/README.md`

```markdown
# GUI-Dokumentations-Prompts Index

Dieser Ordner enthält für jede GUI-Transaktion einen individuellen Dokumentations-Prompt.

## Verwendung

1. Öffne den gewünschten Prompt (z.B. `YSU01_Documentation.prompt.md`)
2. Führe den Prompt mit Copilot aus
3. Die Dokumentation wird automatisch erstellt und verlinkt

## Übersicht nach Komponenten

### User & Identity Management

- [YSU01_Documentation.prompt.md](./YSU01_Documentation.prompt.md) - Benutzer pflegen
- [YSUI_Documentation.prompt.md](./YSUI_Documentation.prompt.md) - Rolle zuordnen
- [YSUIC_Documentation.prompt.md](./YSUIC_Documentation.prompt.md) - Rolle zuordnen (Collective)
- [YSUR_Documentation.prompt.md](./YSUR_Documentation.prompt.md) - Rollenzuordnung anzeigen
- [YSURC_Documentation.prompt.md](./YSURC_Documentation.prompt.md) - Rollenzuordnung prüfen
- [YP02_Documentation.prompt.md](./YP02_Documentation.prompt.md) - Benutzeranalyse
- [YGETBV_Documentation.prompt.md](./YGETBV_Documentation.prompt.md) - Berechtigungsverantwortliche

### Compliance & Audit

- [YAUDCHECK_Documentation.prompt.md](./YAUDCHECK_Documentation.prompt.md) - Audit-Log prüfen

### [Weitere Komponenten]

- ...

## Status

- [ ] Phase 1: GUI-Identifikation abgeschlossen
- [ ] Phase 2: Prompt-Generierung abgeschlossen
- [ ] Phase 3: Alle Prompts ausgeführt
- [ ] Phase 4: Verlinkungen erstellt
```

---

## Ausführungsplan

### Schritt 1: Starte mit Phase 1

Analysiere alle `.tran.xml` und `.screen_*.abap` Dateien und erstelle die GUI-Übersicht.

### Schritt 2: Generiere Prompt-Dateien

Für jede GUI in der Übersicht, erstelle eine Prompt-Datei nach dem Template.

### Schritt 3: Validiere

Prüfe alle generierten Prompts auf Vollständigkeit.

### Schritt 4: Index erstellen

Erstelle die README.md mit allen Links.

---

## Erwartete Ausgaben

Nach Abschluss dieser Aufgabe sollten folgende Dateien existieren:

1. `docs/03_ComponentDocumentation/GUI_Overview.md` - Vollständige GUI-Liste
2. `.github/prompts/3_DepthDocumentation/11_GUI_Prompts/README.md` - Index
3. `.github/prompts/3_DepthDocumentation/11_GUI_Prompts/{TCODE}_Documentation.prompt.md` - Ein Prompt pro GUI (ca. 20-30 Dateien)

**Hinweis:** Die eigentlichen Mockup-Dokumentationen werden erst erstellt, wenn die einzelnen Prompts ausgeführt werden!

---

## Nächste Schritte

Nach Abschluss dieses Prompts:

1. Führe systematisch jeden generierten GUI-Prompt aus
2. Erstelle so die vollständige GUI-Dokumentation
3. Verlinke in den Komponentendokumentationen
4. Erstelle einen Gesamt-Index aller GUI-Mockups
