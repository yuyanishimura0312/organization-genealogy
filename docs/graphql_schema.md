# GraphQL Schema Draft

Status: draft only. This SDL mirrors the current SQLite schema in `sql/schema_sqlite_v01.sql` and `sql/schema_sqlite_v05_temporal_facet.sql`; no GraphQL runtime is implemented yet. Candidate runtimes: Apollo Server, Hasura, PostGraphile.

## SDL

```graphql
scalar Date
scalar DateTime
scalar JSON
scalar Cursor

enum DatePrecision {
  EXACT
  YEAR
  DECADE
  CENTURY
  PERIOD
  BEFORE
  AFTER
  UNKNOWN
}

enum EraBucket {
  ANCIENT
  MEDIEVAL
  EARLY_MODERN
  MODERN
  CONTEMPORARY
  UNKNOWN
}

enum OrgStatus {
  ACTIVE
  DORMANT
  TRANSFORMED
  MERGED
  SPLIT
  EXTINCT
  UNKNOWN
}

enum SourceType {
  PRIMARY_TEXT
  SECONDARY_LITERATURE
  DATASET
  INTERVIEW
  ARCHIVE
  ARTIFACT
  ONCHAIN
  WEB
  ORAL_HISTORY
  ETHNOGRAPHY
}

enum Redistribution {
  PUBLIC_REDISTRIBUTABLE
  ATTRIBUTION_REQUIRED
  NONCOMMERCIAL
  PRIVATE
  RESTRICTED
}

enum ClaimValueKind {
  PRESENT
  ABSENT
  PARTIAL
  UNKNOWN
  INAPPLICABLE
}

enum Orientation {
  EXPLORATION
  EXPLOITATION
  MIXED
  UNSPECIFIED
}

enum FunctionFramework {
  MILLER_LIVING_SYSTEMS
  BEER_VSM
  COMPOUND
}

enum ImpactDirection {
  POSITIVE
  NEGATIVE
  MIXED
  UNCERTAIN
  DESCRIPTIVE
}

enum ImpactTimeHorizon {
  IMMEDIATE
  SHORT_TERM
  MEDIUM_TERM
  LONG_TERM
  INTERGENERATIONAL
}

enum RelationType {
  ALLIANCE
  COMPETITION
  CONTROL
  SUBSIDIARY
  PARTNERSHIP
  MEMBERSHIP
  SUCCESSION
  SPIN_OFF
  MERGER
  ACQUISITION
  TRADE
  FUNDING
  SHAREHOLDING
  KNOWLEDGE_TRANSFER
  MIMETIC_ISOMORPHISM
  NORMATIVE_PRESSURE
  COERCIVE_PRESSURE
  PROTOCOL_DEPENDENCY
  SUPPLY_CHAIN
  INTERLOCKING_DIRECTORATE
  PATRONAGE
  RIVALRY
  SCHISM
  UNKNOWN
}

enum Directionality {
  DIRECTED
  UNDIRECTED
  BIDIRECTIONAL
}

enum EventType {
  FOUNDING
  DISSOLUTION
  MERGER
  ACQUISITION
  SPLIT
  SPIN_OFF
  RENAMING
  RELOCATION
  REFORM
  CRISIS
  GOVERNANCE_CHANGE
  PLATFORM_SHIFT
  IPO
  PRIVATIZATION
  NATIONALIZATION
  DORMANCY_START
  DORMANCY_END
  REVIVAL
  REORGANIZATION
  UNKNOWN
}

enum VsrLabel {
  VARIATION
  SELECTION
  RETENTION
  STRUGGLE
}

enum FacetType {
  MEMBERSHIP
  GOVERNANCE
  RESOURCE_BASE
  TERRITORY
  TECHNOLOGY
  IDENTITY
  SCALE
  LEGITIMATION_BASIS
}

enum RelationDirectionFilter {
  OUTGOING
  INCOMING
  BOTH
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: Cursor
  endCursor: Cursor
}

input PageInput {
  first: Int = 50
  after: Cursor
}

type OrganizationConnection {
  nodes: [Organization!]!
  edges: [OrganizationEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type OrganizationEdge {
  cursor: Cursor!
  node: Organization!
}

type RelationConnection {
  nodes: [Relation!]!
  edges: [RelationEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type RelationEdge {
  cursor: Cursor!
  node: Relation!
}

type FunctionConnection {
  nodes: [Function!]!
  edges: [FunctionEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type FunctionEdge {
  cursor: Cursor!
  node: Function!
}

type ClaimConnection {
  nodes: [Claim!]!
  edges: [ClaimEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type ClaimEdge {
  cursor: Cursor!
  node: Claim!
}

type DateRange {
  from: Date
  fromPrecision: DatePrecision
  to: Date
  toPrecision: DatePrecision
}

type Source {
  id: ID!
  sourceType: SourceType!
  title: String!
  authors: JSON
  publicationDate: Date
  publisher: String
  locator: JSON
  accessedAt: DateTime
  reliabilityScore: Float
  reliabilityBasis: String
  biasNotes: String
  license: String
  redistribution: Redistribution
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Claim {
  id: ID!
  entityType: String!
  entityId: ID!
  fieldPath: String
  valueKind: ClaimValueKind!
  claimValue: JSON
  confidence: Float!
  interpretationNote: String
  recordedBy: String!
  recordedAt: DateTime!
  source: Source
  supersededBy: Claim
  supersedes(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Form {
  id: ID!
  taxonomyName: String!
  formCode: String!
  label: String!
  parent: Form
  children(page: PageInput): [Form!]!
  definition: String
  criteria: JSON
  validPeriod: DateRange
  notes: String
  organizations(page: PageInput): OrganizationConnection!
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type OrganizationFormAssignment {
  id: ID!
  organization: Organization!
  form: Form!
  validPeriod: DateRange
  isPrimary: Boolean!
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
}

type Organization {
  id: ID!
  canonicalName: String!
  alternateNames: JSON
  description: String
  primaryForm: Form
  formAssignments(page: PageInput): [OrganizationFormAssignment!]!
  geoScope: JSON
  startDate: Date
  startDatePrecision: DatePrecision
  endDate: Date
  endDatePrecision: DatePrecision
  eraBucket: EraBucket!
  status: OrgStatus!
  attributes: JSON
  externalIds: JSON
  activities(page: PageInput): [Activity!]!
  functions(typeId: ID, framework: FunctionFramework, vsmSystemNo: String, page: PageInput): FunctionConnection!
  impacts(page: PageInput): [Impact!]!
  relations(type: RelationType, direction: RelationDirectionFilter = BOTH, page: PageInput): RelationConnection!
  events(type: EventType, page: PageInput): [Event!]!
  temporalFacets(type: FacetType, at: Date, page: PageInput): [OrganizationTemporalFacet!]!
  claims(fieldPath: String, page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Activity {
  id: ID!
  organization: Organization!
  activityType: String!
  domain: String
  description: String
  inputs: JSON
  outputs: JSON
  scale: JSON
  orientation: Orientation!
  validPeriod: DateRange
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  functions(page: PageInput): FunctionConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type FunctionType {
  id: ID!
  nameJa: String!
  nameEn: String!
  sourceFramework: FunctionFramework!
  millerSubsystemNo: Int
  vsmSystemNo: String
  parent: FunctionType
  children: [FunctionType!]!
  definition: String!
  observableIndicators: JSON
  eraExamples: JSON
  functions(page: PageInput): FunctionConnection!
}

type Function {
  id: ID!
  organization: Organization!
  functionType: FunctionType!
  mechanism: JSON
  beneficiaries: JSON
  dependency: JSON
  activity: Activity
  validPeriod: DateRange
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Impact {
  id: ID!
  organization: Organization!
  impactDomain: String!
  metricName: String!
  metricValue: JSON!
  direction: ImpactDirection!
  timeHorizon: ImpactTimeHorizon!
  affectedScope: JSON
  evaluationMethod: String
  validPeriod: DateRange
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Relation {
  id: ID!
  sourceOrganization: Organization!
  targetOrganization: Organization!
  relationType: RelationType!
  directionality: Directionality!
  validPeriod: DateRange
  strength: Float
  strengthBasis: String
  relationAttributes: JSON
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  events: [EventRelation!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type Event {
  id: ID!
  eventType: EventType!
  eventDate: Date
  eventDatePrecision: DatePrecision!
  description: String
  participants: JSON
  causes: JSON
  outcomes: JSON
  location: JSON
  dissolutionCause: String
  vsrLabel: VsrLabel
  organizations: [EventOrganization!]!
  relations: [EventRelation!]!
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type EventOrganization {
  id: ID!
  event: Event!
  organization: Organization!
  role: String!
}

type EventRelation {
  id: ID!
  event: Event!
  relation: Relation!
  changeType: String!
  beforeValue: String
  afterValue: String
}

type OrganizationTemporalFacet {
  id: ID!
  organization: Organization!
  validPeriod: DateRange
  facetType: FacetType!
  facetValue: JSON!
  confidence: Float
  claim: Claim
  claims(page: PageInput): ClaimConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
  recordVersion: Int!
}

type GenealogyPath {
  depth: Int!
  relations: [Relation!]!
  organizations: [Organization!]!
}

type GenealogyResult {
  root: Organization!
  maxDepth: Int!
  relationTypes: [RelationType!]!
  paths: [GenealogyPath!]!
  nodes: [Organization!]!
  edges: [Relation!]!
}

input OrganizationFilter {
  status: OrgStatus
  formCode: String
  taxonomyName: String
  eraBucket: EraBucket
  startedAfter: Date
  startedBefore: Date
  search: String
}

type Query {
  organizations(filter: OrganizationFilter, page: PageInput): OrganizationConnection!
  organization(id: ID!): Organization
  forms(taxonomyName: String, parentId: ID, page: PageInput): [Form!]!
  functionTypes(framework: FunctionFramework, vsmSystemNo: String): [FunctionType!]!
  functionsByType(typeId: ID!, page: PageInput): FunctionConnection!
  relations(type: RelationType, organizationId: ID, direction: RelationDirectionFilter = BOTH, page: PageInput): RelationConnection!
  events(type: EventType, organizationId: ID, page: PageInput): [Event!]!
  sources(sourceType: SourceType, page: PageInput): [Source!]!
  claims(entityType: String, entityId: ID, fieldPath: String, page: PageInput): ClaimConnection!
  genealogy(rootId: ID!, depth: Int = 3, relationTypes: [RelationType!] = [SUCCESSION], direction: RelationDirectionFilter = OUTGOING): GenealogyResult!
}
```

