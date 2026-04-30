"""
Internationalization (i18n) module for Devliz.
Provides a simple translation system with English (default) and Italian support.
"""

_current_language = "en"

_translations: dict[str, dict[str, str]] = {
        # ── Home View ──
        "Home": {"it": "Home"},
        "Snapshot Count": {"it": "Numero Snapshot"},
        "Total Size": {"it": "Dimensione Totale"},
        "Total Files": {"it": "File Totali"},
        "Total Folders": {"it": "Cartelle Totali"},
        "Heaviest File": {"it": "File più Pesante"},
        "No file found": {"it": "Nessun file trovato"},

        # ── Catalogue View ──
        "Catalogue": {"it": "Catalogo"},
        "Import": {"it": "Importa"},
        "Edit": {"it": "Modifica"},
        "Sort": {"it": "Ordina"},
        "Search content": {"it": "Cerca contenuto"},
        "Name": {"it": "Nome"},
        "Author": {"it": "Autore"},
        "Creation date": {"it": "Data creazione"},
        "Modification date": {"it": "Data modifica"},
        "Size": {"it": "Dimensione"},
        "Total configurations: {count} ({size})": {"it": "Totale configurazioni: {count} ({size})"},
        "Export": {"it": "Esporta"},
        "Snapshot (.zip)": {"it": "Snapshot (.zip)"},
        "Associated folders (.zip)": {"it": "Cartelle associate (.zip)"},
        "Delete": {"it": "Cancella"},
        "Installed folders": {"it": "Cartelle installate"},
        "Entire snapshot": {"it": "Snapshot intero"},
        "Open": {"it": "Apri"},
        "Snapshot folder": {"it": "Cartella snapshot"},
        "Associated local folder: {name}": {"it": "Cartella locale associata: {name}"},
        "Install": {"it": "Installa"},
        "Update with local": {"it": "Aggiorna con locali"},
        "Duplicate": {"it": "Duplica"},

        # ── Catalogue Table Model ──
        "Description": {"it": "Descrizione"},
        "Date/Time": {"it": "Data/Ora"},
        "Tags": {"it": "Tags"},

        # ── Catalogue Import Dialog ──
        "Import a configuration": {"it": "Importa una configurazione"},
        "Edit a configuration": {"it": "Modifica una configurazione"},
        "CREATE CONFIGURATION": {"it": "CREA CONFIGURAZIONE"},
        "SAVE CHANGES": {"it": "SALVA MODIFICHE"},
        "CLOSE": {"it": "CHIUDI"},
        "Error": {"it": "Errore"},
        "An error occurred while creating the data.": {"it": "Si è verificato un errore durante la creazione dei dati."},
        "The 'Name' field cannot be empty.": {"it": "Il campo 'Nome' non può essere vuoto."},
        "At least one folder must be associated with the configuration.": {"it": "Deve essere associata almeno una cartella alla configurazione."},

        # ── Import Tab Details ──
        "ID:": {"it": "ID:"},
        "Name:": {"it": "Nome:"},
        "Description:": {"it": "Descrizione:"},
        "Tags:": {"it": "Tags:"},
        "Add tag...": {"it": "Aggiungi tag..."},

        # ── Import Tab Directories ──
        "Add local folder": {"it": "Aggiungi cartella locale"},
        "Add starred folder": {"it": "Aggiungi cartella preferita"},
        "Select a folder to add to the list": {"it": "Seleziona una cartella ad aggiungere alla lista"},
        "Warning": {"it": "Attenzione"},
        "The selected folder is already in the list.": {"it": "La cartella selezionata è già presente nella lista."},
        "The selected folder does not exist on the system.": {"it": "La cartella selezionata non esiste nel sistema."},
        "The selected folder is not a valid folder.": {"it": "La cartella selezionata non è una cartella valida."},

        # ── Import Tabs ──
        "Details": {"it": "Dettagli"},
        "Folders": {"it": "Cartelle"},
        "An error occurred while collecting the data.": {"it": "Si è verificato un errore durante la raccolta dei dati."},

        # ── Catalogue Controller ──
        "Configuration created": {"it": "Configurazione creata"},
        "Configuration modified": {"it": "Configurazione modificata"},
        "The configuration has been created successfully.": {"it": "La configurazione è stata creata con successo."},
        "The configuration has been modified successfully.": {"it": "La configurazione è stata modificata con successo."},
        "An error occurred: {error}": {"it": "Si è verificato un errore: {error}"},
        "Install configuration": {"it": "Installa configurazione"},
        "Are you sure you want to install the selected snapshot? All current directories will be replaced with those contained in the snapshot.": {
            "it": "Sei sicuro di voler installare lo snapshot selezionato ? Tutte le directory presenti attualmente verranno rimpiazzate con quelle contenute nello snapshot."
        },
        "Installation error": {"it": "Errore di installazione"},
        "An error occurred during installation: {error}": {"it": "Si è verificato un errore durante l'installazione: {error}"},
        "Edit error": {"it": "Errore di modifica"},
        "An error occurred during editing: {error}": {"it": "Si è verificato un errore durante la modifica: {error}"},
        "Delete configuration": {"it": "Elimina configurazione"},
        "Are you sure you want to delete the selected snapshot?\n\nAll associated files will be deleted in ": {
            "it": "Sei sicuro di voler eliminare lo snapshot selezionato ?\n\n Verranno eliminati tutti i file associati in "
        },
        "Deletion error": {"it": "Errore di eliminazione"},
        "An error occurred during deletion: {error}": {"it": "Si è verificato un errore durante l'eliminazione: {error}"},
        "Duplicate configuration": {"it": "Duplica configurazione"},
        "Are you sure you want to duplicate the selected configuration?": {"it": "Sei sicuro di voler duplicare la configurazione selezionata ?"},
        "Duplication error": {"it": "Errore di duplicazione"},
        "An error occurred during duplication: {error}": {"it": "Si è verificato un errore durante la duplicazione: {error}"},
        "Export snapshot": {"it": "Esporta snapshot"},
        "Are you sure you want to export the selected snapshot?": {"it": "Sei sicuro di voler esportare lo snapshot selezionato ?"},
        "Select the save folder for the snapshot": {"it": "Seleziona la cartella di salvataggio dello snapshot"},
        "Export error": {"it": "Errore di esportazione"},
        "An error occurred during export: {error}": {"it": "Si è verificato un errore durante l'esportazione: {error}"},
        "Export associated folders": {"it": "Esporta cartelle associate"},
        "Are you sure you want to export the folders associated with the selected snapshot?": {
            "it": "Sei sicuro di voler esportare le cartelle associate allo snapshot selezionato ?"
        },
        "Select the save folder for the associated folders": {"it": "Seleziona la cartella di salvataggio delle cartelle associate"},
        "Delete installed folders": {"it": "Elimina cartelle installate"},
        "Are you sure you want to delete the currently installed folders for the selected snapshot?": {
            "it": "Sei sicuro di voler eliminare le cartelle installate attualmente nel sistema relative allo snapshot selezionato ?"
        },
        "Update associated folders": {"it": "Aggiorna cartelle associate"},
        "Are you sure you want to update the associated folders of the selected snapshot with the currently installed ones?": {
            "it": "Sei sicuro di voler aggiornare le cartelle associate allo snapshot selezionato con quelle attualmente installate nel sistema ?"
        },
        "Update error": {"it": "Errore di aggiornamento"},
        "An error occurred during update: {error}": {"it": "Si è verificato un errore durante l'aggiornamento: {error}"},
        "The folder no longer exists in {path}": {"it": "La cartella non esiste più in {path}"},

        # ── Catalogue Searcher View ──
        "Catalogue Search": {"it": "Ricerca nel Catalogo"},
        "Start": {"it": "Avvia"},
        "Stop": {"it": "Ferma"},
        "Target": {"it": "Target"},
        "Type": {"it": "Tipo"},
        "Extensions": {"it": "Estensioni"},
        "Enter the text to search...": {"it": "Inserisci il testo da cercare..."},
        "Waiting...": {"it": "In attesa..."},
        "Remove from search": {"it": "Rimuovi dalla ricerca"},
        "File name": {"it": "Nome del file"},
        "File content": {"it": "Contenuto del file"},
        "Search the content of a file": {"it": "Cerca il contenuto di un file"},
        "Search the content of a file using a regex": {"it": "Cerca il contenuto di un file usando una regex"},
        "Search the name of a file": {"it": "Cerca il nome di un file"},
        "Search the name of a file using a regex": {"it": "Cerca il nome di un file usando una regex"},

        # ── Catalogue Searcher Controller ──
        "Missing text": {"it": "Testo mancante"},
        "Please enter a text before starting the search.": {"it": "Per favore, inserisci un testo prima di avviare la ricerca."},

        # ── Catalogue Searcher Model ──
        "Snapshot name": {"it": "Nome snapshot"},
        "Status": {"it": "Stato"},
        "Values found": {"it": "Valori trovati"},
        "Progress": {"it": "Progresso"},
        "Pending": {"it": "In attesa"},
        "Results": {"it": "Risultati"},
        "Results ({count})": {"it": "Risultati ({count})"},
        "Starting...": {"it": "Avvio..."},
        "Searching...": {"it": "Ricerca in corso..."},
        "Scan: {file_name}": {"it": "Scansione: {file_name}"},

        # ── Settings View ──
        "Settings": {"it": "Impostazioni"},
        "Choose directory": {"it": "Scegli directory"},
        "Catalogue path": {"it": "Percorso del catalogo"},
        "Configuration tags": {"it": "Tag configurazioni"},
        "Add tag": {"it": "Aggiungi tag"},
        "Add one or more tags to assign to configurations": {"it": "Aggiungi uno o più tag da assegnare alle configurazioni"},
        "Enter the tag name": {"it": "Inserisci il nome del tag"},
        "Add": {"it": "Aggiungi"},
        "Cancel": {"it": "Annulla"},
        "The tag cannot be empty or already existing": {"it": "Il tag non può essere vuoto o già esistente"},
        "Confirm deletion": {"it": "Conferma eliminazione"},
        "Are you sure you want to delete this tag?": {"it": "Sei sicuro di voler eliminare questo tag?"},
        "Snapshots - Custom data": {"it": "Snapshots - Dati personalizzati"},
        "Add variable": {"it": "Aggiungi variabile"},
        "Add one or more custom variables to assign to snapshots": {"it": "Aggiungi una o un più variabili personalizzate da assegnare agli snapshots"},
        "Enter the variable name": {"it": "Inserisci il nome della variabile"},
        "The variable cannot be empty or already existing": {"it": "La variabile non può essere vuota o già esistente"},
        "Are you sure you want to delete this variable?": {"it": "Sei sicuro di voler eliminare questa variabile?"},
        "Enable pre-installation backup": {"it": "Abilita backup pre-installazione"},
        "Backup local folders (on this PC) contained in the configuration before installing it": {
            "it": "Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di installarla"
        },
        "Enable pre-edit backup": {"it": "Abilita backup pre-modifica"},
        "Backup local folders (on this PC) contained in the configuration before editing them": {
            "it": "Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di modificarle"
        },
        "Enable pre-deletion backup": {"it": "Abilita backup pre-eliminazione"},
        "Backup local folders (on this PC) contained in the configuration before deleting them": {
            "it": "Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di eliminarle"
        },
        "Clear attached folders before installation": {"it": "Cancella cartelle allegate prima dell'installazione"},
        "Before installing a configuration, clear the local attached folders (on this PC)": {
            "it": "Prima di installare una configurazione, cancella le cartelle allegate locali (presenti su questo pc)"
        },
        "Snapshots": {"it": "Snapshots"},
        "Starred folders": {"it": "Cartelle preferite"},
        "Add folder": {"it": "Aggiungi cartella"},
        "Add one or more starred folders": {"it": "Aggiungi una o più cartelle preferite"},
        "Select folder": {"it": "Seleziona cartella"},
        "Starred files": {"it": "File preferiti"},
        "Add file": {"it": "Aggiungi file"},
        "Add one or more starred files": {"it": "Aggiungi uno o più file preferiti"},
        "Select file": {"it": "Seleziona file"},
        "All Files (*.*)": {"it": "Tutti i file (*.*)"},
        "Starred executables": {"it": "Eseguibili preferiti"},
        "Choose an executable": {"it": "Scegli un eseguibile"},
        "Add one or more starred executables to monitor on the home screen": {"it": "Aggiungi uno o più file preferiti da monitorare nella home"},
        "Select executable": {"it": "Seleziona eseguibile"},
        "Executable Files (*.exe);;All Files (*.*)": {"it": "File eseguibili (*.exe);;Tutti i file (*.*)"},
        "Starred services": {"it": "Servizi preferiti"},
        "Add service": {"it": "Aggiungi servizio"},
        "Add one or more Windows services to monitor on the home screen": {"it": "Aggiungi uno o più servizi di Windows da monitorare nella home"},
        "Enter the Windows service name (e.g. Spooler)": {"it": "Inserisci il nome del servizio di Windows (es. Spooler)"},
        "The service name cannot be empty or already existing": {"it": "Il nome del servizio non può essere vuoto o già esistente"},
        "Are you sure you want to delete this service?": {"it": "Sei sicuro di voler eliminare questo servizio?"},
        "Favorites": {"it": "Preferiti"},
        "Open Folder": {"it": "Apri Cartella"},
        "Working folder of {name}": {"it": "Cartella di lavoro di {name}"},
        "Clear backups": {"it": "Cancella backups"},
        "Clear Backups of {name}": {"it": "Cancella Backups di {name}"},
        "This operation will delete all backup files created by the application.": {
            "it": "Questa operazione eliminerà tutti i file di backup creati dall'applicazione."
        },
        "Application theme": {"it": "Tema dell'applicazione"},
        "Select the application theme": {"it": "Seleziona il tema dell'applicazione"},
        "Light": {"it": "Chiaro"},
        "Dark": {"it": "Scuro"},
        "Application": {"it": "Applicazione"},
        "Information": {"it": "Informazioni"},
        "About {name}": {"it": "Informazioni su {name}"},

        # ── Settings Controller ──
        "Select the catalogue folder": {"it": "Seleziona la cartella del catalogo"},
        "Backup folder cleanup": {"it": "Pulizia cartella di backup"},
        "Are you sure you want to clean the backup folder? This operation will delete all files in the backup folder.": {
            "it": "Sei sicuro di voler pulire la cartella di backup ? Questa operazione eliminerà tutti i file presenti nella cartella di backup."
        },
        "An error occurred while cleaning the backup folder: {error}": {
            "it": "Si è verificato un errore durante la pulizia della cartella di backup: {error}"
        },

        # ── Dashboard Model ──
        "Dashboard Update": {"it": "Aggiornamento Dashboard"},
        "Dashboard data update": {"it": "Aggiornamento dati della dashboard"},

        # ── Devliz Update Tasks ──
        "Retrieving Monitored Software": {"it": "Recupero Software Monitorati"},
        "Retrieving saved snapshots": {"it": "Recupero snapshots salvati"},

        # ── Frame Util ──
        "Updating, please wait": {"it": "Aggiornamento in corso attendere"},

        # ── Language Setting ──
        "Language": {"it": "Lingua"},
        "Select the application language": {"it": "Seleziona la lingua dell'applicazione"},
        "English": {"it": "Inglese"},
        "Italian": {"it": "Italiano"},

        # ── Restart Dialog ──
        "Restart required": {"it": "Riavvio necessario"},
        "The application needs to restart to apply the changes. Restart now?": {
            "it": "L'applicazione deve essere riavviata per applicare le modifiche. Riavviare ora?"
        },
}


def set_language(lang: str):
    """Set the current language ('en' or 'it')."""
    global _current_language
    _current_language = lang


def get_language() -> str:
    """Get the current language code."""
    return _current_language


def tr(key: str, **kwargs) -> str:
    """
    Translate a key to the current language.
    English is the default (the key itself is the English text).
    Supports format placeholders: tr("Hello {name}", name="World")
    """
    if _current_language == "en":
        text = key
    else:
        entry = _translations.get(key)
        if entry and _current_language in entry:
            text = entry[_current_language]
        else:
            text = key

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def init_language():
    """Initialize language from saved settings."""
    from devliz.application.app import app_settings, AppSettings
    lang = app_settings.get(AppSettings.language)
    set_language(lang)
