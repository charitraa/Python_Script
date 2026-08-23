# Python Scripts

A daily-growing collection of Python scripts, generated automatically by the [Gemini API](https://ai.google.dev/) and organized by category.

Every day a GitHub Action picks the next topic from [`topics.txt`](topics.txt), asks Gemini to write a complete, beginner-friendly script for it, saves it under the matching category folder, and updates the list below.

## How it works

1. `.github/workflows/daily.yml` runs on a daily schedule (and can be triggered manually).
2. `generator/generate_script.py` reads the next unused topic from `topics.txt`, builds a prompt from `prompts/python_prompt.txt`, and calls the Gemini API.
3. The generated script is saved as `<Category>/<date>_<topic>.py`.
4. The topic is recorded in `generator/used_topics.txt` so it's never repeated.
5. This README is updated automatically and the change is committed and pushed.

## Categories

Generated scripts land in one of these:

`Automation` `API` `Web` `AI` `CLI` `Utilities` `File` `Image` `Networking` `Database` `Security` `DataScience` `Games` `Projects`

Two folders sit outside that rotation:

- `Learning/` — hand-written practice files and language notes, not generated.
- `assets/` — images, SVGs and JS data files used or produced by the scripts in `Image/`.

## Hand-written scripts

| Script | What it does |
| --- | --- |
| [`Image/ascii_svg.py`](Image/ascii_svg.py) | Converts an image to ASCII art and saves a self-typing animated SVG |
| [`Image/silhouette_js.py`](Image/silhouette_js.py) | Samples an image into a flat JS coordinate array for canvas reveal animations |
| [`Image/ImageCompressor.py`](Image/ImageCompressor.py) | Threaded bulk image compressor |
| [`Image/image_download.py`](Image/image_download.py) | Downloads every image URL in a JSON payload |
| [`Image/decode_sctx.py`](Image/decode_sctx.py) | Decodes Supercell SCTX sprite textures to PNG |
| [`Image/decode_si.py`](Image/decode_si.py) | Decodes Supercell `.si` binary vector files to SVG |
| [`Networking/fileserver.py`](Networking/fileserver.py) | LAN file server for browsing and downloading over the local network |
| [`File/read_file_name.py`](File/read_file_name.py) | Prints the file names inside a folder as asset path entries |
| [`File/remove_webp_image.py`](File/remove_webp_image.py) | Recursively deletes `.webp` files from a folder tree |
| [`Utilities/unicode_to_preeti.py`](Utilities/unicode_to_preeti.py) | Converts DOCX text between Unicode and Preeti encodings |

## Latest Scripts

<!-- LATEST_SCRIPTS_START -->
- 2026-08-23 — **Directory Tree Printer** (File) — [2026-08-23_directory_tree_printer.py](File/2026-08-23_directory_tree_printer.py)
- 2026-08-22 — **Automated Backup Script** (Automation) — [2026-08-22_automated_backup_script.py](Automation/2026-08-22_automated_backup_script.py)
- 2026-08-20 — **Email Sender** (Automation) — [2026-08-20_email_sender.py](Automation/2026-08-20_email_sender.py)
- 2026-08-19 — **Simple Web Scraper** (Web) — [2026-08-19_simple_web_scraper.py](Web/2026-08-19_simple_web_scraper.py)
- 2026-08-18 — **Website Uptime Checker** (Web) — [2026-08-18_website_uptime_checker.py](Web/2026-08-18_website_uptime_checker.py)
- 2026-08-17 — **Currency Converter** (API) — [2026-08-17_currency_converter.py](API/2026-08-17_currency_converter.py)
- 2026-08-15 — **Simple HTTP Server** (Networking) — [2026-08-15_simple_http_server.py](Networking/2026-08-15_simple_http_server.py)
- 2026-08-14 — **Port Scanner** (Networking) — [2026-08-14_port_scanner.py](Networking/2026-08-14_port_scanner.py)
- 2026-08-13 — **Bulk File Renamer** (Automation) — [2026-08-13_bulk_file_renamer.py](Automation/2026-08-13_bulk_file_renamer.py)
- 2026-08-12 — **Clipboard Manager** (Automation) — [2026-08-12_clipboard_manager.py](Automation/2026-08-12_clipboard_manager.py)
- 2026-08-11 — **Duplicate File Finder** (File) — [2026-08-11_duplicate_file_finder.py](File/2026-08-11_duplicate_file_finder.py)
- 2026-08-10 — **File Organizer by Extension** (File) — [2026-08-10_file_organizer_by_extension.py](File/2026-08-10_file_organizer_by_extension.py)
- 2026-08-10 — **CSV Reader and Analyzer** (File) — [2026-08-10_csv_reader_and_analyzer.py](File/2026-08-10_csv_reader_and_analyzer.py)
- 2026-08-09 — **JSON Formatter** (Utilities) — [2026-08-09_json_formatter.py](Utilities/2026-08-09_json_formatter.py)
- 2026-08-08 — **Command Line Calculator** (CLI) — [2026-08-08_command_line_calculator.py](CLI/2026-08-08_command_line_calculator.py)
- 2026-08-07 — **Expense Tracker** (Utilities) — [2026-08-07_expense_tracker.py](Utilities/2026-08-07_expense_tracker.py)
- 2026-08-06 — **Image Resizer** (Image) — [2026-08-06_image_resizer.py](Image/2026-08-06_image_resizer.py)
- 2026-08-05 — **PDF Merger** (File) — [2026-08-05_pdf_merger.py](File/2026-08-05_pdf_merger.py)
- 2026-08-04 — **Weather API Client** (API) — [2026-08-04_weather_api_client.py](API/2026-08-04_weather_api_client.py)
- 2026-08-04 — **QR Code Generator** (Utilities) — [2026-08-04_qr_code_generator.py](Utilities/2026-08-04_qr_code_generator.py)
- 2026-08-04 — **Password Generator** (Security) — [2026-08-04_password_generator.py](Security/2026-08-04_password_generator.py)
<!-- LATEST_SCRIPTS_END -->
