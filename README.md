# ga-project-template (C11 / Google Antigravity)

要件定義から基本設計・詳細設計・実装・読み取り専用コードレビュー・V字モデルテストまでを一貫して進めるための、**Google Antigravity（ホストネイティブ・コンテナ不使用）・C11 向けプロジェクトテンプレート**です。

> 本テンプレートは『ハーネス＆ループで自走するAI駆動開発』（技術評論社、2026年）の Claude Code 用サンプルテンプレートをベースに、Google Antigravity・C11 開発向けに再構築した構成です。

## 前提ツール

ホスト環境に以下を導入して PATH を通してください。

- **C11 コンパイラ**: `clang` / `gcc` / MSVC `cl` のいずれか
- **ビルド・テスト**: `cmake`、`ctest`、`ninja`（または `make` / MSBuild）
- **フック実行ランタイム**: `python`（Python 3）
- **品質ツール（推奨）**: `clang-format`、`cppcheck`

## クイックスタート

### ビルド＆スモークテスト

Debug ビルドでは既定で Sanitizer（ASan/UBSan、対応ツールチェーン時自動有効化）が有効です。

```bash
cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure --timeout 10
```

Sanitizer を明示的に無効にする場合:

```bash
cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=OFF
cmake --build build
ctest --test-dir build --output-on-failure --timeout 10
```

### Antigravity での開発フロー

1. **プロジェクト初期化**（`initial-project` スキル）: アイデア検討 → 要件定義 → 基本設計 → 詳細設計
2. **機能追加**（`feature` スキル）: ヒアリング → タスクリスト → 実装＆ビルド → `c-reviewer` レビュー → 設計書更新 → V字モデルテスト仕様＆ `test-loop`

## ディレクトリ構成

```text
.
├── AGENTS.md                         # 常時読み込みの最小正本（C11ビルド・安全・工程ルール）
├── CMakeLists.txt                    # C11 / 警告エラー化 / CTest / Sanitizer切替
├── .clang-format                     # Cコードフォーマット規約
├── .agents/
│   ├── rules/c-style.md              # *.c / *.h 編集時に自動適用する安全性規約
│   ├── skills/                       # 初期化・設計・機能追加・レビュー・テスト各種スキル
│   ├── agents/                       # 読み取り専用 c-reviewer ほか役割分離サブエージェント
│   ├── hooks.json                    # PostToolUse ライフサイクルフック定義
│   ├── hooks/c-check.py              # 整形（clang-format）＆静的解析（cppcheck/コンパイラ）
│   └── mcp_config.json               # MCP 拡張用設定ファイル
├── include/                          # 公開ヘッダ (.h)
├── src/                              # Cソースファイル (.c)
├── tests/                            # 単体・結合テスト (.c)
├── docs/                             # アイデア・設計書・テスト仕様書
└── changes/                          # 機能別タスクリスト
```

## セキュリティ設定（コンテナ不使用時の推奨）

Antigravity の設定画面で以下を有効にして運用してください。

- **Terminal Sandbox**: 有効
- **Permission Preset**: `Default` または `Auto`（`Turbo` はサンドボックス無効化のため非推奨）
- **Denylist**: `rm -rf`、`make install`、`cmake --install`、`sudo` 等の危険コマンドをブロック

工程の順序や成果物の正本は [AGENTS.md](./AGENTS.md) を参照してください。

## ライセンス

本リポジトリは [MIT License](./LICENSE) のもとで公開しています。
