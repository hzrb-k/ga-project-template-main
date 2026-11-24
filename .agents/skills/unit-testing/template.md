# 単体テスト仕様書テンプレート（C11 / CTest）

各テストケースは「メタブロック（固定フィールド）＋詳細セクション」の形式で記述する。
- `実行手段` は `ctest` または `manual` の1語で固定する（`manual` 時は `理由` を1行必須）。
- テストの合否結果は本ファイルに書き戻さない（CTest 実行ログを正本とする）。

## 1. テスト方針
- 対象モジュール: `<module>`（`include/<module>.h`, `src/<module>.c`）
- 実行手段: `ctest`（`ctest --test-dir build --output-on-failure --timeout 10`）
- 動的検査: Sanitizer 対応環境では `-DENABLE_SANITIZERS=ON` で ASan/UBSan 検知ゼロを確認

## 2. テストケース一覧

## UT-SAMPLE-001 正常値の加算

- **ID**: UT-SAMPLE-001
- **観点**: 正常値
- **実行手段**: ctest
- **理由**: -

### 概要
符号付き32ビット整数の通常加算で正しい和が返ることを確認する。

### 前提条件
- `sample.h` をインクルードして `sample_safe_add` を呼び出せること

### 入力
- `a = 12`, `b = 30`, `out = &result`

### 期待結果
- 戻り値が `true` であること
- `result == 42` であること

## UT-SAMPLE-002 オーバーフローと NULL 引数の防御

- **ID**: UT-SAMPLE-002
- **観点**: 境界値・NULL処理
- **実行手段**: ctest
- **理由**: -

### 概要
`INT32_MAX + 1`、`INT32_MIN - 1`、および `out == NULL` で未定義動作を起こさず `false` を返し、既存の `*out` を破壊しないことを確認する。

### 前提条件
- `result` に初期値 `123` を設定しておくこと

### 入力
- ケース1: `a = INT32_MAX`, `b = 1`, `out = &result`
- ケース2: `a = INT32_MIN`, `b = -1`, `out = &result`
- ケース3: `a = 1`, `b = 2`, `out = NULL`

### 期待結果
- いずれのケースも戻り値が `false` であること
- ケース1・2で `result == 123` のまま変更されないこと
- ASan/UBSan 有効時にエラーが検知されないこと
