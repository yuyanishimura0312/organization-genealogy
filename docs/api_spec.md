# Organization Genealogy REST API Draft

Status: design draft for Phase 6 / v0.7 or later. This document is not an implementation contract for the current SQLite sandbox.

Public responses MUST expose only records and fields backed by `source.redistribution = 'public_redistributable'`. Private API keys MAY enable non-public records in later deployments, but the default public surface is claim-gated.

```yaml
openapi: 3.1.0
info:
  title: Organization Genealogy API
  version: 0.7-draft
  description: >
    REST API draft for claim-based organization genealogy analysis.
    Public endpoints return only records and fields whose backing claims are tied to
    source.redistribution = public_redistributable.
servers:
  - url: /
security: []
tags:
  - name: Organizations
  - name: Relations
  - name: Genealogy
  - name: Taxonomy
  - name: Sources
paths:
  /v1/organizations:
    get:
      tags: [Organizations]
      summary: List organizations
      description: >
        Returns organizations visible through public-redistributable claims.
        Filters are conjunctive. era matches organizations active or valid during the given year or date.
      parameters:
        - $ref: "#/components/parameters/Era"
        - $ref: "#/components/parameters/Status"
        - $ref: "#/components/parameters/Form"
        - $ref: "#/components/parameters/Page"
        - $ref: "#/components/parameters/Limit"
      responses:
        "200":
          description: Paginated organization list.
          headers:
            X-RateLimit-Limit:
              $ref: "#/components/headers/RateLimitLimit"
            X-RateLimit-Remaining:
              $ref: "#/components/headers/RateLimitRemaining"
            X-RateLimit-Reset:
              $ref: "#/components/headers/RateLimitReset"
          content:
            application/json:
              schema:
                allOf:
                  - $ref: "#/components/schemas/PageEnvelope"
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: "#/components/schemas/OrganizationSummary"
        "400":
          $ref: "#/components/responses/BadRequest"
        "429":
          $ref: "#/components/responses/RateLimited"
  /v1/organizations/{id}:
    get:
      tags: [Organizations]
      summary: Get one organization
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
      responses:
        "200":
          description: Organization detail.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OrganizationDetail"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/organizations/{id}/functions:
    get:
      tags: [Organizations]
      summary: List function records for one organization
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
      responses:
        "200":
          description: Function records.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/FunctionRecord"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/organizations/{id}/activities:
    get:
      tags: [Organizations]
      summary: List activities for one organization
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
      responses:
        "200":
          description: Activities.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Activity"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/organizations/{id}/relations:
    get:
      tags: [Organizations, Relations]
      summary: List incoming and outgoing relations for one organization
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
        - $ref: "#/components/parameters/RelationType"
      responses:
        "200":
          description: Relations involving the organization.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Relation"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/organizations/{id}/events:
    get:
      tags: [Organizations]
      summary: List events involving one organization
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
      responses:
        "200":
          description: Events linked through event_organization.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Event"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/organizations/{id}/temporal-facets:
    get:
      tags: [Organizations]
      summary: List temporal facets for one organization
      description: Phase 4+ endpoint backed by organization_temporal_facet.
      parameters:
        - $ref: "#/components/parameters/OrganizationId"
        - name: facet_type
          in: query
          schema:
            $ref: "#/components/schemas/FacetType"
        - name: at
          in: query
          description: ISO 8601 date; returns facets valid at this instant.
          schema:
            type: string
            format: date
      responses:
        "200":
          description: Temporal facet records.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/TemporalFacet"
        "404":
          $ref: "#/components/responses/NotFound"
  /v1/relations:
    get:
      tags: [Relations]
      summary: List relations
      parameters:
        - $ref: "#/components/parameters/RelationType"
        - name: source_organization_id
          in: query
          schema:
            type: string
        - name: target_organization_id
          in: query
          schema:
            type: string
        - $ref: "#/components/parameters/Page"
        - $ref: "#/components/parameters/Limit"
      responses:
        "200":
          description: Paginated relation list.
          content:
            application/json:
              schema:
                allOf:
                  - $ref: "#/components/schemas/PageEnvelope"
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: "#/components/schemas/Relation"
  /v1/genealogy/network:
    get:
      tags: [Genealogy]
      summary: Get a graph projection
      description: Returns nodes and edges for visualization or network analysis.
      parameters:
        - name: root_organization_id
          in: query
          schema:
            type: string
        - name: relation_type
          in: query
          schema:
            $ref: "#/components/schemas/RelationType"
        - name: depth
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 5
            default: 2
        - name: direction
          in: query
          schema:
            type: string
            enum: [outgoing, incoming, both]
            default: both
      responses:
        "200":
          description: Network projection.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Network"
  /v1/function-types:
    get:
      tags: [Taxonomy]
      summary: List function taxonomy records
      responses:
        "200":
          description: Function types.
          content:
            application/json:
              schema:
                type: object
                required: [data]
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/FunctionType"
  /v1/sources:
    get:
      tags: [Sources]
      summary: List public-redistributable sources
      parameters:
        - name: source_type
          in: query
          schema:
            $ref: "#/components/schemas/SourceType"
        - $ref: "#/components/parameters/Page"
        - $ref: "#/components/parameters/Limit"
      responses:
        "200":
          description: Paginated source list.
          content:
            application/json:
              schema:
                allOf:
                  - $ref: "#/components/schemas/PageEnvelope"
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: "#/components/schemas/Source"
  /v1/sources/{id}/claims:
    get:
      tags: [Sources]
      summary: List claims from one public-redistributable source
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
        - $ref: "#/components/parameters/Page"
        - $ref: "#/components/parameters/Limit"
      responses:
        "200":
          description: Claims linked to the source.
          content:
            application/json:
              schema:
                allOf:
                  - $ref: "#/components/schemas/PageEnvelope"
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: "#/components/schemas/Claim"
        "404":
          description: Source not found or not public-redistributable.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: Required only for future private endpoints or private data access.
  headers:
    RateLimitLimit:
      description: Requests allowed per rolling minute.
      schema:
        type: integer
        const: 60
    RateLimitRemaining:
      description: Remaining requests in the current window.
      schema:
        type: integer
        minimum: 0
    RateLimitReset:
      description: Unix timestamp when the current limit window resets.
      schema:
        type: integer
  parameters:
    OrganizationId:
      name: id
      in: path
      required: true
      schema:
        type: string
    Era:
      name: era
      in: query
      description: Year, ISO date, or period label interpreted by the service.
      schema:
        type: string
        examples: ["1700", "1602-03-20"]
    Status:
      name: status
      in: query
      schema:
        $ref: "#/components/schemas/OrgStatus"
    Form:
      name: form
      in: query
      description: organization_form.form_code or organization_form.form_id.
      schema:
        type: string
    RelationType:
      name: relation_type
      in: query
      schema:
        $ref: "#/components/schemas/RelationType"
    Page:
      name: page
      in: query
      schema:
        type: integer
        minimum: 1
        default: 1
    Limit:
      name: limit
      in: query
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 50
  responses:
    BadRequest:
      description: Invalid request parameters.
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    NotFound:
      description: Entity not found in the public API surface.
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    RateLimited:
      description: Rate limit exceeded. Public limit is 60 requests per minute.
      headers:
        Retry-After:
          description: Seconds until retry is allowed.
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
  schemas:
    PageEnvelope:
      type: object
      required: [data, page, limit, total]
      properties:
        data:
          type: array
          items: {}
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
    Error:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message]
          properties:
            code:
              type: string
            message:
              type: string
    OrgStatus:
      type: string
      enum: [active, dormant, transformed, merged, split, extinct, unknown]
    DatePrecision:
      type: string
      enum: [exact, year, decade, century, period, before, after, unknown]
    SourceType:
      type: string
      enum: [primary_text, secondary_literature, dataset, interview, archive, artifact, onchain, web, oral_history, ethnography]
    ClaimValueKind:
      type: string
      enum: [present, absent, partial, unknown, inapplicable]
    RelationType:
      type: string
      enum:
        - alliance
        - competition
        - control
        - subsidiary
        - partnership
        - membership
        - succession
        - spin_off
        - merger
        - acquisition
        - trade
        - funding
        - shareholding
        - knowledge_transfer
        - mimetic_isomorphism
        - normative_pressure
        - coercive_pressure
        - protocol_dependency
        - supply_chain
        - interlocking_directorate
        - patronage
        - rivalry
        - schism
        - unknown
    EventType:
      type: string
      enum: [founding, dissolution, merger, acquisition, split, spin_off, renaming, relocation, reform, crisis, governance_change, platform_shift, ipo, privatization, nationalization, dormancy_start, dormancy_end, revival, reorganization, unknown]
    FacetType:
      type: string
      enum: [membership, governance, resource_base, territory, technology, identity, scale, legitimation_basis]
    ClaimRef:
      type: object
      required: [claim_id, source_id, confidence]
      properties:
        claim_id:
          type: string
        source_id:
          type: string
        confidence:
          type: number
          minimum: 0
          maximum: 1
    OrganizationSummary:
      type: object
      required: [organization_id, canonical_name, status, claims]
      properties:
        organization_id:
          type: string
        canonical_name:
          type: string
        alternate_names:
          type: array
          items:
            type: object
        description:
          type: string
        primary_form_id:
          type: string
        status:
          $ref: "#/components/schemas/OrgStatus"
        start_date:
          type: string
          format: date
        start_date_precision:
          $ref: "#/components/schemas/DatePrecision"
        end_date:
          type: string
          format: date
        end_date_precision:
          $ref: "#/components/schemas/DatePrecision"
        geo_scope:
          type: object
        external_ids:
          type: object
        claims:
          type: array
          items:
            $ref: "#/components/schemas/ClaimRef"
    OrganizationDetail:
      allOf:
        - $ref: "#/components/schemas/OrganizationSummary"
        - type: object
          properties:
            attributes:
              type: object
            forms:
              type: array
              items:
                $ref: "#/components/schemas/OrganizationFormAssignment"
    OrganizationFormAssignment:
      type: object
      properties:
        assignment_id:
          type: string
        form:
          $ref: "#/components/schemas/OrganizationForm"
        valid_from:
          type: string
          format: date
        valid_to:
          type: string
          format: date
        is_primary:
          type: boolean
        confidence:
          type: number
    OrganizationForm:
      type: object
      properties:
        form_id:
          type: string
        taxonomy_name:
          type: string
        form_code:
          type: string
        label:
          type: string
        parent_form_id:
          type: string
        definition:
          type: string
    FunctionType:
      type: object
      required: [function_type_id, name_ja, name_en, source_framework, definition]
      properties:
        function_type_id:
          type: string
        name_ja:
          type: string
        name_en:
          type: string
        source_framework:
          type: string
          enum: [miller_living_systems, beer_vsm, compound]
        miller_subsystem_no:
          type: integer
        vsm_system_no:
          type: string
        parent_function_type_id:
          type: string
        definition:
          type: string
        observable_indicators:
          type: array
          items: {}
        era_examples:
          type: array
          items: {}
    FunctionRecord:
      type: object
      required: [function_id, organization_id, function_type_id]
      properties:
        function_id:
          type: string
        organization_id:
          type: string
        function_type_id:
          type: string
        function_type:
          $ref: "#/components/schemas/FunctionType"
        mechanism:
          type: object
        beneficiaries:
          type: object
        dependency:
          type: object
        activity_id:
          type: string
        valid_from:
          type: string
          format: date
        valid_to:
          type: string
          format: date
        confidence:
          type: number
        claim:
          $ref: "#/components/schemas/ClaimRef"
    Activity:
      type: object
      required: [activity_id, organization_id, activity_type, orientation]
      properties:
        activity_id:
          type: string
        organization_id:
          type: string
        activity_type:
          type: string
        domain:
          type: string
        description:
          type: string
        inputs:
          type: object
        outputs:
          type: object
        scale:
          type: object
        orientation:
          type: string
          enum: [exploration, exploitation, mixed, unspecified]
        valid_from:
          type: string
          format: date
        valid_to:
          type: string
          format: date
        confidence:
          type: number
        claim:
          $ref: "#/components/schemas/ClaimRef"
    Relation:
      type: object
      required: [relation_id, source_organization_id, target_organization_id, relation_type, directionality]
      properties:
        relation_id:
          type: string
        source_organization_id:
          type: string
        target_organization_id:
          type: string
        source_organization:
          $ref: "#/components/schemas/OrganizationSummary"
        target_organization:
          $ref: "#/components/schemas/OrganizationSummary"
        relation_type:
          $ref: "#/components/schemas/RelationType"
        directionality:
          type: string
          enum: [directed, undirected, bidirectional]
        valid_from:
          type: string
          format: date
        valid_to:
          type: string
          format: date
        strength:
          type: number
          minimum: 0
          maximum: 1
        strength_basis:
          type: string
        relation_attributes:
          type: object
        confidence:
          type: number
        claim:
          $ref: "#/components/schemas/ClaimRef"
    Event:
      type: object
      required: [event_id, event_type, event_date_precision]
      properties:
        event_id:
          type: string
        event_type:
          $ref: "#/components/schemas/EventType"
        event_date:
          type: string
          format: date
        event_date_precision:
          $ref: "#/components/schemas/DatePrecision"
        description:
          type: string
        participants:
          type: object
        causes:
          type: object
        outcomes:
          type: object
        location:
          type: object
        dissolution_cause:
          type: string
          enum: [bankruptcy, merger_into_other, split_into_others, voluntary_wind_down, regulatory_dissolution, war_destruction, religious_schism, political_purge, natural_disaster, succession_failure, obsolescence, absorption, transformation, unknown]
        vsr_label:
          type: string
          enum: [variation, selection, retention, struggle]
        confidence:
          type: number
        claim:
          $ref: "#/components/schemas/ClaimRef"
    TemporalFacet:
      type: object
      required: [organization_facet_id, organization_id, facet_type, facet_value]
      properties:
        organization_facet_id:
          type: string
        organization_id:
          type: string
        valid_from:
          type: string
          format: date
        valid_to:
          type: string
          format: date
        facet_type:
          $ref: "#/components/schemas/FacetType"
        facet_value:
          type: object
        confidence:
          type: number
        claim:
          $ref: "#/components/schemas/ClaimRef"
    Source:
      type: object
      required: [source_id, source_type, title, redistribution]
      properties:
        source_id:
          type: string
        source_type:
          $ref: "#/components/schemas/SourceType"
        title:
          type: string
        authors:
          type: array
          items: {}
        publication_date:
          type: string
        publisher:
          type: string
        locator:
          type: object
        accessed_at:
          type: string
          format: date-time
        reliability_score:
          type: number
          minimum: 0
          maximum: 1
        reliability_basis:
          type: string
        bias_notes:
          type: string
        license:
          type: string
        redistribution:
          type: string
          const: public_redistributable
    Claim:
      type: object
      required: [claim_id, entity_type, entity_id, value_kind, source_id, confidence]
      properties:
        claim_id:
          type: string
        entity_type:
          type: string
        entity_id:
          type: string
        field_path:
          type: string
        value_kind:
          $ref: "#/components/schemas/ClaimValueKind"
        claim_value:
          type: object
        source_id:
          type: string
        confidence:
          type: number
          minimum: 0
          maximum: 1
        interpretation_note:
          type: string
        recorded_at:
          type: string
          format: date-time
        superseded_by:
          type: string
    Network:
      type: object
      required: [nodes, edges]
      properties:
        nodes:
          type: array
          items:
            $ref: "#/components/schemas/OrganizationSummary"
        edges:
          type: array
          items:
            $ref: "#/components/schemas/Relation"
        meta:
          type: object
          properties:
            root_organization_id:
              type: string
            depth:
              type: integer
            relation_type:
              $ref: "#/components/schemas/RelationType"
            direction:
              type: string
```

## Cross-cutting decisions

- Public authentication: no authentication required for public data.
- Private authentication: future private access uses `X-API-Key`; private endpoints or private query modes must declare `security: [{ ApiKeyAuth: [] }]`.
- Rate limit: 60 requests per minute per client identity. Responses include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`; 429 returns `Retry-After`.
- Public data gate: public responses return only claims whose source is `public_redistributable`; entities without at least one visible claim may be omitted from public detail surfaces.
- Temporal semantics: `era` and `at` use interval overlap against `start_date/end_date`, `valid_from/valid_to`, or Phase 4 `organization_temporal_facet`.
