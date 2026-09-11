# User Story Assessment Tool - Bewertungsverfahren

## 📋 Übersicht

Das User Story Assessment Tool bewertet User Stories nach einem strukturierten, punktebasierten Verfahren mit **4 Hauptkategorien** und **insgesamt 56 Punkten**. Das Tool unterstützt Teams dabei, die Qualität ihrer User Stories objektiv zu messen und systematisch zu verbessern.

**Version:** 1.1 (Kalibriert und vollständig entwickelt)  
**Letztes Update:** 17. September 2025  
**Entwicklungsstand:** Vollständig implementiert mit 4 Integrationsoptionen

### 🚀 Verfügbare Integrationen

Das Assessment-Tool ist in 4 verschiedenen Varianten verfügbar:

1. **GitHub Copilot Chat** - Für Entwickler mit GitHub Copilot
2. **GitHub Copilot Workspace** - Automatisierte Integration in VS Code
3. **Microsoft Copilot** - Für M365/Bing Copilot Nutzer  
4. **VS Code Snippets** - Lizenzfreie Templates für alle

---

## 🎯 Bewertungsframework im Detail

### **Gesamtpunktzahl: 56 Punkte**

Das Bewertungsverfahren gliedert sich in **4 Hauptkategorien** mit verschiedenen **Subkategorien**:

1. **INVEST-Kriterien** (26 Punkte)
2. **Format & Struktur** (7 Punkte)  
3. **Akzeptanzkriterien** (8 Punkte)
4. **Definition of Ready** (15 Punkte)

---

## 📊 Kategorie 1: INVEST-Kriterien (26 Punkte)

Die klassischen INVEST-Kriterien bilden das Herzstück der Bewertung:

### **I - Independent (4 Punkte)**
**Was wird bewertet:** Unabhängigkeit von anderen User Stories

**Punktvergabe:**
- **4 Punkte:** Story ist vollständig unabhängig, kann isoliert entwickelt werden
- **3 Punkte:** Minimale Abhängigkeiten, die leicht aufgelöst werden können
- **2 Punkte:** Moderate Abhängigkeiten, erfordern Koordination
- **1 Punkt:** Starke Abhängigkeiten, schwer isolierbar
- **0 Punkte:** Kann nicht ohne andere Stories umgesetzt werden

### **N - Negotiable (4 Punkte)**
**Was wird bewertet:** Verhandlungsspielraum in der Umsetzung

**Punktvergabe:**
- **4 Punkte:** Klare Ziele mit flexiblen Umsetzungsmöglichkeiten
- **3 Punkte:** Gute Balance zwischen Klarheit und Flexibilität
- **2 Punkte:** Einige verhandelbare Aspekte vorhanden
- **1 Punkt:** Wenig Spielraum für Verhandlungen
- **0 Punkte:** Zu detailliert spezifiziert oder zu vage

### **V - Valuable (5 Punkte)**
**Was wird bewertet:** Geschäftswert und Nutzen für den Anwender

**Punktvergabe:**
- **5 Punkte:** Klarer, messbarer Geschäftswert explizit beschrieben
- **4 Punkte:** Geschäftswert ist erkennbar und nachvollziehbar
- **3 Punkte:** Wert ist vorhanden, aber nicht optimal kommuniziert
- **2 Punkte:** Wert ist implizit, aber nicht klar ausgedrückt
- **1 Punkt:** Minimaler oder fraglicher Wert
- **0 Punkte:** Kein erkennbarer Geschäftswert

### **E - Estimable (4 Punkte)**
**Was wird bewertet:** Schätzbarkeit von Aufwand und Komplexität

**Punktvergabe:**
- **4 Punkte:** Umfang und Komplexität sind klar schätzbar
- **3 Punkte:** Gute Schätzbarkeit mit geringen Unsicherheiten
- **2 Punkte:** Schätzbar, aber mit höheren Unsicherheiten
- **1 Punkt:** Schwer schätzbar, viele Unbekannte
- **0 Punkte:** Nicht schätzbar ohne weitere Analyse

### **S - Small (4 Punkte)**
**Was wird bewertet:** Angemessene Größe für einen Sprint

