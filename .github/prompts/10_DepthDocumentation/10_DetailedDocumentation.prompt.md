---
mode: agent
---

@workspace Erzeuge eine Dokumentation zum Sub-Modul <Thema>.
File "<Thema>01_SystemSummary.md" im "docs/20*DetailierteDokumentation" Ordner ab.
Erzeuge einen Verweis darauf in der "<Komponentennummer>*<Komponente>Documentation.md" im entsprechenden Kapitel.

**Hinweise zu den Modulen <Komponente>:**
Lese aus "<Komponentennummer>\_<Komponente>Documentation.md" heraus in welchen ABAP-Paketen sich die Hauptinformationen zum <Thema> befinden und durchsuche den ABAP-Code in diesen Paketen zum <Thema>. Wenn nötig, dann identifiziere DB-Tabellen und der Verknüpfungen untereinander.
Zur <Thema> beschreibe relevante Subprozesse und deren Ablauf.

**Dialoge und GUI-Komponenten:**
Identifiziere die Dialoge und GUI-Komponenten, die im Rahmen der <Thema> verwendet werden.

**Formulare:**
Identifiziere die Formulare (Smartforms, Adobe Forms, SAP Scripts), die im Rahmen der <Thema> verwendet werden.

**Schnittstellen:**
Identifiziere die Schnittstellen, die im Rahmen der <Thema> verwendet werden.

**Stammdaten:**
Identifiziere die Stammdaten, die im Rahmen der <Thema> verwendet werden.

**Benachbarte Prozesse:**
Identifiziere benachbarte Prozesse, die mit der <Thema> in Verbindung stehen und erstelle jeweils Querverweise in den relevanten Dokumentationen.

**Abhängigkeiten:**
Identifiziere Abhängigkeiten zu anderen Komponenten und erstelle jeweils einen Tabelleneintrag im Dokument docs/11_Abhängigkeiten.csv: <Komponente Sender>, <Komponente Empfänger>, <Abhängigkeitstyp>, <relevanter Prozess der Abhängigkeit>, wobei <Komponente Sender> oder <Komponente Empfänger> die aktuelle Komponente ist. Im Prozess muss <Thema> auftauchen.
