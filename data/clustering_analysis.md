# Function Vector Clustering Analysis

## Scope

This analysis uses `data/clustering_results.json`, generated from `data/og.db` by `etl/21_function_clustering.py`.

Important limitation: the task text expected 18 organizations and an 18x18 matrix, but the current SQLite database returns 43 organizations for the specified query. The script therefore outputs a 43x43 matrix over the full 25 function dimensions. The interpretation below is limited to the current database state and should not be read as a validated typology.

The feature vector is binary: a function is either recorded for an organization or not. It ignores confidence, source density, temporal phase, scale, geography, legal form, and direction of influence.

## Clustering Behavior

Single linkage is dominated by chaining. At height 0.50 it collapses 39 of 43 organizations into one large cluster, leaving only four singletons. This is useful for finding bridges but weak for typological interpretation.

Complete linkage remains more interpretable. At height 0.75 it yields 10 clusters, including:

- Public-voice and advocacy cluster: Anonymous, Black Panther Party, ICRC, United Nations. Shared functions emphasize boundary, output/input transduction, policy identity, and decision or coordination functions.
- Open-source / identity-governance cluster: Haudenosaunee Confederacy, Linux Kernel Community, MakerDAO, Wikimedia Foundation, Asante Empire. This is structurally striking because it joins historical confederacy, protocol governance, and knowledge commons through decider, memory, boundary, and policy identity.
- Reproductive institutional continuity cluster: Toyota, Al-Azhar, Naqshbandi Tariqa, Benedictines, University of Bologna, Roman collegia, Mitsui, Andong Kwon Munjung, Mount Hiei. Shared functions emphasize reproducer, memory, boundary, and policy identity.
- Administrative extraction / allocation cluster: Egyptian vizier, Ottoman Timar, VOC, Mughal Mansabdari, Sakai Egoshu. Shared functions emphasize ingestor, distributor, decider, memory, and internal control.
- Network coordination cluster: Grameen Bank, Hanseatic League, Vietnamese village compact, Shanxi merchants. Shared functions emphasize boundary, coordination, channel/net, and identity.
- Production and mutual-support cluster: Mondragon, SEWA, Suleymaniye Kulliyesi, Kyocera, Konike house. This cluster mixes cooperative enterprise, welfare-complex, corporation, and merchant house because the vectors foreground reproduction, ingestion, production, identity, and control more than legal form.

At height 0.50 complete linkage identifies tighter cores:

- Haudenosaunee Confederacy, MakerDAO, Wikimedia Foundation, and Linux Kernel Community cluster around memory, decider, boundary, channel/net or policy identity.
- Al-Azhar, Benedictines, Roman collegia, Mitsui, Andong Kwon Munjung, and Mount Hiei cluster around institutional reproduction and memory.
- Egyptian vizier, Ottoman Timar, and Mughal Mansabdari form a compact administrative-control cluster.

The zero-distance pairs are not necessarily historical analogues. They mean only that the current function annotations are identical. Examples include Haudenosaunee Confederacy and MakerDAO, and the trio Mitsui / Andong Kwon Munjung / Mount Hiei.

## Comparison With Existing Typologies

Mintzberg-style structural types separate machine bureaucracy, professional bureaucracy, divisionalized form, adhocracy, and simple structure. The function clustering cuts across those categories. For example, Toyota, Al-Azhar, Benedictines, and Roman collegia do not share a Mintzberg form, but they cluster through reproduction, memory, identity, and boundary maintenance.

Hannan and Freeman's organizational ecology focuses on population selection, niche, inertia, and founding conditions. The clustering does not model population-level selection. It instead groups organizations by recorded functional repertoire, so it can place historically unrelated organizations together when they solve similar control, reproduction, or memory problems.

Laloux-style categories emphasize worldview and management consciousness. The vector approach does not encode consciousness, culture, hierarchy depth, or deliberative quality. MakerDAO and Haudenosaunee Confederacy can become identical in this representation despite very different cosmologies and governance traditions.

## Structures Not Captured By Existing Typologies

The main structure not well captured by standard typologies is cross-era functional convergence. The method groups organizations by what system functions are present, not by legal form, epoch, ownership, ideology, or scale.

Three patterns stand out:

- Memory plus identity as a durable-organizing core. Monastic orders, kinship groups, universities, merchant houses, and corporations converge when reproduction and memory are both annotated.
- Boundary plus decision as a governance-interface pattern. Commons, confederacies, and protocol-like organizations converge even when their authority mechanisms differ.
- Ingestion, distribution, decider, and internal control as an administrative-extraction pattern. Imperial and commercial arrangements converge despite different formal institutions.

## Limits

The result is annotation-sensitive. Many vectors have only 3 to 6 active functions out of 25, so one added or removed function can materially change Jaccard distance.

The current database has 43 annotated organizations, not the requested 18. If the intended sample is a fixed 18-case subset, it needs an explicit selection rule before drawing stronger conclusions.

The analysis is exploratory. It should be treated as a clustering trial for hypothesis generation, not as evidence that the organizations are historically equivalent.
