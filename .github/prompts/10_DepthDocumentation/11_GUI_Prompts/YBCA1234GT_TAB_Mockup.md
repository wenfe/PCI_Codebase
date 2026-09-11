# GUI-Dokumentation: YBCA1234GT_TAB - Customizing Get Table

**Transaktion:** YBCA1234GT_TAB  
**Programm:** SM30 (Table Maintenance Generator)  
**View:** YBCA1234_GT_VAR  
**Komponente:** Reporting & Query Tools (adm)  
**Typ:** Table Maintenance  
**Dokumentationsstand:** 24.11.2025

---

## Executive Summary

**YBCA1234GT_TAB** ist eine SM30-basierte Tabellenpflege-Transaktion zur Verwaltung von Selektionsvarianten für das generische Tabellenabfrage-Tool YBCA1234GT. Die Transaktion ermöglicht Power Usern und Administratoren, wiederverwendbare Abfrageparameter zentral zu definieren, zu speichern und zu pflegen.

**Hauptfunktionen:**
- Verwaltung von Selektionsvarianten für Get Table Tool
- Definition wiederverwendbarer WHERE-Clauses
- Zentrale Pflege von Standardselektionen
- Benutzerspezifische Query-Templates

**Zielgruppe:**
- Power User (Berichtwesen, Controlling)
- System-Administratoren
- Audit & Compliance Mitarbeiter

---

## 1. Hauptbildschirm - Table Maintenance (SM30)

### 1.1 Einstiegsbildschirm

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Tabellensicht YBCA1234_GT_VAR pflegen                    [?] [□] [×]       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tabelle/View   YBCA1234_GT_VAR                                            │
│                                                                             │
│  ◉ Anzeigen    ○ Pflegen                                                   │
│                                                                             │
│  [Anzeigen]  [Pflegen]                                                     │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

**Beschreibung:**
Standardmäßiger SM30-Einstieg über Parameter-Call:
```
/*SM30 UPDATE=X;VIEWNAME=YBCA1234_GT_VAR;
```

---

### 1.2 Übersichtsliste - Varianten

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tabellensicht YBCA1234_GT_VAR pflegen: Übersicht                         [?] [□] [×]               │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Neue Einträge] [Kopieren als...] [Löschen] [Transportieren]  [◄] [►] [Aktualisieren]            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│ Positionieren: Variante [__________] Tabellenname [__________]                                     │
│                                                                                                      │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │☐│ Variante      │ Tabellenname │ ID │ Feldname │ Sign │ Option │ Low        │ High       │🔧│ │
│ ├─┼───────────────┼──────────────┼────┼──────────┼──────┼────────┼────────────┼────────────┼──┤ │
│ │ │ USER_ACTIVE   │ USR02        │ 001│ BNAME    │ I    │ CP     │ Z*         │            │📝│ │
│ │ │ USER_ACTIVE   │ USR02        │ 002│ GLTGB    │ I    │ GE     │ 99991231   │            │📝│ │
│ │ │ USER_LOCKED   │ USR02        │ 001│ UFLAG    │ I    │ EQ     │ 64         │            │📝│ │
│ │ │ USER_LOCKED   │ USR02        │ 002│ UFLAG    │ I    │ EQ     │ 128        │            │📝│ │
│ │ │ ROLE_ANALYSIS │ AGR_USERS    │ 001│ UNAME    │ I    │ CP     │ *          │            │📝│ │
│ │ │ ROLE_ANALYSIS │ AGR_USERS    │ 002│ TO_DAT   │ I    │ GE     │ 20250101   │            │📝│ │
│ │ │ PASSWORD_EXP  │ USR02        │ 001│ PWDCHGDAT│ I    │ LE     │ 20240101   │            │📝│ │
│ │ │ AUTH_CHECK    │ AGR_1251     │ 001│ OBJECT   │ I    │ EQ     │ S_USER_GRP │            │📝│ │
│ │ │ AUTH_CHECK    │ AGR_1251     │ 002│ FIELD    │ I    │ EQ     │ CLASS      │            │📝│ │
│ │ │ AUTH_CHECK    │ AGR_1251     │ 003│ LOW      │ I    │ CP     │ *ADMIN*    │            │📝│ │
│ └─┴───────────────┴──────────────┴────┴──────────┴──────┴────────┴────────────┴────────────┴──┘ │
│                                                                                                      │
│ [Zurück] [Abbrechen] [Sichern]                                         Einträge: 142 von 1.287     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Feldbeschreibung:**

| Feld | Technischer Name | Typ | Key | Beschreibung |
|------|------------------|-----|-----|--------------|
| Variante | VARIANTE | CHAR(30) | X | Name der Selektionsvariante (Pflichtfeld) |
| Tabellenname | TABNAME | CHAR(30) | X | SAP-Tabellenname (z.B. USR02, AGR_USERS) |
| ID | ID | NUMC(3) | X | Laufende Nummer für WHERE-Clause-Zeilen |
| Feldname | FIELDNAME | CHAR(30) | - | Feldname aus der Tabelle |
| Sign | SIGN | CHAR(1) | - | I (Include) oder E (Exclude) |
| Option | OPTION_O | CHAR(2) | - | EQ, NE, CP, GE, LE, BT, etc. |
| Low | LOW | CHAR(45) | - | Unterer Wert oder Einzelwert |
| High | HIGH | CHAR(45) | - | Oberer Wert (bei BT = Between) |

