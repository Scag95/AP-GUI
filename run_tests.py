"""
Script de ejecución unificada de pruebas para AP-GUI.
Ejecuta la batería completa de tests usando pytest de forma programática.
"""

import sys
import pytest


def run_all_tests():
    print("=" * 60)
    print("   EJECUCIÓN DE BATERÍA DE TESTS AUTOMATIZADOS DE AP-GUI")
    print("=" * 60)
    
    # Argumentos para pytest: carpeta tests/, verbose, traceback corto
    args = ["tests/", "-v", "--tb=short"]
    
    # Ejecución programática de pytest
    exit_code = pytest.main(args)
    
    return exit_code


if __name__ == "__main__":
    code = run_all_tests()
    sys.exit(code)