**Punktvergabe:**
- **4 Punkte:** Optimal für 1 Sprint (1-5 Entwicklertage)
- **3 Punkte:** Passende Größe, leicht in einem Sprint umsetzbar
- **2 Punkte:** Grenzwertig, möglicherweise zu groß für einen Sprint
- **1 Punkt:** Definitiv zu groß, sollte aufgeteilt werden
- **0 Punkte:** Viel zu groß oder zu klein für praktische Umsetzung

### **T - Testable (5 Punkte)**
**Was wird bewertet:** Testbarkeit und Prüfbarkeit der Anforderungen

**Punktvergabe:**
- **5 Punkte:** Vollständig testbar mit klaren Erfolgs-/Fehlerkriterien
- **4 Punkte:** Gut testbar mit definierten Testkriterien
- **3 Punkte:** Testbar, aber Testkriterien könnten präziser sein
- **2 Punkte:** Eingeschränkt testbar, vage Erfolgskriterien
- **1 Punkt:** Schwer testbar, subjektive Bewertung erforderlich
- **0 Punkte:** Nicht testbar oder keine Testkriterien erkennbar

---

## 📝 Kategorie 2: Format & Struktur (7 Punkte)

### **Standard User Story Format (5 Punkte)**
**Was wird bewertet:** Einhaltung des "Als ... möchte ich ... damit ..." Formats

**Punktvergabe:**
- **5 Punkte:** Perfekte Struktur mit Rolle, Wunsch und Grund
- **4 Punkte:** Gute Struktur, kleinere Abweichungen
- **3 Punkte:** Grundstruktur erkennbar, aber unvollständig
- **2 Punkte:** Teilweise strukturiert, wichtige Elemente fehlen
- **1 Punkt:** Kaum erkennbare Struktur
- **0 Punkte:** Keine Standard-Struktur verwendet

### **Angemessene Länge (2 Punkte)**
**Was wird bewertet:** Prägnanz und Verständlichkeit

**Punktvergabe:**
- **2 Punkte:** Optimal: 1-3 Sätze, klar und prägnant
- **1 Punkt:** Akzeptabel: etwas zu lang oder zu kurz
- **0 Punkte:** Zu lang (>5 Sätze) oder zu kurz (<1 Satz)

---

## ✅ Kategorie 3: Akzeptanzkriterien (8 Punkte)

### **Given-When-Then Format (5 Punkte)**
**Was wird bewertet:** Verwendung des strukturierten GWT-Formats

**Punktvergabe:**
- **5 Punkte:** Alle Akzeptanzkriterien in korrektem GWT-Format
- **4 Punkte:** Meiste Kriterien in GWT-Format, wenige Ausnahmen
- **3 Punkte:** Teilweise GWT-Format, gemischte Ansätze
- **2 Punkte:** Erkennbare Struktur, aber nicht konsequent GWT
- **1 Punkt:** Wenig strukturierte Kriterien
- **0 Punkte:** Keine strukturierten Akzeptanzkriterien

### **Vollständigkeit der Kriterien (3 Punkte)**
**Was wird bewertet:** Abdeckung aller wichtigen Szenarien

**Punktvergabe:**
- **3 Punkte:** Alle wichtigen Szenarien (Happy Path, Edge Cases, Fehlerbehandlung)
- **2 Punkte:** Hauptszenarien abgedeckt, wenige Edge Cases fehlen
- **1 Punkt:** Grundlegende Szenarien, aber wichtige Aspekte fehlen
- **0 Punkte:** Unvollständige oder fehlende Akzeptanzkriterien

---

## 🎬 Kategorie 4: Definition of Ready (15 Punkte)

### **Klare Rolle/Persona (3 Punkte)**
**Was wird bewertet:** Spezifität und Klarheit der Zielgruppe

**Punktvergabe:**
- **3 Punkte:** Spezifische, gut definierte Rolle/Persona
- **2 Punkte:** Klare Rolle, könnte spezifischer sein
- **1 Punkt:** Vage oder generische Rollenbeschreibung
- **0 Punkte:** Keine oder unklare Rolle definiert

### **Business Value Explanation (4 Punkte)**
**Was wird bewertet:** Erklärung des Geschäftswerts

**Punktvergabe:**
- **4 Punkte:** Detaillierte Erklärung mit messbaren Vorteilen
- **3 Punkte:** Gute Erklärung des Business Value
- **2 Punkte:** Business Value erkennbar, aber oberflächlich
- **1 Punkt:** Schwache oder vage Value-Erklärung
- **0 Punkte:** Kein erkennbarer Business Value

