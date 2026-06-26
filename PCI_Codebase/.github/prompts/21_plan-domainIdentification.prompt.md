# Plan: Domain-Identifikation und Transformationsstrategie für ZBK-System

Basierend auf Domain Driven Design werden Bounded Contexts in der ZBK-Berechtigungsadministration identifiziert, deren Abhängigkeiten analysiert und eine Strangler-Fig-Transformationsstrategie entwickelt.

Verwende sequential thinking mit mcp-server. Wenn der Auftrag zu groß ist, unterteile ihn in sinnvolle Schritte.

## Steps

### 1. Domänen-Identifikation nach DDD-Prinzipien

**Analysiere existierende Komponentendokumentation** aus `docs/01_SystemSummary.md` und `docs/SystemComponents.csv`, um fachliche Domänen nach DDD-Prinzipien zu identifizieren.

**Aufgabe:**

- Gruppiere die 10 technischen Pakete und 30+ Komponenten in 5-8 Bounded Contexts
- Basiere Gruppierung auf:
  - Geschäftsfähigkeiten (Business Capabilities)
  - Ubiquitous Language (Fachsprache je Domäne)
  - Fachlicher Kohäsion und Kopplung
  - Organisatorischen Verantwortlichkeiten

**Zu berücksichtigende Pakete:**

- `adm/` - Berechtigungsadministration (Audit, Logging, Exceptions, SNC, Stammdaten)
- `adm_40/` - Xiting Times Integration
- `usr/` - Benutzerverwaltung (User Maintenance, Role Assignment, Person in Charge)
- `upd/` - Upload/Download-Funktionen (Synchronization, HR Mapping, Role Management)
- `hr/` - HR-spezifische Anwendungen
- `nash/` - Nashcon Integration
- `pack/` - Transport-Management
- `wl/` - Workload-Monitoring
- `archiv/` - Archivierung
- SAP-Standard als eigene Domain(s)

Vermeide aber die Pakete zu lesen - nutze nur die Dokumentation im Ordner 'docs\03_ComponentDocumentation'.

**Erwartetes Ergebnis:**

- Liste von 5-8 identifizierten Domänen mit:
  - Domänenname
  - Geschäftszweck und Verantwortlichkeit
  - Enthaltene Komponenten/Pakete
  - Ubiquitous Language (Kernbegriffe)
  - Domänentyp (Core, Supporting, Generic)

---

### 2. Integrationspunkte und Abhängigkeiten

**Untersuche Integrationspunkte** zwischen Domänen durch Analyse von RFC-Schnittstellen, Datenbankzugriffen und Funktionsaufrufen.

**Aufgabe:**

- Analysiere RFC-Schnittstellen aus `5.01_SynchronizationDocumentation.md`
- Analysiere HR-Mappings aus `5.02_HRMappingDocumentation.md`
- Identifiziere cross-cutting concerns aus `05_Rework_with_docs.md`
- Erstelle Abhängigkeitsmatrix mit Context Maps

**Zu untersuchende Integrationsmuster:**

- **Upstream/Downstream**: Welche Domäne ist führend?
- **Shared Kernel**: Gemeinsam genutzte Daten/Logik
- **Anti-Corruption Layer (ACL)**: Erforderliche Übersetzungsschichten
- **Conformist**: Abhängigkeiten von SAP-Standard
- **Open Host Service**: RFC-Schnittstellen als öffentliche APIs
- **Published Language**: Datenformate (BAPI, IDoc, etc.)

**Zu identifizierende Abhängigkeiten:**

- Datenbankzugriffe auf gemeinsame Tabellen (USR*, AGR*, YBCA1234\_\*)
- RFC-Aufrufe zwischen Komponenten
- BAPI-Nutzung (BAPI*USER*_, BAPI*ACTGROUPS*_)
- HR-Infotype-Zugriffe (PA0001, PA0105)
- Change Document Integration (CDHDR, CDPOS)

**Erwartetes Ergebnis:**

- Abhängigkeitsmatrix: Domäne A → Domäne B (Art der Integration)
- Context Map mit Strategic Design Patterns
- Identifikation von Core Domain, Supporting Subdomains, Generic Subdomains

---

### 3. Visualisierung der Domänenarchitektur

**Visualisiere Domänenarchitektur** mit Mermaid-Diagrammen.

**Aufgabe:**
Erstelle folgende Diagramme in Mermaid-Syntax:

1. **Bounded Context Übersicht**

   - Alle identifizierten Domänen als Boxen
   - Gruppierung nach Domänentyp (Core/Supporting/Generic)
   - SAP-Standard als separate externe Domäne

