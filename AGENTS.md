# プロジェクト大原則（C11 / Google Antigravity）

本リポジトリは、**コンテナ不使用（ホストネイティブ）・C11・Google Antigravity** 向けの開発テンプレートです。全作業で以下の原則を遵守してください。

## 1. 技術スタックと必須コマンド

- **言語 / 標準**: C11（`CMAKE_C_STANDARD 11`、`CMAKE_C_STANDARD_REQUIRED ON`、`CMAKE_C_EXTENSIONS OFF`）
- **ビルド / テスト**: CMake + CTest（ビルド出力先は **`build/` に限定**）
- **整形 / 静的解析**: `clang-format` / `cppcheck`（未導入時はコンパイラ構文チェックへフォールバック）

```text
設定（既定: Sanitizer有効） : cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
設定（Sanitizer無効化）     : cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=OFF
ビルド                      : cmake --build build
テスト                      : ctest --test-dir build --output-on-failure --timeout 10
```

## 2. 品質・安全の鉄則（コンテナなし前提）

1. **ワークスペース外操作の禁止**: プロジェクトルート外のファイル参照・作成・編集・削除を一切行わない。
2. **危険コマンドの禁止**: `cmake --install` / `make install` などのシステム領域へのインストール、`rm -rf` などの破壊的コマンドを実行しない。
3. **警告ゼロ・全テスト通過**: コンパイル警告ゼロ（GCC/Clang: `-Wall -Wextra -Werror`、MSVC: `/W4 /WX`）かつ `ctest` 全通過まで完了としない。
4. **バイナリ実行の制約**: 生成バイナリの直接実行はテストランナー（`ctest`）経由に限定し、必ずタイムアウト（`--timeout 10`）を付ける。
5. **期待値の改ざん禁止**: テストを通す目的で `assert` や期待値を実挙動に合わせて緩めない。

## 3. 開発プロセス（正本）

開発は **「プロジェクト初期化」** と **「機能追加」** の2フェーズで進めます。

### プロジェクト初期化（`initial-project` スキル）

以下の4段階でドキュメントを作成し、**各フェーズでユーザー承認を得てから次へ進む**。

1. アイデア検討（対話形式） → `docs/ideas/idea-summary.md`
2. 要件定義（`requirements-definition` スキル） → `docs/specs/requirements-definition.md`
3. 基本設計（`basic-design` スキル） → `docs/specs/basic-design.md`
4. 詳細設計（`detailed-design` スキル） → `docs/specs/detailed-design.md`

### 機能追加（`feature` スキル）

以下の6フェーズで進めます。

1. **機能要求のヒアリング**: 設計書と照合し、要件範囲・矛盾を確認する。
2. **タスクリストの作成・承認**: `changes/YYYYMMDD-<機能名>/tasklist.md` に保存し、ユーザー承認後に着手する。
3. **実装＆ビルド確認**: タスクリスト順に実装・完了チェックしつつ、警告ゼロのビルドを維持する。
4. **コードレビューと修正ループ**（`code-review-loop` スキル）: 読み取り専用サブエージェント `c-reviewer` でレビューし、致命的・高の指摘がゼロになるまで修正する（最大3周。残存時は人間判断へ停止）。
5. **ドキュメント更新**: 実装と設計書の乖離を確認し、承認後に設計書を最新化する。
6. **テスト仕様作成・実施（V字モデル・2段構え）**:
   - **6-1. 仕様作成**: `testspec-writer` サブエージェントが対応する体裁スキル（`unit-testing` / `integration-testing` / `system-testing`）を用いて全レベルの仕様書を作成・追記し、網羅性をユーザー確認する。
   - **6-2. コード作成・実行**: 実行手段（既定 `ctest`、`manual` は除外）ごとに `test-loop` スキルを起動し、`test-to-code`（生成）と `test-runner`（実行・読み取り専用）を分離して回す。
   - **失敗原因の分類（B/M/T/I/E）**:
     - **B（Build）**: コンパイル・警告・リンクエラー → ヘッダ依存・型・`CMakeLists.txt` を修正
     - **M（Memory / UB）**: Sanitizer（ASan/UBSan）または `cppcheck` 検知 → ポインタ・配列境界・メモリ解放を修正
     - **T（Test）**: テストコードの不備 → `test-to-code` へ差し戻し（最大3周）
     - **I（Implementation）**: 仕様と実装の不一致 → テストを改変せず人間確認へ停止（または実装修正）
     - **E（Environment）**: ツールチェーン・CMake環境不備 → 人間確認へ停止
   - **結果の正本**: テスト合否は仕様書（`.md`）に書き戻さず、CTest の出力・ログを正本とする。

## 4. ディレクトリ・成果物格納規約

| 種類 | 格納先 |
|---|---|
| 公開ヘッダ / ソース / テスト | `include/*.h` / `src/*.c` / `tests/test_*.c` |
| ビルド生成物（Git除外） | `build/` |
| アイデアサマリー | `docs/ideas/idea-summary.md` |
| 要件定義書 / 基本設計書 / 詳細設計書 | `docs/specs/{requirements-definition,basic-design,detailed-design}.md` |
| 単体 / 結合 / 総合テスト仕様書 | `docs/tests/{unit,integration,system}/<名前>.md` |
| 機能別タスクリスト | `changes/YYYYMMDD-<機能名>/tasklist.md` |
| Antigravity カスタマイズ | `.agents/{rules,skills,agents,hooks}/`, `.agents/hooks.json`, `.agents/mcp_config.json` |