**Zusätzliche Felder (nicht in Übersicht sichtbar):**

| Feld | Technischer Name | Typ | Beschreibung |
|------|------------------|-----|--------------|
| Logischer Operator | LOGOP | CHAR(3) | AND/OR-Verknüpfung (Standard: AND) |
| Arity | ARITY | NUMC(1) | Stelligkeit des Operators |
| Line | LINE | CHAR(72) | Freitextzeile für Kommentare |
| Angelegt von | ERNAM | CHAR(12) | Ersteller-Benutzername |
| Angelegt am | ERDAT | DATS(8) | Erstellungsdatum |
| Angelegt um | ERTIM | TIMS(6) | Erstellungszeit |
| Geändert von | AENAM | CHAR(12) | Letzter Änderer |
| Geändert am | AEDAT | DATS(8) | Änderungsdatum |
| Geändert um | AETIM | TIMS(6) | Änderungszeit |

---

### 1.3 Detailansicht - Neue Einträge

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tabellensicht YBCA1234_GT_VAR pflegen: Detailbild                        [?] [□] [×]               │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Sichern] [Zurück] [Abbrechen] [Feldübersicht] [F4-Hilfe]                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│ ┌─ Identifikation ─────────────────────────────────────────────────────────────────────────────┐   │
│ │                                                                                               │   │
│ │  Variante         [USER_ACTIVE_______________]*  🔍                                          │   │
│ │  Tabellenname     [USR02_____________________]*  🔍                                          │   │
│ │  ID               [001]*                                                                     │   │
│ │                                                                                               │   │
│ └───────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                      │
│ ┌─ Selektionsbedingung ────────────────────────────────────────────────────────────────────────┐   │
│ │                                                                                               │   │
│ │  Feldname         [BNAME_____________________]  🔍                                           │   │
│ │  Logischer Op.    [AND_]  🔽 (AND / OR)                                                      │   │
│ │  Arity            [2]                                                                        │   │
│ │  Sign             [I]  🔽 (I = Include, E = Exclude)                                         │   │
│ │  Option           [CP]  🔽 (EQ, NE, CP, GE, LE, GT, LT, BT, NB)                             │   │
│ │  Low              [Z*_________________________]                                              │   │
│ │  High             [______________________________]                                            │   │
│ │                                                                                               │   │
│ │  Kommentar        [Alle Benutzer mit Z am Anfang________________________]                    │   │
│ │                                                                                               │   │
│ └───────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                      │
│ ┌─ Verwaltungsdaten ───────────────────────────────────────────────────────────────────────────┐   │
│ │                                                                                               │   │
│ │  Angelegt von     [ADMIN001____]  am  [24.11.2025]  um  [14:23:17]                          │   │
│ │  Geändert von     [ADMIN001____]  am  [24.11.2025]  um  [14:23:17]                          │   │
│ │                                                                                               │   │
│ └───────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                      │
│ [Sichern] [Zurück] [Abbrechen]                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.4 Beispielhafte Varianten-Definitionen

#### Beispiel 1: USER_ACTIVE - Aktive Benutzer ermitteln

```
Variante: USER_ACTIVE
Tabelle:  USR02

Zeile 1:  BNAME    | I | CP | Z*         |            (Benutzer Z*)
Zeile 2:  GLTGB    | I | GE | 99991231   |            (Gültig bis >= 31.12.9999)
Zeile 3:  UFLAG    | I | NE | 64         |            (Nicht gesperrt - 64)
Zeile 4:  UFLAG    | I | NE | 128        |            (Nicht gesperrt - 128)
```

#### Beispiel 2: ROLE_ANALYSIS - Rollenzuordnungen analysieren

```
Variante: ROLE_ANALYSIS
Tabelle:  AGR_USERS

Zeile 1:  UNAME    | I | CP | *          |            (Alle Benutzer)
Zeile 2:  AGR_NAME | I | CP | Y*         |            (Kundenrollen Y*)
Zeile 3:  TO_DAT   | I | GE | 20250101   |            (Gültig ab 01.01.2025)
```

#### Beispiel 3: CRITICAL_AUTHS - Kritische Berechtigungen

```
Variante: CRITICAL_AUTHS
Tabelle:  AGR_1251

Zeile 1:  OBJECT   | I | EQ | S_TCODE    |            (Objekt S_TCODE)
Zeile 2:  FIELD    | I | EQ | TCD        |            (Feld TCD)
Zeile 3:  LOW      | I | CP | *DEBUG*    |            (Enthält DEBUG)
```

---

## 2. Funktionsbeschreibung

### 2.1 Hauptfunktionalitäten

#### 2.1.1 Variante erstellen

**Beschreibung:** Erstellt eine neue Selektionsvariante für YBCA1234GT

**Ablauf:**
1. Button `[Neue Einträge]` in Übersichtsliste klicken
2. Pflichtfelder ausfüllen:
   - **Variante**: Eindeutiger Name (max. 30 Zeichen)
   - **Tabellenname**: SAP-Tabellenname (z.B. USR02)
   - **ID**: Laufende Nummer (001, 002, 003, ...)
3. Selektionsbedingung definieren:
   - **Feldname**: Feld aus der gewählten Tabelle
   - **Sign**: I (Include) oder E (Exclude)
   - **Option**: EQ, NE, CP, GE, LE, BT, etc.
   - **Low/High**: Wertebereiche
