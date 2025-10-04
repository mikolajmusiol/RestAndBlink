# 🚀 Project Overtake: Predykcyjny Doradca Mobilności

## "Przestań reagować na opóźnienia. Zacznij je wyprzedzać."

**Project Overtake** to kompleksowe rozwiązanie do **Inteligentnego Zarządzania Informacją Pasażerską (PIM)**, które przechodzi od historycznego informowania o opóźnieniach do **predykcyjnej optymalizacji trasy** w czasie rzeczywistym. Naszym celem jest likwidacja "silosów danych" w transporcie publicznym i dostarczenie pasażerom **Wiedzy Absolutnej**, umożliwiającej świadome i natychmiastowe decyzje.

---

## 🎯 Problem & Wizja

### 🧐 Problem
Miliony pasażerów codziennie tracą czas z powodu:
1.  **Reaktywnego** informowania (komunikat jest opóźniony względem zdarzenia).
2.  **Fragmentaryczności** danych (różne systemy przewoźników nie komunikują się).
3.  **Braku Predykcji** (brak informacji, jak opóźnienie wpłynie na kolejne przesiadki).

### ✨ Wizja
Stworzenie **Jednolitego Inteligentnego Centrum Danych Transportowych (JICDT)**, które agreguje, normalizuje i przetwarza dane w czasie rzeczywistym, generując nie tylko **Estymowany Czas Przyjazdu (ETA)**, ale również **Optymalne Alternatywne Plany (OAP)**.

---

## 🧠 Mechanizm Działania: Architektura JICDT

### 1. Agregacja i Normalizacja Danych (Real-Time Fusion)

JICDT działa jako centralny broker danych, przyjmując strumienie z różnorodnych źródeł:
* **GPS/AVL:** Pozycja, prędkość i faktyczne opóźnienie pojazdów.
* **IoT & Infrastruktura:** Stan torów, sygnalizacji, zasilania (sensory predykcyjnego utrzymania ruchu).
* **Zdarzenia Operacyjne:** Ręczne zgłoszenia dyspozytorów i zmiany w rozkładzie.
* **Crowdsourcing:** Anonimowe dane o zagęszczeniu pasażerów w punktach transferowych.

**Standard:** Wszystkie dane są ujednolicane do formatu **GTFS Realtime (GTFS-RT)**, co gwarantuje interoperacyjność.

### 2. Analityka Predykcyjna (AI/ML Core)

Sercem systemu jest model Uczenia Maszynowego, który oblicza dynamiczne opóźnienie:

$$\Delta t_{\text{opóźnienia}}(k) = f_{\text{ML}}(\mathbf{X}_k, \mathbf{H})$$

| Zmienna | Opis |
| :--- | :--- |
| $\Delta t$ | Prognozowany wzrost/spadek opóźnienia na odcinku $k$. |
| $\mathbf{X}_k$ | Wektor cech w czasie rzeczywistym (pogoda, awarie, zagęszczenie). |
| $\mathbf{H}$ | Historyczne dane opóźnień w podobnych warunkach (pamięć systemowa). |
| $f_{\text{ML}}$ | Model regresji trenowany na minimalizację błędu prognozy ETA. |

#### Wynik: Precyzyjne ETA

Finalne $\text{ETA}_{\text{prognozowane}}$ jest obliczane nie na podstawie rozkładu, ale na podstawie dynamicznej symulacji uwzględniającej rozprzestrzenianie się zakłócenia (Ripple Effect).

### 3. Generowanie OAP (The Overtake Advisor)

Dla każdej zagrożonej trasy pasażera, system generuje zbiór alternatyw $A$:

$$\text{OAP} = \min_{a \in A} \left( \text{ETA}_{\text{prognozowane}}(j)_a \right) \text{, gdzie } \sum \text{Dystans Pieszy} < \text{Dystans Maks.}$$

System wybiera najszybszą opcję, jednocześnie minimalizując nieakceptowalny (dla pasażera) dystans pieszy.

---

## 💻 Interfejs Użytkownika (Pasażer)

Wiedza jest dostarczana proaktywnie, a nie na żądanie:

1.  **Powiadomienia Proaktywne:** Pasażer otrzymuje alert na 10 minut przed konieczną zmianą decyzji (np. przed wyjściem z domu, lub na stacji przesiadkowej).
    > ⚠️ **ALERT!** Twoja planowana przesiadka (Metro M1) jest zagrożona (spóźnienie 15 minut). **Zalecana Akcja:** Zejdź 400m na przystanek Autobusowy 123. Oszczędzasz 12 minut.
2.  **Wizualizacja Wpływu:** Zamiast suchego komunikatu, pasażer widzi swoją trasę: **ORYGINALNA (10:30) vs. ZALECANA (10:18)**.
3.  **Mapa Ciepła Zakłóceń:** Dynamiczne renderowanie sieci, gdzie opóźnienia są wizualizowane jako strefy wysokiego ryzyka (czerwone/pomarańczowe), pozwalając pasażerowi "wyczuć" problematyczne obszary.

---

## 🤝 Integracja i Współpraca

Project Overtake dostarcza **API** oparte na GTFS-RT, umożliwiające łatwą integrację z istniejącymi aplikacjami mobilnymi, systemami biletowymi i tablicami informacyjnymi.

**Szukamy:**
* **Przewoźników** chętnych do udostępniania danych w czasie rzeczywistym.
* **Miast/Regionów** gotowych do wdrożenia predykcyjnych modeli mobilności.
* **Deweloperów** chcących wzbogacić swoje aplikacje o wiedzę predykcyjną.

> **Project Overtake.** Twoja mobilność jest zbyt ważna, by polegać na zgadywaniu.
