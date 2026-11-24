---
name: initial-project
description: C11プロジェクトの立ち上げ初期化を行うスキル。「プロジェクトを初期化して」「ドキュメント一式を作成して」「initial-project を進めて」など、アイデア検討から要件定義書・基本設計書・詳細設計書までを段階的に作成したいときに使う。各フェーズでユーザー承認を得てから次へ進む。
---

# プロジェクト初期化スキル（C11 プロジェクト向け）

このスキルは、C11 プロジェクト立ち上げに必要な設計ドキュメント一式を順番に作成するためのスキルです。

## 全体の流れ

以下の 4 フェーズで進行します。各フェーズ完了時に**必ずユーザーの承認を得てから次へ進んでください**。承認なしに次フェーズへ進むことは禁止です。

```text
フェーズ1: アイデア検討（対話形式） → docs/ideas/idea-summary.md
    ↓ ユーザー承認
フェーズ2: 要件定義書の作成（requirements-definition スキル） → docs/specs/requirements-definition.md
    ↓ ユーザー承認
フェーズ3: 基本設計書の作成（basic-design スキル） → docs/specs/basic-design.md
    ↓ ユーザー承認
フェーズ4: 詳細設計書の作成（detailed-design スキル） → docs/specs/detailed-design.md
    ↓ ユーザー承認（完了）
```

---

## フェーズ1: アイデア検討（対話形式）

要件定義に入る前に、ユーザーとの対話を通じて「何を作るか」の輪郭を整理します。一度にすべて聞かず、会話の流れに合わせて深掘りしてください。

### 対話で引き出す内容
- **背景・動機**: なぜこのツール／ライブラリ／アプリケーションを C11 で作るのか、解決したい課題は何か
- **目的**: 実現したい状態・提供価値
- **想定利用者・呼び出し元**: CLI 利用者か、他プログラムからリンクされるライブラリか、組み込み／常駐ツールか
- **主要機能**: 必須機能と任意機能、主な入出力（標準入出力・ファイル・コマンド引数・API 呼び出し等）
- **制約・前提**: 対応 OS（Windows / Linux / macOS）、C11 標準準拠、外部依存の可否、メモリ・性能・安全性要件

### アイデアサマリーの保存
対話で全体像が整理できたら、`write_file` で以下に保存し、ユーザーの承認を得てください。
- **保存先**: `docs/ideas/idea-summary.md`

---

## フェーズ2: 要件定義書の作成

`.agents/skills/requirements-definition/SKILL.md` と同ディレクトリの `template.md` を `read_file` で読み込み、その手順に従って要件定義書を作成します。

- **保存先**: `docs/specs/requirements-definition.md`
- 作成・セルフレビュー後、ユーザー承認を得てフェーズ3へ進みます。

---

## フェーズ3: 基本設計書の作成

`.agents/skills/basic-design/SKILL.md` と同ディレクトリの `template.md` を `read_file` で読み込み、C11・CMake・CTest 構成を前提とした基本設計書を作成します。

- **インプット**: `docs/specs/requirements-definition.md`
- **主な観点**:
  - モジュール構成（`include/`・`src/`・`tests/`）とコンポーネント責務分割
  - 公開インターフェース（CLI 仕様 / 公開ヘッダ API / 入出力ファイル形式）
  - 技術スタック（C11・CMake・CTest・コンパイラ・Sanitizer・`clang-format`・`cppcheck`）
  - 非機能設計（メモリ安全性・エラー処理方針・性能・移植性）
- **保存先**: `docs/specs/basic-design.md`
- ユーザー承認を得てフェーズ4へ進みます。

---

## フェーズ4: 詳細設計書の作成

`.agents/skills/detailed-design/SKILL.md` と同ディレクトリの `template.md` を `read_file` で読み込み、実装に着手できる粒度まで詳細設計書を作成します。

- **インプット**: `docs/specs/requirements-definition.md`、`docs/specs/basic-design.md`
- **主な観点**:
  - ファイル構成（`include/*.h`・`src/*.c`・`tests/test_*.c`・`CMakeLists.txt` ターゲット）
  - データ構造（`struct` / `enum` / `typedef`）と公開関数シグネチャ
  - メモリ所有権・ライフサイクル（誰が確保し誰が解放するか）
  - エラーコード一覧・境界条件・処理フロー
- **保存先**: `docs/specs/detailed-design.md`
- ユーザー承認を得たらプロジェクト初期化完了を報告します。

---

## 完了時の報告内容
- 作成されたドキュメント一覧（パス付き）
- 次のステップ（`feature` スキルを使った機能単位のタスクリスト作成・実装・レビュー・テスト）