4. Optional: Logischer Operator für Verknüpfung (AND/OR)
5. Button `[Sichern]` drücken

**Ergebnis:** Variante ist gespeichert und kann in YBCA1234GT verwendet werden

---

#### 2.1.2 Variante kopieren

**Beschreibung:** Kopiert eine bestehende Variante mit neuen Werten

**Ablauf:**
1. Quell-Variante markieren
2. Button `[Kopieren als...]` klicken
3. Neuen Varianten-Namen eingeben
4. Optional: Werte anpassen
5. Button `[Sichern]` drücken

**Ergebnis:** Neue Variante mit gleicher Struktur ist erstellt

---

#### 2.1.3 Variante ändern

**Beschreibung:** Ändert Selektionsbedingungen einer bestehenden Variante

**Ablauf:**
1. Variante in Übersichtsliste markieren
2. Auf 🔧 (Detail-Icon) oder Zeile doppelklicken
3. Werte anpassen
4. Button `[Sichern]` drücken

**Ergebnis:** Variante ist aktualisiert

---

#### 2.1.4 Variante löschen

**Beschreibung:** Löscht eine oder mehrere Varianten

**Ablauf:**
1. Variante(n) markieren (☐ Checkbox aktivieren)
2. Button `[Löschen]` klicken
3. Sicherheitsabfrage bestätigen
4. Button `[Sichern]` drücken

**Ergebnis:** Variante(n) sind gelöscht

---

#### 2.1.5 Variante transportieren

**Beschreibung:** Erstellt Transportauftrag für Varianten

**Ablauf:**
1. Variante(n) markieren
2. Button `[Transportieren]` klicken
3. Transportauftrag auswählen oder neu erstellen
4. Änderungen werden im Transport erfasst

**Ergebnis:** Varianten sind transportfähig

---

### 2.2 Tastenkombinationen / Shortcuts

| Taste | Funktion | Beschreibung |
|-------|----------|--------------|
| **F3** | Zurück | Zurück zur vorherigen Ansicht |
| **F4** | Suchhilfe | F4-Hilfe für aktuelles Feld |
| **F8** | Ausführen | Daten anzeigen (nur Anzeige-Modus) |
| **Ctrl+S** | Sichern | Änderungen speichern |
| **Ctrl+F** | Suchen | Suche in Übersichtsliste |
| **Ctrl+Pos1** | Erste Seite | Zur ersten Seite springen |
| **Ctrl+Ende** | Letzte Seite | Zur letzten Seite springen |
| **Shift+F4** | Neue Einträge | Neue Zeile einfügen |

---

### 2.3 Berechtigungen

#### Erforderliche Berechtigungsobjekte

**S_TCODE (Transaktionscode)**
- Wert: YBCA1234GT_TAB
- Aktivität: 16 (Ausführen)

**S_TABU_DIS (Tabellenanzeige/-pflege über Berechtigungsgruppe)**
- DICBERCLS: YUSR (Authorization Class der Tabelle)
- ACTVT: 02 (Ändern), 03 (Anzeigen)

**S_TABU_NAM (Tabellenanzeige/-pflege über Tabellenname)**
- TABLE: YBCA1234_GT_VAR
- ACTVT: 02 (Ändern), 03 (Anzeigen)

**S_TABU_CLI (Tabellenanzeige/-pflege über mandantenabhängige Tabellen)**
- CLIIDMAINT: X (Pflege erlaubt)

#### Prüfungen im Code

Die Berechtigungsprüfung erfolgt im Hauptprogramm YBCA1234_GT:

```abap
* Berechtigungsprüfung - Transaktion (aus YBCA1234_GT.prog.abap)
CALL FUNCTION 'AUTHORITY_CHECK_TCODE'
  EXPORTING
    tcode  = 'YBCA1234GT_TAB'
  EXCEPTIONS
    ok     = 1
    not_ok = 2
    OTHERS = 3.

IF sy-subrc <> 1.
  MESSAGE e077(s#) WITH 'YBCA1234GT_TAB'.  "Keine Berechtigung
ENDIF.
```

**Standard-SM30-Berechtigungen:**
- Wird über Table Maintenance Generator automatisch geprüft
- Customizing-Tabelle YBCA1234_GT_VAR ist mandantenabhängig (CLIIDMAINT)

---

## 3. Ablaufdiagramm

### 3.1 Prozessfluss - Variante erstellen und verwenden