### **Testability/DoD Criteria (5 Punkte)**
**Was wird bewertet:** Definition of Done und Testkriterien

**Punktvergabe:**
- **5 Punkte:** Umfassende DoD mit spezifischen Testkriterien
- **4 Punkte:** Gute DoD mit den meisten wichtigen Kriterien
- **3 Punkte:** Grundlegende DoD, aber unvollständig
- **2 Punkte:** Minimale DoD-Kriterien vorhanden
- **1 Punkt:** Vage oder unklare DoD
- **0 Punkte:** Keine Definition of Done

### **Dependencies Identified (3 Punkte)**
**Was wird bewertet:** Identifikation und Dokumentation von Abhängigkeiten

**Punktvergabe:**
- **3 Punkte:** Alle Abhängigkeiten identifiziert und dokumentiert
- **2 Punkte:** Wichtigste Abhängigkeiten bekannt
- **1 Punkt:** Einige Abhängigkeiten identifiziert
- **0 Punkte:** Abhängigkeiten nicht betrachtet oder unbekannt

---

## 🏆 Qualitätsstufen und Handlungsempfehlungen

### **Exzellent (45-56 Punkte) - 80-100%**
**Bewertung:** ✅ Ready for Development  
**Handlungsempfehlung:**
- Story ist bereit für die Entwicklung
- Kann direkt in den Sprint aufgenommen werden
- Eventuell als Referenz für andere Stories nutzen

### **Gut (34-44 Punkte) - 61-79%**
**Bewertung:** ⚠️ Kleinere Verbesserungen erforderlich  
**Handlungsempfehlung:**
- Wenige, spezifische Verbesserungen vor Sprint-Aufnahme
- Fokus auf schwächste Bereiche (niedrigste Punktzahlen)
- Kurze Refinement-Session ausreichend

### **Ausreichend (22-33 Punkte) - 39-60%**
**Bewertung:** 🔄 Überarbeitung erforderlich  
**Handlungsempfehlung:**
- Umfassende Überarbeitung vor Entwicklung notwendig
- Product Owner und Team sollten gemeinsam refinieren
- Zusätzliche Stakeholder-Inputs einholen
- Nicht für nächsten Sprint geeignet

### **Unzureichend (0-21 Punkte) - 0-38%**
**Bewertung:** ❌ Komplett neu schreiben  
**Handlungsempfehlung:**
- Story von Grund auf neu erstellen
- Requirements-Engineering-Session einplanen
- Stakeholder-Workshop zur Klärung der Anforderungen
- Eventuell Epic aufteilen oder Scope überdenken

---

## 🔧 Anwendung des Bewertungsverfahrens

### **Bewertungsprozess:**

1. **Story analysieren:** Alle 4 Kategorien durchgehen
2. **Punkte vergeben:** Pro Subkategorie entsprechend den Kriterien
3. **Gesamtpunktzahl berechnen:** Summe aller Teilpunkte (max. 56)
4. **Qualitätsstufe bestimmen:** Einordnung in eine der 4 Stufen
5. **Handlungsempfehlung ableiten:** Nächste Schritte definieren

### **Einsatzgebiete:**

- **Sprint Planning:** Qualitätskontrolle vor Sprint-Aufnahme
- **Backlog Refinement:** Systematische Verbesserung der Stories
- **Team-Onboarding:** Schulung für konsistente Story-Qualität
- **Qualitätsmetriken:** Tracking der Story-Qualität über Zeit
- **Review-Prozesse:** Objektive Bewertung in Story-Reviews

---

## 📈 Kalibrierung und Kontinuierliche Verbesserung

Das Bewertungsverfahren wurde basierend auf praktischen Tests kalibriert und wird kontinuierlich verfeinert:

### 🎯 Kalibrierte Bewertungsregeln (v1.1)

#### **Häufige Bewertungsfehler vermeiden:**

**1. Story-Größe konservativ bewerten (INVEST-Small)**
- ❌ **Fehler**: Multi-Feature Stories als "grenzwertig machbar" bewerten
- ✅ **Korrektur**: Mehr als ein Feature = automatisch max 2/4 Punkte
- ✅ **Faustregel**: Bei Zweifel konservativer bewerten und Aufspaltung empfehlen

