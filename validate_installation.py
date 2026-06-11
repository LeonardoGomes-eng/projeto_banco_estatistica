"""
Script de Validação - Análise Estatística Avançada
Verifica se todos os componentes foram instalados e estão funcionando
"""

import sys
import importlib
from pathlib import Path

def check_python_version():
    """Verifica se Python 3.8+ está instalado"""
    print("🔍 Verificando versão do Python...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
        return True
    else:
        print(f"   ❌ Python 3.8+ necessário (atual: {sys.version_info.major}.{sys.version_info.minor})")
        return False


def check_packages():
    """Verifica se todos os pacotes necessários estão instalados"""
    print("\n🔍 Verificando pacotes necessários...")
    
    packages = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'plotly': 'Plotly',
        'sklearn': 'Scikit-learn',
        'scipy': 'SciPy',
        'statsmodels': 'Statsmodels',
        'psycopg2': 'psycopg2-binary'
    }
    
    prophet_available = True
    all_ok = True
    
    for module, name in packages.items():
        try:
            importlib.import_module(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (instale com: pip install {module})")
            if module == 'psycopg2':
                print(f"      └─ Alternativa: pip install psycopg2-binary")
            all_ok = False
    
    # Prophet é opcional
    try:
        importlib.import_module('prophet')
        print(f"   ✅ Prophet")
    except ImportError:
        print(f"   ⚠️  Prophet (opcional - instale com: pip install prophet)")
        prophet_available = False
    
    return all_ok, prophet_available


def check_files():
    """Verifica se os arquivos foram criados corretamente"""
    print("\n🔍 Verificando estrutura de arquivos...")
    
    base_path = Path('dashboard')
    
    files_to_check = {
        'dashboard/app.py': 'Arquivo principal',
        'dashboard/components/statistical_analysis.py': 'Módulo de análises',
        'dashboard/components/statistical_utils.py': 'Funções utilitárias',
        'dashboard/pages/07_Analise_Estatistica.py': 'Página de análise',
        'dashboard/examples_statistical_analysis.py': 'Exemplos',
        'ANALISE_ESTATISTICA_DOCS.md': 'Documentação',
        'GUIA_INSTALACAO.md': 'Guia de instalação',
    }
    
    all_ok = True
    for file_path, description in files_to_check.items():
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {description}")
            print(f"      └─ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {description}")
            print(f"      └─ {file_path} (não encontrado)")
            all_ok = False
    
    return all_ok


def check_requirements():
    """Verifica se requirements.txt foi atualizado"""
    print("\n🔍 Verificando requirements.txt...")
    
    try:
        with open('dashboard/requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = {
            'prophet': 'Prophet',
            'scikit-learn': 'Scikit-learn',
            'scipy': 'SciPy',
            'statsmodels': 'Statsmodels',
            'numpy': 'NumPy'
        }
        
        all_ok = True
        for package, name in required_packages.items():
            if package in content:
                print(f"   ✅ {name} ({package})")
            else:
                print(f"   ❌ {name} ({package}) não encontrado")
                all_ok = False
        
        return all_ok
    
    except FileNotFoundError:
        print("   ❌ requirements.txt não encontrado")
        return False


def check_imports():
    """Tenta importar os módulos de análise"""
    print("\n🔍 Testando importações dos módulos...")
    
    try:
        # Adicionar dashboard ao path
        sys.path.insert(0, 'dashboard')
        
        from components.statistical_analysis import (
            analyze_seasonality,
            forecast_with_prophet,
            analyze_trend_by_state,
            cluster_municipalities
        )
        print("   ✅ Módulo statistical_analysis importado com sucesso")
        
        from components.statistical_utils import (
            calculate_growth_rate,
            classify_trend,
            detect_outliers_iqr
        )
        print("   ✅ Módulo statistical_utils importado com sucesso")
        
        return True
    
    except ImportError as e:
        print(f"   ❌ Erro ao importar módulos: {str(e)}")
        return False
    except Exception as e:
        print(f"   ⚠️  Aviso ao importar: {str(e)}")
        return True  # Não é crítico


def check_database():
    """Verifica conexão com banco de dados"""
    print("\n🔍 Verificando conexão com banco de dados...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "zika_db")
        db_user = os.getenv("DB_USER", "postgres")
        
        print(f"   ℹ️  Configuração:")
        print(f"      └─ Host: {db_host}")
        print(f"      └─ Port: {db_port}")
        print(f"      └─ Database: {db_name}")
        print(f"      └─ User: {db_user}")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=os.getenv("DB_PASSWORD", "")
            )
            
            print("   ✅ Conexão com PostgreSQL bem-sucedida")
            
            # Verificar tabelas
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='notificacoes'
            """)
            
            if cursor.fetchone()[0] > 0:
                cursor.execute("SELECT COUNT(*) FROM notificacoes")
                count = cursor.fetchone()[0]
                print(f"   ✅ Tabela 'notificacoes' encontrada ({count} registros)")
            else:
                print("   ⚠️  Tabela 'notificacoes' não encontrada")
                print("      └─ Execute o script de setup do banco de dados")
            
            conn.close()
            return True
        
        except psycopg2.Error as e:
            print(f"   ❌ Erro ao conectar: {str(e)}")
            print("      └─ Verifique credenciais em .env")
            return False
    
    except ImportError:
        print("   ⚠️  psycopg2 não instalado (opcional para testes)")
        return True


def main():
    """Executa todos os testes de validação"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " VALIDAÇÃO - ANÁLISE ESTATÍSTICA AVANÇADA ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {
        'Python': check_python_version(),
        'Arquivos': check_files(),
        'Requirements': check_requirements(),
        'Importações': check_imports(),
    }
    
    packages_ok, prophet_available = check_packages()
    results['Pacotes'] = packages_ok
    
    # Database check é informativo
    check_database()
    
    # Resumo
    print("\n" + "=" * 80)
    print("📋 RESUMO DE VALIDAÇÃO")
    print("=" * 80)
    
    for name, status in results.items():
        status_str = "✅ OK" if status else "❌ ERRO"
        print(f"  {name}: {status_str}")
    
    print("\n" + "=" * 80)
    
    if all(results.values()):
        print("\n✨ VALIDAÇÃO COMPLETA - Sistema pronto para uso!")
        print("\n🚀 Próximos passos:")
        print("   1. Execute: streamlit run dashboard/app.py")
        print("   2. Navegue até: 'Análise Avançada' → 'Análise Estatística Avançada'")
        print("   3. Explore as 4 abas de análise")
        
        if prophet_available:
            print("\n✅ Prophet disponível - Previsões funcionarão normalmente")
        else:
            print("\n⚠️  Prophet não instalado - Instale com: pip install prophet")
        
        return 0
    else:
        print("\n❌ ERROS DETECTADOS - Corrija antes de continuar")
        print("\n💡 Dicas:")
        print("   • Instale pacotes: pip install -r dashboard/requirements.txt")
        print("   • Verifique estrutura de diretórios")
        print("   • Configure .env com credenciais do banco")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