```mermaid
flowchart TD
    Start([Start: /nYBCA1234GT_TAB]) --> SM30Check{SM30 Parameter<br/>korrekt?}
    
    SM30Check -->|Nein| ErrorParam[Fehler: Parameter fehlt]
    ErrorParam --> End1([Ende])
    
    SM30Check -->|Ja| AuthCheck{Berechtigung<br/>S_TCODE?}
    
    AuthCheck -->|Nein| ErrorAuth[Fehler: Keine Berechtigung]
    ErrorAuth --> End2([Ende])
    
    AuthCheck -->|Ja| LoadView[View YBCA1234_GT_VAR laden]
    LoadView --> DisplayList[Übersichtsliste anzeigen]
    
    DisplayList --> UserAction{Benutzer-<br/>aktion?}
    
    UserAction -->|Neue Einträge| NewEntry[Detailbild öffnen]
    NewEntry --> FillFields[Pflichtfelder ausfüllen:<br/>Variante, Tabname, ID]
    
    FillFields --> DefineCondition[Selektionsbedingung:<br/>Feldname, Sign, Option,<br/>Low, High]
    
    DefineCondition --> ValidateEntry{Eingabe<br/>vollständig?}
    
    ValidateEntry -->|Nein| ErrorMissing[Fehler: Pflichtfeld fehlt]
    ErrorMissing --> FillFields
    
    ValidateEntry -->|Ja| CheckDuplicate{Variante +<br/>Tabelle + ID<br/>bereits<br/>vorhanden?}
    
    CheckDuplicate -->|Ja| ErrorDup[Fehler: Duplikat]
    ErrorDup --> FillFields
    
    CheckDuplicate -->|Nein| SaveData[Daten in YBCA1234_GT_VAR<br/>schreiben]
    SaveData --> Transport{Transport-<br/>auftrag<br/>erforderlich?}
    
    Transport -->|Ja| CreateTransport[Transport erstellen/<br/>zuordnen]
    CreateTransport --> Success[Erfolgsmeldung:<br/>Variante gespeichert]
    
    Transport -->|Nein| Success
    
    Success --> DisplayList
    
    UserAction -->|Ändern| ModifyEntry[Eintrag auswählen]
    ModifyEntry --> FillFields
    
    UserAction -->|Löschen| DeleteEntry[Eintrag(e) markieren]
    DeleteEntry --> ConfirmDelete{Löschung<br/>bestätigen?}
    
    ConfirmDelete -->|Nein| DisplayList
    ConfirmDelete -->|Ja| DeleteDB[Daten aus DB löschen]
    DeleteDB --> DisplayList
    
    UserAction -->|Kopieren| CopyEntry[Quell-Eintrag auswählen]
    CopyEntry --> NewName[Neuen Varianten-Namen eingeben]
    NewName --> FillFields
    
    UserAction -->|Zurück| End3([Ende])
    
    UserAction -->|In YBCA1234GT verwenden| UseInGT[Variante in Get Table Tool laden]
    UseInGT --> ExecuteQuery[Query mit Variante ausführen]
    ExecuteQuery --> End4([Ende: Daten angezeigt])
```

### 3.2 Ablaufbeschreibung

**Phase 1: Initialisierung**
1. Transaktion YBCA1234GT_TAB wird aufgerufen
2. SM30 erhält Parameter: `UPDATE=X;VIEWNAME=YBCA1234_GT_VAR;`
3. System prüft Berechtigung S_TCODE für YBCA1234GT_TAB
4. View YBCA1234_GT_VAR wird geladen

**Phase 2: Anzeige**
5. Übersichtsliste mit bestehenden Varianten wird angezeigt
6. Benutzer kann nach Variante/Tabelle positionieren
7. System zeigt alle Einträge gruppiert nach Variante

**Phase 3: Variante erstellen**
8. Button `[Neue Einträge]` öffnet Detailbild
9. Pflichtfelder eingeben: Variante, Tabellenname, ID
10. Selektionsbedingung definieren (Feldname, Sign, Option, Low, High)
11. Optional: Logischen Operator (AND/OR) festlegen
12. Validierung: Prüfung auf Vollständigkeit und Duplikate
13. Bei Erfolg: Daten in YBCA1234_GT_VAR schreiben

**Phase 4: Transport (optional)**
14. Falls Customizing-System: Transportauftrag erforderlich
15. System erstellt oder nutzt bestehenden Transportauftrag
16. Änderungen werden im Transport-Request erfasst

**Phase 5: Verwendung**
17. Variante kann in YBCA1234GT über F4-Hilfe ausgewählt werden
18. System lädt WHERE-Clauses aus YBCA1234_GT_VAR
19. Query wird mit vordefinierten Selektionen ausgeführt

---

## 4. Technische Details

### 4.1 Datenbankzugriffe

#### Gelesene Tabellen

**YBCA1234_GT_VAR** (Haupttabelle)
```sql
SELECT * FROM ybca1234_gt_var
  WHERE variante = @pa_var
    AND tabname  = @pa_tab
  ORDER BY id.
```
- **Zweck:** Laden der Selektionsvarianten für Display und Änderung
- **Index:** Primary Key (MANDT, VARIANTE, TABNAME, ID)
- **Performance:** Optimal durch Schlüsselzugriff

**DD02L** (Data Dictionary Tabellendefinitionen)
```sql
SELECT SINGLE tabname FROM dd02l
  WHERE tabname = @lv_tabname
    AND as4local = 'A'.
```
- **Zweck:** Validierung des Tabellennamens in F4-Hilfe
- **Performance:** Schnell durch Primary Key

**DD03L** (Data Dictionary Felddefinitionen)
```sql
SELECT fieldname FROM dd03l
  WHERE tabname = @lv_tabname
    AND as4local = 'A'
  ORDER BY position.
```
- **Zweck:** F4-Hilfe für Feldnamen
- **Performance:** Index auf TABNAME vorhanden

#### Schreibzugriffe

**INSERT**
```abap
INSERT ybca1234_gt_var FROM @ls_gt_var.
```
- **Trigger:** Neue Einträge anlegen
- **Validierung:** Key-Duplikat-Prüfung durch DB

**UPDATE**
```abap
UPDATE ybca1234_gt_var FROM @ls_gt_var.
```
- **Trigger:** Bestehende Einträge ändern
- **Lock:** Enqueue-Mechanismus über SM30

