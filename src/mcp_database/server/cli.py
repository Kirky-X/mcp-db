#!/usr/bin/env python3
"""MCP Database Server CLI - 启动 MCP 数据库服务器"""

import argparse
import asyncio
import os

from mcp.server.stdio import stdio_server

from mcp_database.server import create_server


async def main() -> None:
    parser = argparse.ArgumentParser(description="MCP Database Server")
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="数据库连接 URL（默认从 DATABASE_URL 环境变量读取）",
    )
    args = parser.parse_args()

    if not args.database_url:
        parser.error("必须指定 --database-url 或设置 DATABASE_URL 环境变量")

    server = create_server(args.database_url)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
