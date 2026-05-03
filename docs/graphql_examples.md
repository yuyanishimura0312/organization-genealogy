# GraphQL Query Examples

These examples are specifications only. They use identifiers and labels confirmed in the local SQLite database when concrete IDs are shown.

## 1. ベネディクト会から succession チェーンで 3 ホップ

Current data has two outgoing `SUCCESSION` relations from `ベネディクト会 (Order of Saint Benedict)`: `Cluny 修道会 (Order of Cluny)` and `シトー会 (Cistercian Order)`. A 3-hop query should therefore return the available 1-hop paths unless more succession edges are added.

```graphql
query BenedictineSuccession {
  genealogy(
    rootId: "2cf732ca2e44458b8d793880b59a1b5d"
    depth: 3
    relationTypes: [SUCCESSION]
    direction: OUTGOING
  ) {
    root {
      id
      canonicalName
    }
    paths {
      depth
      organizations {
        id
        canonicalName
        startDate
        status
      }
      relations {
        relationType
        validPeriod {
          from
          fromPrecision
        }
        confidence
        claim {
          valueKind
          source {
            title
            locator
          }
        }
      }
    }
  }
}
```

## 2. VSM S5 が記録された全組織

```graphql
query OrganizationsWithVsmS5($after: Cursor) {
  functionTypes(framework: BEER_VSM, vsmSystemNo: "S5") {
    id
    nameEn
    functions(page: { first: 50, after: $after }) {
      nodes {
        id
        organization {
          id
          canonicalName
          primaryForm {
            label
          }
          status
          startDate
        }
        confidence
        claim {
          confidence
          interpretationNote
          source {
            title
            sourceType
            reliabilityScore
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

## 3. 中世の知識伝達ネットワーク

The resolver can either filter by derived `EraBucket` on both endpoint organizations or let the client post-filter returned nodes. This example keeps the relation query explicit and asks for endpoint era buckets.

```graphql
query MedievalKnowledgeNetwork {
  relations(type: KNOWLEDGE_TRANSFER, page: { first: 100 }) {
    nodes {
      id
      sourceOrganization {
        id
        canonicalName
        eraBucket
        startDate
      }
      targetOrganization {
        id
        canonicalName
        eraBucket
        startDate
      }
      validPeriod {
        from
        fromPrecision
        to
        toPrecision
      }
      strength
      confidence
      claim {
        valueKind
        confidence
        source {
          title
          authors
          locator
        }
      }
    }
  }
}
```

## 4. シトー会の機能・活動・出典をまとめて取得

```graphql
query CistercianFunctionTrace {
  organization(id: "d9c2571497d84171ad42eb73e6c6799c") {
    id
    canonicalName
    primaryForm {
      taxonomyName
      formCode
      label
    }
    activities(page: { first: 20 }) {
      id
      activityType
      domain
      orientation
      validPeriod {
        from
        to
      }
      claim {
        confidence
        source {
          title
        }
      }
    }
    functions(page: { first: 25 }) {
      nodes {
        functionType {
          id
          nameEn
          sourceFramework
          vsmSystemNo
          millerSubsystemNo
        }
        mechanism
        confidence
        claim {
          fieldPath
          valueKind
          source {
            title
            locator
          }
        }
      }
    }
  }
}
```

## 5. ある source に紐づく claim と対象 entity を監査する

```graphql
query SourceClaimAudit($sourceType: SourceType!) {
  sources(sourceType: $sourceType, page: { first: 20 }) {
    id
    title
    reliabilityScore
    redistribution
    claims(page: { first: 50 }) {
      nodes {
        id
        entityType
        entityId
        fieldPath
        valueKind
        confidence
        interpretationNote
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

## 6. 組織の temporal facets を指定時点で取得

```graphql
query OrganizationStateAtDate($id: ID!, $at: Date!) {
  organization(id: $id) {
    id
    canonicalName
    temporalFacets(at: $at, page: { first: 50 }) {
      facetType
      facetValue
      validPeriod {
        from
        fromPrecision
        to
        toPrecision
      }
      confidence
      claim {
        source {
          title
        }
      }
    }
  }
}
```

## 7. succession と schism を同時に辿る系譜探索

```graphql
query SuccessionAndSchism($rootId: ID!) {
  genealogy(
    rootId: $rootId
    depth: 4
    relationTypes: [SUCCESSION, SCHISM]
    direction: OUTGOING
  ) {
    nodes {
      id
      canonicalName
      status
    }
    edges {
      sourceOrganization {
        canonicalName
      }
      targetOrganization {
        canonicalName
      }
      relationType
      validPeriod {
        from
      }
      confidence
      claim {
        source {
          title
        }
      }
    }
  }
}
```

GraphQL が REST より優位な操作: 組織を起点に、機能・活動・関係・イベント・temporal facet・各 claim と source を一度の nested query で取得し、過取得や複数往復を避けながら、出典付きの系譜ビューをクライアントごとの粒度で組み立てられる。