## Query examples

### 1. Organization with nested traceability

```graphql
query OrganizationTrace($id: ID!) {
  organization(id: $id) {
    id
    canonicalName
    status
    primaryForm {
      label
    }
    functions(vsmSystemNo: "S5", page: { first: 10 }) {
      nodes {
        functionType {
          id
          nameEn
        }
        claim {
          confidence
          source {
            title
            locator
          }
        }
      }
    }
    claims(page: { first: 20 }) {
      nodes {
        fieldPath
        valueKind
        confidence
        source {
          title
        }
      }
    }
  }
}
```

### 2. Cursor pagination over active organizations

```graphql
query ActiveOrganizations($after: Cursor) {
  organizations(filter: { status: ACTIVE }, page: { first: 25, after: $after }) {
    nodes {
      id
      canonicalName
      startDate
      eraBucket
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### 3. Genealogy from a root organization

```graphql
query SuccessionGenealogy($rootId: ID!) {
  genealogy(rootId: $rootId, depth: 3, relationTypes: [SUCCESSION], direction: OUTGOING) {
    root {
      canonicalName
    }
    edges {
      relationType
      validPeriod {
        from
      }
      targetOrganization {
        canonicalName
      }
      claim {
        confidence
        source {
          title
        }
      }
    }
  }
}
```

### 4. VSM S5 functions across organizations

```graphql
query VsmS5Organizations {
  functionTypes(framework: BEER_VSM, vsmSystemNo: "S5") {
    id
    nameEn
    functions(page: { first: 50 }) {
      nodes {
        organization {
          id
          canonicalName
          status
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
}
```

### 5. Medieval knowledge-transfer network

```graphql
query MedievalKnowledgeTransfer {
  relations(type: KNOWLEDGE_TRANSFER, page: { first: 100 }) {
    nodes {
      sourceOrganization {
        canonicalName
        eraBucket
      }
      targetOrganization {
        canonicalName
        eraBucket
      }
      validPeriod {
        from
        fromPrecision
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

## Notes

- `claims` fields are resolver conveniences: they select `claim` rows by `entity_type`, `entity_id`, and optional `field_path`.
- Cursor pagination should use stable keys such as `(updated_at, id)` or `(canonical_name, id)` depending on resolver order.
- `EraBucket` is derived from `start_date`; it is not stored in the current SQLite schema.
- A root-to-depth genealogy query should return fewer than `depth` hops when the stored graph has no further edges.

GraphQL が REST より優位な操作: 組織を起点に、機能・活動・関係・イベント・temporal facet・各 claim と source を一度の nested query で取得し、過取得や複数往復を避けながら、出典付きの系譜ビューをクライアントごとの粒度で組み立てられる。
