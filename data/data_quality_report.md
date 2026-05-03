# Data Quality Report (Phase 3 #R)
_Generated: 2026-05-03 09:39:11_
- organizations 総数: **348**

## 1. 重複候補 (canonical_name ratio > 0.85)
- 候補ペア数: **187**
- 検出手法: difflib.SequenceMatcher (lowercase normalize、最短 4 字未満は除外)

### Top 10 by ratio
| ratio | A | B |
|---:|---|---|
| 0.967 | Banagram Primary Health Centre (`1390465b`) | Baragram Primary Health Centre (`3c5757d0`) |
| 0.952 | TNTvillage (`1612e842`) | TNT Village (`ad29844a`) |
| 0.947 | Jamtoria Primary Health Centre (`83ab739d`) | Jatra Primary Health Centre (`19331f24`) |
| 0.943 | Amba Primary Health Centre (`e506627a`) | Jamar Primary Health Centre (`0e9011f3`) |
| 0.926 | Jamar Primary Health Centre (`0e9011f3`) | Jatra Primary Health Centre (`19331f24`) |
| 0.918 | Dharampur Primary Health Centre (`215d028e`) | Indrapur Primary Health Centre (`7d152b05`) |
| 0.915 | Community Health Systems - Longview Regional Medical Center (`cc5e5109`) | Community Health Systems - Bluffton Regional Medical Center (`57bd6ef4`) |
| 0.915 | Faridpur Primary Health Centre (`75739f48`) | Gazipur Primary Health Centre (`d9df71f7`) |
| 0.912 | Hurshi Primary Health Centre (`bde76029`) | Gokhuri Primary Health Centre (`cbbb2b51`) |
| 0.912 | Jamtoria Primary Health Centre (`83ab739d`) | Jamar Primary Health Centre (`0e9011f3`) |

## 2. 外部 ID クロスリンク (Wikidata QID -> ROR)
- 試行: **30** 件 (パイロット limit 30)
- 取得成功: **0** 件
- API: Wikidata REST `Special:EntityData/Qxxx.json`、user-agent=OrganizationGenealogyResearch/0.1 (info@emerging-future.org)、interval=0.5s

## 3. 信頼性スコア再算出
- 対象 claim: canonical_name (active) **330** 件
- 修正された claim: **330** 件
- 平均 confidence: before=**0.6758** -> after=**0.6574**
- フラグ件数 (after <= 0.35): **76**

### 分布 (before / after)
| bucket | before | after |
|---|---:|---:|
| <0.30 | 0 | 0 |
| 0.30-0.49 | 0 | 76 |
| 0.50-0.69 | 230 | 154 |
| 0.70-0.84 | 0 | 0 |
| 0.85-1.00 | 100 | 100 |

## 4. 手動レビュー対象 Top 20
| # | kind | ratio | A | B |
|---:|---|---:|---|---|
| 1 | duplicate_candidate | 0.967 | Banagram Primary Health Centre (`1390465b`) | Baragram Primary Health Centre (`3c5757d0`) |
| 2 | duplicate_candidate | 0.952 | TNTvillage (`1612e842`) | TNT Village (`ad29844a`) |
| 3 | duplicate_candidate | 0.947 | Jamtoria Primary Health Centre (`83ab739d`) | Jatra Primary Health Centre (`19331f24`) |
| 4 | duplicate_candidate | 0.943 | Amba Primary Health Centre (`e506627a`) | Jamar Primary Health Centre (`0e9011f3`) |
| 5 | duplicate_candidate | 0.926 | Jamar Primary Health Centre (`0e9011f3`) | Jatra Primary Health Centre (`19331f24`) |
| 6 | duplicate_candidate | 0.918 | Dharampur Primary Health Centre (`215d028e`) | Indrapur Primary Health Centre (`7d152b05`) |
| 7 | duplicate_candidate | 0.915 | Community Health Systems - Longview Regional Medical Center (`cc5e5109`) | Community Health Systems - Bluffton Regional Medical Center (`57bd6ef4`) |
| 8 | duplicate_candidate | 0.915 | Faridpur Primary Health Centre (`75739f48`) | Gazipur Primary Health Centre (`d9df71f7`) |
| 9 | duplicate_candidate | 0.912 | Hurshi Primary Health Centre (`bde76029`) | Gokhuri Primary Health Centre (`cbbb2b51`) |
| 10 | duplicate_candidate | 0.912 | Jamtoria Primary Health Centre (`83ab739d`) | Jamar Primary Health Centre (`0e9011f3`) |
| 11 | duplicate_candidate | 0.909 | Bhatol Primary Health Centre (`44b975b1`) | Boyal Primary Health Centre (`bd9769ea`) |
| 12 | duplicate_candidate | 0.909 | Gankar Primary Health Centre (`546d062d`) | Jamar Primary Health Centre (`0e9011f3`) |
| 13 | duplicate_candidate | 0.906 | Amba Primary Health Centre (`e506627a`) | Jatra Primary Health Centre (`19331f24`) |
| 14 | duplicate_candidate | 0.903 | Chandpur Primary Health Centre (`4bf6e575`) | Bahadurpur Primary Health Centre (`aba1bdab`) |
| 15 | duplicate_candidate | 0.900 | Banagram Primary Health Centre (`1390465b`) | Balihara Primary Health Centre (`2ba214ff`) |
| 16 | duplicate_candidate | 0.900 | Chandpur Primary Health Centre (`4bf6e575`) | Faridpur Primary Health Centre (`75739f48`) |
| 17 | duplicate_candidate | 0.900 | Chandpur Primary Health Centre (`4bf6e575`) | Indrapur Primary Health Centre (`7d152b05`) |
| 18 | duplicate_candidate | 0.900 | Faridpur Primary Health Centre (`75739f48`) | Iswarpur Primary Health Centre (`8ecfd172`) |
| 19 | duplicate_candidate | 0.900 | Iswarpur Primary Health Centre (`8ecfd172`) | Indrapur Primary Health Centre (`7d152b05`) |
| 20 | duplicate_candidate | 0.897 | Bhatol Primary Health Centre (`44b975b1`) | Barunhat Primary Health Centre (`fb4a8b2c`) |

## 5. ルール
- 削除なし: 旧 claim は `superseded_by` で新 claim にリンク。
- canonical_name が `^Q\d+$` のとき confidence -> 0.3。
- alternate_names 空 + geo_scope 空 + end_date 空、かつ before=0.6 のとき confidence -> 0.3。
- ボーナス: country 有 +0.05 / end_date 有 +0.05 / alt 多言語 +0.05 (clamp 0..1)。
