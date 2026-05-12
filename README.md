# stock-materials prototype

日本株の「ストップ高銘柄」について、材料候補を自動収集してMarkdownレポートにする試作品です。

狙いは、AI APIに課金せずに次の流れをGitHub Actionsで回すことです。

1. ストップ高銘柄を取得する
2. TDnetとニュースRSSから材料候補を探す
3. キーワードで材料らしさを採点する
4. 任意でローカルLLMに短い要約を作らせる
5. `reports/YYYY-MM-DD.md` に保存する

## まず動かす

ネット接続なしでも、デモデータで動作確認できます。

```bash
python -m stock_materials --stop-source sample --demo --output reports/demo.md
```

CSVで対象銘柄を渡す場合:

```bash
python -m stock_materials --stop-source csv --stop-csv sample_stop_high.csv --demo
```

TDnet取得の確認用:

```bash
python -m stock_materials \
  --date 2026-05-08 \
  --stop-source csv \
  --stop-csv examples/stop_high_2026-05-08.csv \
  --tdnet-days 3
```

実際に取得する場合:

```bash
python -m stock_materials \
  --stop-source stockmaster \
  --include-news \
  --include-social \
  --tdnet-days 3 \
  --output reports/$(date +%Y-%m-%d).md
```

`--include-social` を付けると、各銘柄に Yahoo!ファイナンス掲示板、Yahoo!ファイナンスの株つぶやき、X検索への確認リンクを追加します。投稿本文の大量取得はせず、TDnetやニュースとは別の「市場の声チェック」として出します。

## ローカルLLMを使う

`LOCAL_LLM_CMD` を設定すると、APIではなくローカルコマンドに要約を任せます。

例:

```bash
export LOCAL_LLM_CMD='llama-cli -m ./models/model.gguf -n 512 -p {prompt}'
python -m stock_materials --stop-source stockmaster --include-news --use-llm
```

`LOCAL_LLM_CMD` が未設定、または実行に失敗した場合は、キーワードベースの要約に戻ります。

## GitHub Actions

`.github/workflows/stock-materials.yml` が、平日16:15 JSTに実行される設定です。手動実行もできます。

注意点:

- GitHub ActionsのcronはUTC基準です。
- 非公開リポジトリではActions分の課金設定に注意してください。
- WebサイトのHTML変更で取得が崩れる可能性があります。
- レポートは投資助言ではありません。必ずTDnetや会社IRなど一次情報を確認してください。
