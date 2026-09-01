
def test_app_dashboard_launch(qtbot):
    """
    Test E2E that opens the Dashboard, verifies it loads,
    and navigates to the Settings page.
    """
    from devliz.controller.dashboard import DashboardController
    
    # Inizializza il controller principale della dashboard
    dashboard = DashboardController()
    
    # Registra la vista al qtbot in modo che la finestra venga distrutta a fine test
    qtbot.addWidget(dashboard.view)
    
    # Avvia la dashboard
    dashboard.start()
    
    # Attendiamo che l'interfaccia si aggiorni
    # Importante in E2E: aspettiamo che i task in background della dashboard
    # (es. lettura dei file e calcolo delle statistiche) siano finiti prima
    # di navigare o chiudere l'app, per evitare crash da thread orfani.
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Verifica che la pagina iniziale sia la Home
    assert dashboard.view.stackedWidget.currentWidget() == dashboard.home.view

    # Naviga verso la pagina delle impostazioni
    # Per il momento simuliamo lo switch programmatico. Più avanti
    # possiamo cercare il pulsante fisico nella navigazione.
    dashboard.view.switchTo(dashboard.settings.view)
    
    # Attendiamo che l'interfaccia si aggiorni
    qtbot.waitUntil(
        lambda: dashboard.view.stackedWidget.currentWidget() == dashboard.settings.view,
        timeout=2000
    )
    
    assert dashboard.view.stackedWidget.currentWidget() == dashboard.settings.view

    # Controlliamo che esista un elemento noto nei settings
    # E.g., proviamo a vedere se la vista delle impostazioni è configurata
    assert dashboard.settings.view.objectName() is not None
