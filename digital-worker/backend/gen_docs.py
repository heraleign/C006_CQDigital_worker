import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_USER", "root")
os.environ.setdefault("MYSQL_PASSWORD", "123456")
os.environ.setdefault("MYSQL_DATABASE", "db_digital_worker")

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.database import Base
from app.models import *

def generate_sql():
    output = []
    output.append("-- ============================================================")
    output.append("-- 数据运维数字员工平台 - 数据库建表语句")
    output.append("-- Database: db_digital_worker")
    output.append("-- Charset: utf8mb4")
    output.append("-- ============================================================")
    output.append("")
    output.append("CREATE DATABASE IF NOT EXISTS db_digital_worker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    output.append("USE db_digital_worker;")
    output.append("")

    for table in Base.metadata.sorted_tables:
        try:
            stmt = str(CreateTable(table).compile(dialect=mysql.dialect()))
            output.append(stmt)
            output.append("")
        except Exception as e:
            output.append(f"-- ERROR generating {table.name}: {e}")
            output.append("")

    sql_path = os.path.join(os.path.dirname(__file__), "../../docs", "db_schema.sql")
    os.makedirs(os.path.dirname(sql_path), exist_ok=True)
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print(f"SQL generated: {sql_path}")
    return sql_path

if __name__ == "__main__":
    generate_sql()