2. **Domain-Abhängigkeitsgraph**

   - Gerichtete Kanten zwischen Domänen
   - Beschriftung mit Integrationstyp (RFC, DB, BAPI)
   - Stärke der Kopplung (stark/mittel/schwach)

3. **Context Map mit Strategic Patterns**

   - Upstream/Downstream-Beziehungen
   - ACL-Pattern-Anwendungen
   - Shared Kernel Bereiche
   - Open Host Services

4. **SAP-Standard Subdomain-Struktur**
   - BC-SEC-USR (User Management)
   - PA (Personnel Administration)
   - PFCG (Role Maintenance)
   - Weitere relevante Module

**Erwartetes Ergebnis:**

- 3-4 Mermaid-Diagramme mit Beschreibung
- Legende für verwendete Symbole und Patterns

---

### 4. Strangler-Fig-Transformationsstrategie

**Entwickle Strangler-Fig-Transformationsstrategie** in 4-6 Schritten.

**Aufgabe:**
Definiere eine schrittweise Migrationsstrategie mit folgenden Kriterien:

**Priorisierungsfaktoren:**

1. **Geschäftswert**: Welche Domäne bringt den größten Business Value?
2. **Technische Unabhängigkeit**: Welche Domäne hat die wenigsten Abhängigkeiten?
3. **Migrationsrisiko**: Welche Domäne birgt das geringste Risiko?
4. **Team-Fähigkeiten**: Welche Domäne kann das Team am besten umsetzen?
5. **Time-to-Market**: Welche Domäne liefert schnell sichtbare Ergebnisse?

**Transformationsschritte (3-5 Iterationen):**

Für jeden Schritt definiere:

- **Schritt-Nummer und Name**
- **Zu migrierende Domäne(n)**
- **Begründung der Reihenfolge**
- **Neue Service-Grenzen** (Microservices/Bounded Contexts)
- **Notwendige Anti-Corruption-Layer**
- **Datenmigrationssstrategie** (Strangler Pattern für Daten)
- **Rückfall-Mechanismen** (Fallback zum Legacy-System)
- **Erfolgs-Metriken** (Definition of Done für diesen Schritt)
- **Risiken und Mitigation**
- **Geschätzter Aufwand**

**Beispiel-Struktur:**

```
Schritt 1: Foundation & Reporting Layer
- Domänen: Reporting/Analytics, Archiving
- Begründung: Geringe Abhängigkeiten, Read-Only-Zugriffe
- Service-Architektur: Event-Driven Read Models
- ACL: Event-Streaming von Legacy Change Documents
- Dauer: 3-4 Monate

Schritt 2: [...]
```

**Erwartetes Ergebnis:**

- 3-5 definierte Transformationsschritte
- Roadmap-Visualisierung (Gantt-ähnlich mit Mermaid)
- Risikobewertung pro Schritt
- Gesamtaufwandsschätzung

---

### 5. Dokumentation der Ergebnisse

**Dokumentiere Ergebnisse** in `docs/21_Domains/DomainAnalysis.md`.

**Aufgabe:**
Erstelle vollständige Dokumentation gemäß `.github/instructions/create_documentation.instructions.md`.

**Dokumentstruktur:**

```markdown
# Domain-Analyse und Transformationsstrategie: ZBK-System

## Inhaltsverzeichnis

[Automatisch generiert]

## 1. Executive Summary

- Überblick über identifizierte Domänen
- Wichtigste Abhängigkeiten
- Empfohlene Transformationsstrategie
- Erwarteter Geschäftswert

## 2. Domain Driven Design Grundlagen

- Bounded Context Konzept
- Ubiquitous Language
- Context Mapping Patterns
- Angewandt auf ZBK-System

## 3. Identifizierte Domänen

Für jede Domäne:

- 3.1 [Domänenname]
  - Geschäftszweck
  - Verantwortlichkeiten
  - Enthaltene Komponenten
  - Ubiquitous Language
  - Domänentyp (Core/Supporting/Generic)
  - Schnittstellen (Inputs/Outputs)

## 4. Domänen-Abhängigkeiten

- 4.1 Abhängigkeitsmatrix
- 4.2 Context Map
- 4.3 Integrationsmuster
- 4.4 Shared Kernel Analyse
- 4.5 SAP-Standard als Upstream-Domäne

## 5. Visualisierungen

- 5.1 Bounded Context Diagramm
- 5.2 Abhängigkeitsgraph
- 5.3 Context Map
- 5.4 SAP-Standard Integration

## 6. Strangler-Fig-Transformationsstrategie

- 6.1 Strategische Übersicht
- 6.2 Priorisierungskriterien
- 6.3 Transformationsschritte (detailliert)
- 6.4 Transformations-Roadmap (Visualisierung)
- 6.5 Risikomanagement
- 6.6 Aufwandsschätzung

## 7. Technische Umsetzungsempfehlungen

- 7.1 Anti-Corruption Layer Patterns
- 7.2 Event-Driven Architecture für Legacy-Integration
- 7.3 Datenmigrationsstrategien
- 7.4 Testing-Strategie für Strangler Pattern
- 7.5 Deployment-Strategie (Blue-Green, Canary)

## 8. Anhang

- 8.1 Glossar (Ubiquitous Language pro Domäne)
- 8.2 Referenzen zu Komponentendokumentation
- 8.3 Literatur und Best Practices
```