**2. Akzeptanzkriterien von Unit Tests abgrenzen**
- ❌ **Fehler**: Technische Tests mit Business-Akzeptanzkriterien gleichsetzen
- ✅ **Unit Tests**: Technische Testabdeckung (gehört in DoD)
- ✅ **Akzeptanzkriterien**: Business-testbare Given-When-Then Szenarien

**3. Konsistenz zwischen INVEST-Testable und DoR-Testkriterien**
- ✅ **Regel**: Beide Kategorien sollten ähnliche Scores haben
- ✅ **Bei Inkonsistenz**: Den niedrigeren Score für beide verwenden

**4. Keine technischen Details in User Stories tolerieren**
- ❌ **Fehler**: Implementation Details als "verhandelbar" bewerten
- ✅ **Regel**: Jede Code-Referenz = Abzug bei Negotiable
- ✅ **Format**: Technische Details = automatisch 0 Punkte für Länge

#### **Verschärfte INVEST-Standards:**

**Small (4 Punkte) - STRENGE Bewertung:**
- **4 Punkte**: Ein klar abgegrenztes Feature, 1-2 Tage Arbeit
- **3 Punkte**: Ein Feature, 3-5 Tage Arbeit
- **2 Punkte**: Ein komplexeres Feature oder zwei sehr kleine Features
- **1 Punkt**: Mehrere Features oder Epic-Charakter erkennbar
- **0 Punkte**: Definitiv Epic-Level, mehrere Sprints erforderlich

**Testable (5 Punkte) - Präzise Abgrenzung:**
- **5 Punkte**: Vollständige Given-When-Then Kriterien für alle Szenarien
- **4 Punkte**: Given-When-Then für Hauptszenario + wichtigste Edge Cases
- **3 Punkte**: Grundlegende Given-When-Then Struktur vorhanden
- **2 Punkte**: Wenige strukturierte Testkriterien
- **1 Punkt**: Vage oder unstrukturierte Testkriterien
- **0 Punkte**: Keine messbaren Testkriterien

### 📊 Bewertungsstatistiken
- **Testbasis:** Bewertung verschiedener realer User Stories
- **Validierung:** Abgleich mit tatsächlichen Entwicklungsergebnissen
- **Anpassung:** Punkteverteilung basierend auf Team-Feedback
- **Evolution:** Kontinuierliche Optimierung basierend auf praktischer Anwendung

---

## 🛠️ Tool-Integration und Anwendung

### **Empfohlene Integration nach Team-Setup:**

1. **Entwicklungsteams mit GitHub Copilot:**
   - Nutzen Sie `copilot-integration/copilot-chat-instructions.md`
   - Direkter Chat-Prompt für sofortige Bewertung

2. **Teams mit Microsoft 365:**
   - Nutzen Sie `microsoft-copilot-integration/microsoft-copilot-prompt.md`
   - Integration in bestehende M365-Workflows

3. **VS Code Teams (lizenzfrei):**
   - Nutzen Sie `vscode-snippets/user-story-snippets.json`
   - Template-basierte Erstellung und Bewertung

4. **Vollautomatisierte Workflows:**
   - Nutzen Sie `copilot-integration/copilot-instructions-workspace.md`
   - Automatische Integration in VS Code Workspace

---

**Tool-Version:** 1.1 (Vollständig entwickelt und kalibriert)  
**Dokumentations-Stand:** 17. September 2025  
**Entwicklungsstatus:** Produktionsreif mit 4 Integrationsoptionen  
**Nächste Review:** Nach 100 bewerteten Stories oder 6 Monaten  

### 📚 Weitere Dokumentation

- **Hauptdokumentation:** `README.md` - Übersicht aller 4 Integrationsoptionen
- **Quick-Start:** `QUICK-START.md` - 2-Minuten Setup für sofortige Nutzung
- **Team-Setup:** `TEAM-SETUP-GUIDE.md` - Detailliertes Team-Onboarding
- **Rollout-Checklist:** `TEAM-ROLLOUT-CHECKLIST.md` - Schritt-für-Schritt Implementation
- **Testdaten:** `Testdaten/` - Beispiel User Stories für Training