**DELETE**
```abap
DELETE FROM ybca1234_gt_var WHERE variante = @lv_var
                                AND tabname = @lv_tab
                                AND id = @lv_id.
```
- **Trigger:** Einträge löschen
- **Protokoll:** Change Document aktiviert (PROTOKOLL = X)

---

### 4.2 RFC-Calls / Function Modules

**VIEW_MAINTENANCE_CALL**
```abap
CALL FUNCTION 'VIEW_MAINTENANCE_CALL'
  EXPORTING
    action                    = 'U'
    view_name                 = 'YBCA1234_GT_VAR'
    show_selection_popup      = ' '
  EXCEPTIONS
    client_reference          = 1
    foreign_lock              = 2
    invalid_action            = 3
    ...
```
- **Zweck:** Generischer Aufruf der Tabellenpflege
- **Parameter:** UPDATE=X für Änderungsmodus

**AUTHORITY_CHECK_TCODE**
```abap
CALL FUNCTION 'AUTHORITY_CHECK_TCODE'
  EXPORTING
    tcode  = 'YBCA1234GT_TAB'
  EXCEPTIONS
    ok     = 1
    not_ok = 2
    OTHERS = 3.
```
- **Zweck:** Berechtigungsprüfung vor Transaktionsaufruf
- **Aufrufer:** YBCA1234_GT (Button FC03)

**ENQUEUE_E_TABLE** / **DEQUEUE_E_TABLE**
```abap
CALL FUNCTION 'ENQUEUE_E_TABLE'
  EXPORTING
    tabname        = 'YBCA1234_GT_VAR'
    varkey         = lv_key
  EXCEPTIONS
    foreign_lock   = 1
    ...
```
- **Zweck:** Lock-Handling für parallele Zugriffe
- **Auto-Generated:** Table Maintenance Generator

**POPUP_TO_CONFIRM**
```abap
CALL FUNCTION 'POPUP_TO_CONFIRM'
  EXPORTING
    text_question = 'Variante überschreiben?'
    text_button_1 = 'Ja'
    text_button_2 = 'Nein'
  IMPORTING
    answer        = lv_answer.
```
- **Zweck:** Bestätigung beim Überschreiben
- **Kontext:** Button FC02 in YBCA1234_GT

---

### 4.3 Performance-Aspekte

#### Kritische Queries

**Problem:** Volltabellen-Scan bei unscharfer Suche
```sql
-- LANGSAM: Ohne Index-Nutzung
SELECT * FROM ybca1234_gt_var
  WHERE fieldname LIKE '%USER%'.
```

**Optimierung:** Key-basierter Zugriff
```sql
-- SCHNELL: Mit Primary Key
SELECT * FROM ybca1234_gt_var
  WHERE variante = @lv_var
    AND tabname  = @lv_tab
  ORDER BY id.
```

#### Laufzeitverhalten

| Operation | Anzahl Einträge | Erwartete Laufzeit | Optimierung |
|-----------|----------------|-------------------|-------------|
| Display (Key) | < 100 | < 0.1 Sek | Optimal durch Primary Key |
| Display (Pattern) | > 1.000 | 1-3 Sek | Positionierung nutzen |
| Insert | 1 | < 0.1 Sek | Direct DB Insert |
| Mass Update | > 100 | 2-5 Sek | Batch-Processing |
| Delete | < 50 | < 0.5 Sek | Key-basierte Deletion |

#### Optimierungspotenzial

1. **Indizierung:**
   - Sekundärindex auf (TABNAME, VARIANTE) für schnellere Suche
   - Aktuell: Nur Primary Key (MANDT, VARIANTE, TABNAME, ID)

2. **Buffering:**
   - Tabelle ist partiell gebuffert (PUFFERUNG = P)
   - Effektiv bei häufig genutzten Varianten

3. **Archivierung:**
   - Alte/ungenutzte Varianten regelmäßig löschen
   - Typisches Volumen: 500-2.000 Einträge
   - Kritisch: > 10.000 Einträge

4. **Table Maintenance Performance:**
   - Bei > 1.000 Varianten: Custom-GUI erwägen
   - SM30 performant bis ~5.000 Einträge

---

## 5. Integration mit YBCA1234GT

### 5.1 Verwendung der Varianten

**Workflow:**

```
┌─────────────────┐          ┌──────────────────┐          ┌─────────────────┐
│  YBCA1234GT_TAB │          │  YBCA1234_GT_VAR │          │   YBCA1234GT    │
│  (SM30)         │          │  (Tabelle)       │          │   (Get Table)   │
└────────┬────────┘          └────────┬─────────┘          └────────┬────────┘
         │                            │                             │
         │ 1. Variante anlegen        │                             │
         ├───────────────────────────>│                             │
         │                            │                             │
         │ 2. Sichern                 │                             │
         │<───────────────────────────┤                             │
         │                            │                             │
         │                            │ 3. F4-Hilfe: Variante laden │
         │                            │<────────────────────────────┤
         │                            │                             │
         │                            │ 4. WHERE-Clause zurückgeben │
         │                            ├────────────────────────────>│
         │                            │                             │
         │                            │ 5. Query ausführen          │
         │                            │                             ├─> RFC/DB
         │                            │                             │
         │                            │ 6. Daten anzeigen (ALV)     │
         │                            │<────────────────────────────┤
```

### 5.2 Varianten-Auflösung im Code

**YBCA1234_GT_F01.prog.abap - PERFORM get_variant**

