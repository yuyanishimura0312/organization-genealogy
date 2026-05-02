# Phase 1 (v0.1) 完了レポート

完了日: 2026-05-02
ステータス: **Phase 1 完了基準達成** → Phase 2 (v0.2 Activity/Function/Impact 分離) 移行可

## ロードマップ完了条件 vs 実績

| 条件 | 結果 |
|---|---|
| 全レコードが Source/Claim に紐づく | ✓ 5 ケースは完全注釈、ETL 投入分は最小 claim 付与 |
| 日付精度を扱える (`exact`/`year`/`century` 等) | ✓ 全ケースで運用 |
| 近代法人以外が下位扱いされない | ✓ ベネディクト会・ハンザ・三井(家)・MakerDAO で検証済 |
| 200-500 件の pilot データ | ✓ **335 件達成** (ROR 100 + Wikidata typed 230 + 完全注釈 5) |

## データ投入実績

```
組織 (organization)         335
　├ ROR 学術機関              100
　├ Wikidata typed            230
　│  ├ monastic_order  50
　│  ├ historical_org  50
　│  ├ hanseatic       30
　│  ├ dao             50
　│  ├ corporation     50
　│  └ clan             0 (Q11425700 は instance なし)
　└ 完全注釈代表ケース          5

claim                       340
source                       10
organization_form            53
function_type                25
activity                     10
function_record              22
impact_record                 9
event                        10
relation                      2
form_assignment              16
```

## 状態別分布

| status | 件数 |
|---|---:|
| active | 103 |
| unknown | 226 |
| extinct | 6 |

`unknown` が多いのは Wikidata の dissolution_date 欠損が原因。Phase 2 で claim 経由で補完予定。

## 既知のデータ品質課題 (Stream J 警告通り)

Wikidata の `P31/P279*` (instance_of + subclass tree) クエリは、subclass の広がりが想定より大きく、不適切なエントリが混入する:

- **Q15243209 historical_organization** → 「Primary Health Centre」「Ferry」「Parramatta (都市)」などが含まれる (subclass の解釈ぶれ)
- **Q4287745 DAO** → ホスピタル・市町村まで波及する例
- ラベルなしの QID (`Q2260863` 等) も混入

これは Stream J の **「Wikidata の粒度・欠落を真実として扱ってしまう」** リスク (リスク登録 #2 関連) の実演。

**対策 (Phase 2)**:
1. 取り込み時に instance_of 階層の depth を制限 (P279 で 2 段以下)
2. claim 確度を `0.4` 程度に下げる (現状 0.6) — `unknown` ラベルや subclass 距離による減点
3. 別ソースとのクロスチェック (ROR は学術機関に限定されるので低リスク)
4. 手動 curation phase を Phase 2 に組み込む

## 残課題と次のステップ

### Phase 2 (v0.2) への移行アクション

ロードマップ Phase 2 のアクティビティ:
- Activity / Function / Impact 分離の **深掘り注釈** を 50-100 件で実施
- 機能タイプの標準セット運用 (現状 22 件 → 200 件以上を目標)
- 東アジア事例で「文化」フィールドに丸めず、継続原理・信用・場・名跡を機能として分解

### 即着手可能な追加 ETL

- **OpenAlex** 学術機関の補完 (ROR 連携)
- **Companies House (UK)** 英国法人の取り込み
- **EDINET** 日本上場企業の取り込み (XBRL)
- **Seshat databank** 古代ポリティの導入 (Stream J)

## 意思決定ゲート通過状況

| Gate | 内容 | 通過判定 |
|---|---|---|
| Gate 0 理論 | 個体群生態学を主、Luhmann/Beer/制度論を補助、Spencer 批判 | ✓ Phase 0 で固定済 |
| Gate 1 データ | ROR (CC0)、Wikidata (CC0)、5 ケース手動注釈 | ✓ public_redistributable のみ |
| Gate 2 スキーマ | 法人中心への偏り検査 | ⚠ 100/335 が学術機関、5/335 が完全注釈非西洋・修道院・DAO。Phase 2 で東アジア事例を増やす |

## コミット情報

- yuyanishimura0312/organization-genealogy `b8a44e7` (66 ファイル initial)
- 次の commit で Phase 1 完了状態を push 予定
