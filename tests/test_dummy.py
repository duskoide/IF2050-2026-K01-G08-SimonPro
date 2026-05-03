def test_matematika_dasar():
    """Test super basic untuk ngecek pytest jalan."""
    assert 1 + 1 == 2

def test_pyqt_bisa_jalan_headless():
    """Test untuk memastikan xvfb berhasil merender QApplication tanpa monitor."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    assert app is not None
