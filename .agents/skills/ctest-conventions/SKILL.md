---
name: ctest-conventions
description: 実行手段=ctest の C11 テスト実装プロファイル（配置・命名・トレーサビリティ・CHECKマクロ・CMakeLists.txt登録・実行コマンド・Sanitizer・B/M/T/I/E症状カタログと診断方法）。test-to-code が C テストを書くとき、test-runner がビルド・実行・診断するときに必ず参照する。
---

# 実装プロファイル：ctest（C11 + CMake + CTest）

実行手段=`ctest` のときのツール固有作法をまとめます。責務分離・5分類（B/M/T/I/E）・期待値改ざん禁止などの原則は `test-loop` / `test-to-code` / `test-runner` に従います。

## ディレクトリ・配置と CMake 登録
- テストコード配置:
  - 単体テスト: `tests/test_<モジュール名>.c`
  - 結合テスト: `tests/test_it_<フロー名>.c`
  - 総合（CLI）テスト: `tests/test_st_<フロー名>.c`（必要に応じてテスト用ドライバ）
- `CMakeLists.txt` の `if(BUILD_TESTING)` ブロックへ以下を登録する：
  ```cmake
  add_executable(test_<name> tests/test_<name>.c)
  target_link_libraries(test_<name> PRIVATE app_core project_options)
  add_test(NAME UT_<NAME> COMMAND test_<name>)
  set_tests_properties(UT_<NAME> PROPERTIES TIMEOUT 10)
  ```
- ビルド出力は **`build/` のみ**。テスト用一時ファイルが必要な場合は `build/test_tmp/` などワークスペース内に作成し、終了時に必ず削除する。

## 命名・トレーサビリティ
- テスト関数名は `static void test_<ケースID小文字>_<内容>(void)` とする（例: `test_ut_sample_001_safe_add_normal`）。
- CTest 名（`add_test(NAME ...)`）および失敗時 `stderr` ログにケースIDを含め、仕様書と 1 対 1 で突合できるようにする。

## アサーション規約（`NDEBUG` 非依存）
- 標準 `assert()` は `Release` ビルド（`-DNDEBUG`）で無効化されるため使用せず、以下と同等の **`CHECK` マクロ**で失敗件数を集計し、`main()` が失敗時に非ゼロ（`1`）を返す構成とする：

```c
#include <stdio.h>

static int g_failures = 0;

#define CHECK(cond)                                                                                \
    do {                                                                                           \
        if (!(cond)) {                                                                             \
            (void)fprintf(stderr, "FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond);                 \
            g_failures++;                                                                          \
        }                                                                                          \
    } while (0)
```

- 浮動小数を比較する場合は厳密一致（`==`）を避け、仕様で定めた許容誤差（`fabs(a - b) <= eps`）で比較する。
- テスト関数内で確保した動的メモリも全経路で `free` する（ASan/LSan 誤検知防止）。

## 実行コマンド（必須ルール準拠）
生成バイナリを直接叩かず、**必ず `ctest` 経由＋タイムアウト付き**で実行する：

```text
設定（既定: Sanitizer有効） : cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
設定（Sanitizer無効化）     : cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=OFF
ビルド                      : cmake --build build
テスト実行                  : ctest --test-dir build --output-on-failure --timeout 10
```

## `test-runner` 向け：B / M / T / I / E 症状カタログと診断方法

| 観察される症状 | 分類 | 具体例と対処方針 |
|---|---|---|
| 構文エラー、未宣言識別子、型不一致、`-Werror` / `/WX` 警告エラー、未解決シンボル | **B** | コンパイラ/リンカのエラー行が `tests/` なら `test-to-code` へ、`include/`・`src/`・`CMakeLists.txt` ならメインへ差し戻す |
| AddressSanitizer / UndefinedBehaviorSanitizer 報告、SEGFAULT、アクセス違反、`cppcheck` 警告 | **M** | スタックトレースの起点を確認し、`tests/` 起因なら `test-to-code` へ、`src/` 起因なら本体修正へ差し戻す |
| テストデータの準備ミス、浮動小数の厳密一致、一時ファイルパスの誤り、順序非保証の比較 | **T** | 期待値は緩めず、テスト側の前提・比較方法の修正を `test-to-code` へ差し戻す |
| 仕様書の期待値と関数の実戻り値・出力が食い違う（ビルド・メモリは正常） | **I** | テストは正しくバグを検出しているためテストを変更せず人間確認へ停止 |
| `cmake`/`ctest`/コンパイラ未導入、ジェネレータ設定不備、Sanitizer リンク非対応 | **E** | 人間（環境担当）へ報告して停止（Sanitizer 非対応時は `-DENABLE_SANITIZERS=OFF` の案内を添える） |
| テストが `--timeout 10` で打ち切られた | **I** または **T** | 無限ループやブロッキング入力待ちの原因箇所を特定し、本体起因なら `I`、テスト起因なら `T` として報告 |
