#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from life_os_agent.database.setup import DB_PATH, init_database


def main():
    print("🗄️  Inicializando banco de dados LifeOS...")
    print(f"   Caminho: {DB_PATH}")

    result = init_database()

    if result.get("status") == "ok":
        print("✅ Banco de dados criado com sucesso!")
        print("\n📋 Tabelas criadas:")
        print("   - users")
        print("   - transactions")
        print("   - budget_goals")
        print("   - calendar_events")
    else:
        print("❌ Erro ao criar banco de dados")
        sys.exit(1)


if __name__ == "__main__":
    main()