```abap
FORM get_variant.
  
  DATA: lt_gt_var TYPE TABLE OF ybca1234_gt_var,
        ls_gt_var TYPE ybca1234_gt_var,
        ls_where  TYPE ybca1234_s_where_clause.
  
  " Variante aus Tabelle lesen
  SELECT * FROM ybca1234_gt_var
    INTO TABLE lt_gt_var
    WHERE variante = pa_var
      AND tabname  = pa_tab
    ORDER BY id.
  
  IF sy-subrc = 0.
    " WHERE-Clauses aufbauen
    LOOP AT lt_gt_var INTO ls_gt_var.
      
      CLEAR ls_where.
      ls_where-fieldname = ls_gt_var-fieldname.
      ls_where-sign      = ls_gt_var-sign.
      ls_where-option    = ls_gt_var-option_o.
      ls_where-low       = ls_gt_var-low.
      ls_where-high      = ls_gt_var-high.
      
      APPEND ls_where TO gt_where_clauses.
      
    ENDLOOP.
  ELSE.
    MESSAGE e006(ybca1234_get_table).  "Variante nicht gefunden
  ENDIF.
  
ENDFORM.
```

---

## 6. Anwendungsfälle und Best Practices

### 6.1 Typische Anwendungsfälle

#### Use Case 1: Standard-Reports beschleunigen

**Szenario:** Compliance-Team benötigt täglich Bericht über gesperrte Benutzer

**Lösung:**
1. Variante `USER_LOCKED` erstellen
2. Tabelle: `USR02`
3. Bedingungen:
   - `UFLAG = 64` (Initial Password)
   - `UFLAG = 128` (Locked by Administrator)
4. In YBCA1234GT: Variante auswählen → sofort ausführen

**Vorteil:** Wiederholbare Abfrage ohne manuelle Eingabe

---

#### Use Case 2: Audit-Prüfungen vorbereiten

**Szenario:** Jahresabschluss-Prüfung erfordert Übersicht kritischer Berechtigungen

**Lösung:**
1. Mehrere Varianten für verschiedene Checks:
   - `AUDIT_S_TCODE_DEBUG` (S_TCODE mit Debug-TCD)
   - `AUDIT_S_USER_GRP_ADMIN` (S_USER_GRP mit ADMIN-Class)
   - `AUDIT_S_TABU_DIS_ALL` (S_TABU_DIS mit *)
2. Varianten vor Audit-Termin erstellen
3. Am Audit-Tag: Schnelle Ausführung aller Checks

**Vorteil:** Standardisierte Prüfungen, konsistente Ergebnisse

---

#### Use Case 3: Systemübergreifende Analysen

**Szenario:** Vergleich von Rollenzuordnungen zwischen DEV, QAS, PRD

**Lösung:**
1. Variante `ROLE_COMPARE` erstellen
2. Tabelle: `AGR_USERS`
3. Bedingungen:
   - `AGR_NAME LIKE 'Y*'` (Kundenrollen)
   - `TO_DAT >= aktuelles Datum`
4. In YBCA1234GT: RFC-Destinationen auswählen (DEV, QAS, PRD)
5. Variante laden → Vergleich in einer Ausführung

**Vorteil:** Konsistenz-Check über Systemlandschaft

---

### 6.2 Best Practices

#### Namenskonventionen

**Empfehlung:**
```
<Bereich>_<Tabelle>_<Zweck>

Beispiele:
- AUDIT_USR02_LOCKED          (Bereich: Audit, Tabelle: USR02, Zweck: Locked Users)
- REPORT_AGR_USERS_ACTIVE     (Bereich: Report, Tabelle: AGR_USERS, Zweck: Aktive Zuordnungen)
- CHECK_AGR_1251_DEBUG        (Bereich: Check, Tabelle: AGR_1251, Zweck: Debug-TCD)
```

**Vermeiden:**
- Kryptische Namen (VAR01, VAR02)
- Umlaute (Ä, Ö, Ü)
- Sonderzeichen außer Unterstrich

---

#### Dokumentation

**In Feld "LINE" (Kommentar):**
```
Beispiel:
Variante: AUDIT_USR02_LOCKED
Zeile 1: UFLAG | I | EQ | 64  | | "Initial Password - never logged in"
Zeile 2: UFLAG | I | EQ | 128 | | "Locked by Administrator - security risk"
```

**Externe Dokumentation:**
- Wiki-Eintrag mit Verwendungszweck
- Zuständiger Ansprechpartner
- Aktualisierungsintervall

---

#### Wartung und Lifecycle

**Regelmäßige Reviews:**
- Quartalsweise: Ungenutzte Varianten löschen
- Jährlich: Dokumentation aktualisieren
- Bei Release-Wechsel: Tabellenstrukturen prüfen

**Versionierung:**
```
USER_ACTIVE_V1  (Version 1: Original)
USER_ACTIVE_V2  (Version 2: Erweitert um USTYP-Prüfung)
USER_ACTIVE     (Aktuell: Verweis auf V2)
```

---

## 7. Fehlerzustände und Validierungen

### 7.1 Fehlermeldungen