**Qualitätskriterien:**

- ✅ Deutsche Sprache
- ✅ Mermaid-Diagramme (keine anderen Diagrammformate)
- ✅ Keine Annahmen ohne Quellenverifikation
- ✅ Referenzen zu existierender Dokumentation
- ✅ Inhaltsverzeichnis bis Level 2
- ✅ Markdown-Formatierung

**Erwartetes Ergebnis:**

- Vollständige Dokumentation in `docs/21_Domains/DomainAnalysis.md`
- 5-10 Seiten umfassende Analyse
- 4-6 Mermaid-Diagramme
- Actionable Transformationsstrategie

---

## Further Considerations

### 1. SAP-Standard-Granularität

**Fragestellung:**
Soll SAP-Standard als monolithische Domain oder aufgeteilt nach Modulen (BC-SEC-USR, PA, PFCG) betrachtet werden?

**Empfehlung:**

- **Aufteilung nach Subdomänen** für präzisere Abhängigkeitsanalyse
- Struktur:
  ```
  SAP-Standard (Upstream-Domäne)
  ├── BC-SEC-USR (User Management)
  │   ├── User Master (USR01, USR02)
  │   ├── Authorization Profiles (USR10, UST04)
  │   └── Change Documents (CDHDR, CDPOS)
  ├── PA (Personnel Administration)
  │   ├── Infotypes (PA0001, PA0105)
  │   └── HR Master Data
  └── PFCG (Role Management)
      ├── Role Definitions (AGR_DEFINE)
      ├── Role Assignments (AGR_USERS)
      └── Profile Mappings (AGR_1016)
  ```
- Ermöglicht differenzierte ACL-Strategie pro SAP-Modul

### 2. Migrationssequenz

**Fragestellung:**
Big-Bang für eng gekoppelte Domänen oder strikte Strangler-Sequenz?

**Empfehlung:**

- **Strikte Strangler-Sequenz** mit temporären Adapter-Patterns
- Beginne mit am wenigsten integrierten Domänen:
  1. **Reporting & Analytics** (Read-Only, Event-Sourcing von Change Documents)
  2. **Archiving** (Asynchrone Verarbeitung, geringe Echtzeit-Anforderungen)
  3. **Workload Monitoring** (Standalone-Komponente mit Event Collection)
  4. **Exception Management** (Moderate Integration, klar abgegrenzt)
  5. **Role & User Maintenance** (Core Domain, erst nach Infrastruktur-Migration)
- Vermeide Big-Bang auch bei eng gekoppelten Domänen:
  - Nutze Feature Toggles für schrittweise Aktivierung
  - Implementiere Shadow Mode (Parallel-Betrieb mit Ergebnisvergleich)
  - Baue Rollback-Mechanismen ein (Feature-Flag-basiert)

### 3. Datenhoheit und Event-Sourcing

**Zusätzliche Überlegung:**

- **Frage:** Welche Domäne besitzt welche Daten in der Zielarchitektur?
- **Empfehlung:**
  - User Domain: Eigentümer von Benutzerstammdaten (unabhängig von SAP USR\*)
  - Role Domain: Eigentümer von Rollendefinitionen und -zuordnungen
  - Audit Domain: Event Store für alle Änderungen (Event-Sourcing)
  - HR Domain: Konsument von HR-Events (nicht Eigentümer, da externes System)
- **Pattern:** Event-Driven Architecture mit Domain Events
  - UserCreated, UserModified, RoleAssigned, etc.
  - Ermöglicht Audit-Trail "by design"
  - Unterstützt CQRS für Reporting-Domäne

### 4. Technologie-Stack für neue Services

**Zusätzliche Überlegung:**

- **Frage:** Welche Technologien für neue Microservices?
- **Zu berücksichtigende Faktoren:**
  - SAP RAP/ABAP RESTful Services für nahtlose SAP-Integration
  - SAP CAP in BTP
- **Empfehlung:** In Dokumentation als Diskussionspunkt aufnehmen, aber keine finale Entscheidung treffen (nicht Scope dieser Analyse). Es ist auch ein hybrider Ansatz denkbar, je nach Domäne unterschiedliche Technologien zu nutzen.
