# Klon sklepu **miedzydrutami.pl**

## Opis projektu

Projekt stanowi klon sklepu internetowego **miedzydrutami.pl** zrealizowany przy użyciu **PrestaShop 1.7.8** oraz **MySQL 5.7**. W projekcie wykorzystano skrypty w Pythonie do scrapowania produktów oraz ich importu do sklepu.

## Wykorzystane technologie

- **PrestaShop**: 1.7.8
- **MySQL**: 5.7
- **Python**: Skrypty do scrapowania i wgrywania produktów
- **Docker**: Zarządzanie środowiskiem aplikacji
- **Docker Compose**: Uruchamianie i budowanie aplikacji

## Sposób uruchomienia

Aby uruchomić projekt, wykonaj poniższe kroki:

1. Sklonuj repozytorium:
   ```bash
   git clone <url-repozytorium>
   cd <nazwa-folderu>
   ```

2. Uruchom aplikację przy pomocy Docker Compose:
   ```bash
   docker-compose up
   ```

3. Jeśli potrzebujesz zrestartować aplikację lub odświeżyć kontenery:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

4. Aplikacja powinna być dostępna pod adresem:
   ```
   https://localhost:433
   ```

## Skład zespołu

Projekt został zrealizowany przez zespół:

- **Marcin Bajkowski** (193696)
- **Maciej Krysiak** (193463)
- **Jakub Kobyliński** (193618)
- **Stanisław Lemański** (193333)

## Uwagi

- Pliki ze skryptami Python znajdują się w katalogu scraper.
- Dane scrapowane są przechowywane w bazie MySQL i ładowane do PrestaShop oraz są dostepne w katalogu scraper-data.
- Upewnij się, że masz zainstalowane **Docker**, **Docker Compose** i **Python** na swoim środowisku przed uruchomieniem projektu.