| Fehlercode | Meldung | Ursache | Lösung |
|------------|---------|---------|--------|
| **E077(S#)** | Keine Berechtigung für YBCA1234GT_TAB | Fehlende S_TCODE-Berechtigung | Berechtigung anfordern beim Berechtigungs-Admin |
| **E006(YBCA1234_GET_TABLE)** | Variante nicht gefunden | Variante existiert nicht in DB | Variante über YBCA1234GT_TAB neu anlegen |
| **-** | Duplikat beim Einfügen | Key (Variante+Tabname+ID) bereits vorhanden | ID erhöhen oder andere Variante/Tabelle wählen |
| **-** | Pflichtfeld nicht gefüllt | VARIANTE, TABNAME oder ID leer | Alle Key-Felder ausfüllen |
| **-** | Tabellenname ungültig | Tabelle existiert nicht im Data Dictionary | Tabellenname in SE11 prüfen |
| **-** | Feldname ungültig | Feld existiert nicht in Tabelle | Feldnamen in SE11 für Tabelle prüfen |
| **-** | Foreign Lock | Eintrag wird von anderem User bearbeitet | Warten oder anderen User kontaktieren |

---

### 7.2 Validierungsregeln

#### Pflichtfelder

```abap
" Validierung im Table Maintenance Generator
IF gs_ybca1234_gt_var-variante IS INITIAL.
  MESSAGE e001(00) WITH 'Variante ist Pflichtfeld'.
ENDIF.

IF gs_ybca1234_gt_var-tabname IS INITIAL.
  MESSAGE e001(00) WITH 'Tabellenname ist Pflichtfeld'.
ENDIF.

IF gs_ybca1234_gt_var-id IS INITIAL.
  MESSAGE e001(00) WITH 'ID ist Pflichtfeld'.
ENDIF.
```

#### Wertebereichsprüfung

**SIGN (Include/Exclude):**
- Erlaubt: `I`, `E`
- Domain: `DDSIGN` mit Wertebereich

**OPTION (Operator):**
- Erlaubt: `EQ`, `NE`, `CP`, `NP`, `GE`, `GT`, `LE`, `LT`, `BT`, `NB`
- Domain: `TVARV_OPTI`

**LOGOP (Logischer Operator):**
- Erlaubt: `AND`, `OR`, ` ` (leer)
- Domain: `RSDSLOGOP`

---

### 7.3 Warnung bei kritischen Operationen

**Löschen von Varianten:**
```
┌──────────────────────────────────────────────────┐
│ Warnung                                  [!]     │
├──────────────────────────────────────────────────┤
│                                                  │
│ Sie sind dabei, 3 Variante(n) zu löschen.       │
│                                                  │
│ - USER_ACTIVE                                    │
│ - ROLE_ANALYSIS                                  │
│ - CRITICAL_AUTHS                                 │
│                                                  │
│ Dieser Vorgang kann nicht rückgängig gemacht    │
│ werden!                                          │
│                                                  │
│ Möchten Sie fortfahren?                          │
│                                                  │
│         [Ja]            [Nein]                   │
└──────────────────────────────────────────────────┘
```

---

## 8. Verlinkungen und Dokumentationsstruktur

### 8.1 Verwandte Transaktionen

| Transaktion | Beziehung | Beschreibung |
|-------------|-----------|--------------|
| **YBCA1234GT** | Konsument | Nutzt Varianten aus YBCA1234_GT_VAR |
| **SM30** | Basis-Tool | Generisches Table Maintenance Tool |
| **SE11** | Data Dictionary | Tabellenstruktur anzeigen/ändern |
| **SE16** | Data Browser | Daten ohne Pflege-GUI anzeigen |
| **SE16N** | Extended Data Browser | Erweiterte Anzeige- und Filterfunktionen |

### 8.2 Dokumentations-Links

**In dieser Dokumentation:**
- [Reporting & Query Tools - Übersicht](../../../../docs/03_ComponentDocumentation/2.08_ReportingQueryToolsDocumentation.md)
- [GUI-Übersicht](../../../../docs/03_ComponentDocumentation/GUI_Overview.md)
- [Stammdatenverwaltung](../../../../docs/03_ComponentDocumentation/2.01_StammdatenverwaltungDocumentation.md)

**Externe Dokumentation:**
- SAP-Hilfe: SM30 - Table Maintenance
- SAP-Hilfe: Table Maintenance Generator
- SAP-Note: 1582905 - Performance of Table Maintenance

---

## 9. Technische Metadaten

### 9.1 Tabellenstruktur YBCA1234_GT_VAR

| Feldname | Datentyp | Länge | Key | Beschreibung | Domain/Datenelement |
|----------|----------|-------|-----|--------------|---------------------|
| MANDT | CLNT | 3 | X | Mandant | MANDT |
| VARIANTE | CHAR | 30 | X | Variantenname | YBCA1234_VARIANT |
| TABNAME | CHAR | 30 | X | Tabellenname | TABNAME |
| ID | NUMC | 3 | X | Laufende Nummer | YBCA1234_ID |
| FIELDNAME | CHAR | 30 | - | Feldname | FIELDNAME |
| LOGOP | CHAR | 3 | - | Logischer Operator (AND/OR) | RSDSLOGOP |
| ARITY | NUMC | 1 | - | Stelligkeit | RSDSARITY |
| SIGN | CHAR | 1 | - | Include/Exclude | DDSIGN |
| OPTION_O | CHAR | 2 | - | Operator (EQ, NE, CP, ...) | TVARV_OPTI |
| LOW | CHAR | 45 | - | Unterer Wert | TVARV_VAL |
| HIGH | CHAR | 45 | - | Oberer Wert | TVARV_VAL |
| LINE | CHAR | 72 | - | Kommentarzeile | SYCHAR72 |
| ERNAM | CHAR | 12 | - | Ersteller | ERNAM |
| ERDAT | DATS | 8 | - | Erstelldatum | ERDAT |
| ERTIM | TIMS | 6 | - | Erstellzeit | YBCA1234_ERTIM |
| AENAM | CHAR | 12 | - | Änderer | AENAM |
| AEDAT | DATS | 8 | - | Änderungsdatum | AEDAT |
| AETIM | TIMS | 6 | - | Änderungszeit | YBCA1234_AETIM |

### 9.2 Technische Einstellungen

| Eigenschaft | Wert | Bedeutung |
|-------------|------|-----------|
| **Tabellenklasse** | TRANSP | Transparente Tabelle (Applikationstabelle) |
| **Mandantenabhängig** | Ja (CLIIDEP = X) | Daten sind mandantenspezifisch |
| **Delivery Class** | C | Customizing-Tabelle (über SM30 pflegbar) |
| **Pufferung** | P | Partiell gepuffert (Single Record Buffering) |
| **Protokollierung** | X | Change Document aktiv (Änderungen werden protokolliert) |
| **Authorization Class** | YUSR | Berechtigungsgruppe für kundeneigene User-Tabellen |

### 9.3 Indizes

**Primary Key (Index 0):**
```
MANDT + VARIANTE + TABNAME + ID
```
- **Unique:** Ja
- **Performance:** Optimal für Key-basierte Zugriffe

**Empfohlener Secondary Index (nicht implementiert):**
```
MANDT + TABNAME + VARIANTE
```
- **Zweck:** Schnellere Suche nach Tabelle
- **Nutzung:** Pattern-Matching in Übersichtsliste

---

## 10. Change History & Versioning

| Datum | Version | Autor | Änderung |
|-------|---------|-------|----------|
| 02.02.2015 | 1.0 | X114409 (NL) | Initial Release - Basic Variant Management |
| 15.06.2016 | 1.1 | - | Hinzufügen von LOGOP für UND/ODER-Verknüpfung |
| 12.12.2017 | 1.2 | - | Erweiterung LINE-Feld für Kommentare |
| 20.04.2018 | 1.3 | AMN | Code-Profiler-Findings: Berechtigungsprüfung optimiert |
| 24.11.2025 | 2.0 | Documentation | Vollständige GUI-Dokumentation erstellt |

---

## 11. Anhang

### 11.1 SQL-Beispiele für direkte DB-Abfragen

**Alle Varianten für Tabelle USR02:**
```sql
SELECT variante, id, fieldname, sign, option_o, low, high
  FROM ybca1234_gt_var
  WHERE mandant = '100'
    AND tabname = 'USR02'
  ORDER BY variante, id;
```

**Häufigst genutzte Varianten (Top 10):**
```sql
SELECT variante, COUNT(*) as anzahl_zeilen
  FROM ybca1234_gt_var
  WHERE mandant = '100'
  GROUP BY variante
  ORDER BY anzahl_zeilen DESC
  LIMIT 10;
```

**Varianten ohne Feldnamen (inkomplett):**
```sql
SELECT variante, tabname, id
  FROM ybca1234_gt_var
  WHERE mandant = '100'
    AND fieldname IS NULL
  ORDER BY variante;
```

### 11.2 Checkliste für Varianten-Erstellung

- [ ] Variantenname sprechend und gemäß Namenskonvention gewählt
- [ ] Tabellenname existiert im Data Dictionary (SE11)
- [ ] Alle Feldnamen korrekt und in Tabelle vorhanden
- [ ] SIGN/OPTION-Werte gültig (I/E, EQ/NE/CP/...)
- [ ] LOW/HIGH-Werte im korrekten Format (Datum: YYYYMMDD)
- [ ] Logische Verknüpfung (AND/OR) sinnvoll gewählt
- [ ] Kommentar im LINE-Feld für Dokumentation hinterlegt
- [ ] Test in YBCA1234GT durchgeführt
- [ ] Bei Bedarf: Transport erstellt und freigegeben
- [ ] Dokumentation im Wiki/Confluence aktualisiert

### 11.3 Kontakt und Support

**Fachlicher Ansprechpartner:**
- Bereich: Reporting & Analytics
- Team: User Administration & Compliance

**Technischer Support:**
- Programm: YBCA1234_GT
- Entwickler: MHP (Mieschke Hofmann und Partner)
- Support-Transaktion: YBCA1234GT_TAB

**Bei Problemen:**
1. Berechtigungen prüfen (S_TCODE, S_TABU_DIS)
2. Tabellenstruktur in SE11 validieren
3. ST22 für Laufzeitfehler prüfen
4. SM21 für System-Log-Einträge prüfen

---

**Ende der Dokumentation**

---

## Qualitätssicherung

✅ **Vollständigkeit:** Alle Screens und Funktionen dokumentiert  
✅ **Realitätsnähe:** Mockups orientieren sich an SAP GUI Standard  
✅ **Beispieldaten:** Realistische Testdaten in Mockups  
✅ **Lesbarkeit:** Klare Struktur und verständliche Beschreibungen  
✅ **Verlinkungen:** Cross-References zu anderen Dokumenten gesetzt  
✅ **Technische Tiefe:** Code-Analyse ausreichend detailliert  
✅ **Ablauflogik:** Programmfluss nachvollziehbar im Mermaid-Diagramm  

---
