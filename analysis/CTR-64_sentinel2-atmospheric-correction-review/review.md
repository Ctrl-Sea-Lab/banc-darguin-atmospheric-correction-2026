## Executive summary

**Take-home message.** Retain the PI’s four processors—Sen2Cor, ACOLITE, POLYMER, and MAJA—and add **C2RCC** as the preferred fifth. This compares vegetation-constrained atmospheric retrieval, dark-spectrum fitting, joint water–atmosphere spectral fitting, temporal constraints, and neural-network inversion. It is a defensible experimental selection, not a performance ranking for Banc d’Arguin.

**Meaningful results.** Sen2Cor and MAJA overlap in land-surface objectives and some spectral constraints, but MAJA’s temporal information makes both worth retaining. ACOLITE and POLYMER target aquatic reflectance through different inverse problems. C2RCC adds trained inversion of coupled water–atmosphere simulations and a public local implementation through SNAP. The recommended set has two land-oriented references and three aquatic approaches. Network variants and ACOLITE configurations are sensitivity treatments within processors, not independent processors. This recommendation is the reviewer’s interpretation of the evidence below.

**Issues and limitations.** No imagery was processed, atmospheric processor installed, or hardware benchmark run. No site-specific accuracy was established for Banc d’Arguin. Published comparisons often concern older software and different water types or references. POLYMER’s free terms restrict use to noncommercial research; iCOR’s current package terms and compatibility were not obtained; the current MAJA GitLab returned an access challenge. Independent scientific review and PI disposition remain pending. The protected root bibliography awaits synchronization.

**Implications and next steps.** Recommend **Sen2Cor + ACOLITE + POLYMER + MAJA + C2RCC** for a later, separately authorized comparison. Use **iCOR as a conditional water/shoreline fallback**, after package, terms, and compatibility verification. If access fails, SIAC is a publicly inspectable **land-focused alternative**, not an equivalent aquatic replacement. A PI decision to prioritize exposed vegetation could favor SIAC as fifth. Test ACOLITE DSF primarily, with TSDSF + RAdCor as a separate adjacency sensitivity treatment. Validate water, exposed sediment, exposed vegetation, and shoreline mixtures separately.

## Question, scope, and evidence

### Objectives and study domain

Which five locally executable Sentinel-2 atmospheric correction processors provide useful methodological diversity for coastal waters, intertidal habitats, exposed sediments, and exposed coastal vegetation? This review preserves the PI’s four selected processors and recommends a fifth. It assesses feasibility of a future experiment, not installation permission or demonstrated performance on the PI’s computer.

Banc d’Arguin is the intended application area. No local field observations, scenes, tide series, aerosol records, or habitat labels were supplied for this review. Mineral dust, bright neighboring surfaces, changing inundation, shallow-bottom reflectance, and vegetation exposure are **conditions to investigate**, not measured explanations or established local processor failures. No ecological result is inferred from software design.

### Search, verification, and selection

The search date was **20 October 2026**. This is a **structured critical review**, not a preregistered systematic review. Discovery combined targeted web searches, Crossref and OpenAlex APIs, publishers, institutional repositories, official documentation, and developer repositories. A Semantic Scholar API search returned HTTP 429. Searches combined processor names and MSI/Sentinel-2 with aerosol retrieval, mineral dust, adjacency, sunglint, coastal/turbid/shallow waters, intertidal exposure, mudflat, seagrass, and vegetation. Queries and source outcomes accompany the report.

Priority went to algorithm descriptions, current implementation evidence, and comparisons with traceable radiometric references. Sources without verifiable identity, detailed claims supported only by an abstract, and statistics without a clear sensor/reference/configuration were not used for detailed conclusions. Citation chaining from ACIX-Aqua, ACIX-II Land and developer bibliographies identified foundational and recent sources. Intertidal-specific coverage is weaker than land and aquatic validation; inaccessible services prevent an exhaustive coverage claim.

Crossref metadata were compared with full-text first pages or publisher records. OpenAlex supplied identifiers and lawful repository leads. Relevant methods and conclusions were inspected in retrieved papers. Failed PDF requests were retained as access failures, never labeled full text. The original 2011 POLYMER paper remains metadata/abstract verified in this library; detailed implementation claims instead use developer documentation and inspected comparison studies. PDFs are retained locally and excluded from Git and the transfer archive. Downloading a paper alone is not equivalent to evaluating its findings.

The claim table distinguishes **literature findings**, **documented capabilities**, and **reviewer interpretations/recommendations**. Retrieval logs record URLs, dates, content hashes and outcomes. No numerical accuracy statistic is attributed to a local experiment.

### Quantitative context

{{< include tables/coverage.md >}}

Warren et al. compared six processors using Sentinel-2A, with **521 matchups common to all processors**. Coastal and inland matching windows differed: **±3 h** and **±24 h**, respectively. Their Baltic, Western Channel and inland datasets do not establish Banc d’Arguin accuracy. Coverage and timing affect interpretation alongside correction error. [@Warren2019, Methods and Conclusions]

ACIX-II Land’s common comparison included **79 Sentinel-2 sites and 62 Landsat-8 sites**. It used radiative-transfer-derived surface references and field radiometric observations, which have different independence and representativeness. Its land results cannot establish aquatic Rrs accuracy. [@Doxani2023, Abstract and Methods]

No pooled error, effect size, or meta-analytic ranking is calculated. Pooling would combine incompatible outputs, versions, matchups and surface domains. No performance figure is generated because no harmonized benchmark dataset was assembled.

## Physical foundations and selected processors

### Distinguish the forward model from the inverse problem

The forward model predicts a sensor signal from atmosphere, illumination, surface and viewing geometry. Inversion estimates atmospheric and surface properties from observations. Radiative-transfer engines, lookup tables, optimization, and surface priors are separate choices. Different engines can support similar dark-target assumptions; shared physics can support very different temporal or spectral constraints. Shared radiative transfer alone does not establish redundancy.

{{< include tables/method_matrix.md >}}

The matrix describes documented families and inspected configurations. “Correction” means an explicit retrieval operation: masking, flagging, or tolerating contamination does not demonstrate its removal.

### Sen2Cor

The reviewed standalone release is **2.13.02**, released **24 September 2026**. ESA lists PSD **15.2** and several preceding specifications, and improved use of CAMS aerosol information over water. Its default configuration corresponds to ground-segment baseline **05.13**, although standalone output has a distinct baseline label. These are documented software changes, not independent demonstrations of improved local accuracy. [ESA release page](https://step.esa.int/main/snap-supported-plugins/sen2cor/sen2cor-v2-13/)

Sen2Cor retrieves surface reflectance with **libRadtran lookup tables**. Dense dark vegetation constrains aerosol optical thickness (AOT); CAMS supports fallback when suitable vegetation is absent. The manual offers rural, maritime, or automatic aerosol selection. Choosing between available models does not guarantee representation of arbitrary mineral-dust mixtures. Water vapor uses absorption information; ozone and other atmospheric quantities use auxiliary/configuration information. Cloud, shadow, snow, cirrus, terrain and surface processing accompany atmospheric correction. DEM and ESA CCI products improve classification and core-like processing. [2.13.02 manual, §§2.2–2.3](https://step.esa.int/thirdparties/sen2cor/2.13.0/docs/OMPC.TPZ.SUM.004%20-%20i1r0%20-%20Sen2Cor%202.13.02%20Configuration%20and%20User%20Manual.pdf)

The linked **2.10 ATBD** describes adjacency correction using a neighborhood approximation. That establishes capability, not identical behavior in every later executable/configuration. The current manual also describes an expert setting concerning suppression of a reflectance-retrieval step: retain distributed calibration files before claiming adjacency is enabled by default. Neither “no adjacency treatment” nor “equivalent to RAdCor” is justified. Cirrus and terrain operations are not sunglint or whitecap removal; a dedicated water-glint retrieval was not established here. [ATBD, §§4.5–4.7](https://step.esa.int/thirdparties/sen2cor/2.10.0/docs/S2-PDGS-MPC-L2A-ATBD-V2.10.0.pdf)

Input is intact **L1C SAFE** with geometry and metadata, not an L2A raster. Output includes surface reflectance, AOT, water vapor, scene classification and quality information at supported resolutions. The input–output document identifies the surface quantity as hemispherical-directional reflectance factor. Read quantification values and offsets from metadata. Water classification does not turn land surface reflectance into aquatic Rrs. [2.13.02 input–output definition, §§2.1–2.3](https://step.esa.int/thirdparties/sen2cor/2.13.0/docs/OMPC.TPZG.IOD.004%20-%20i1r0%20-%20Sen2Cor%202.13.02%20Input%20Output%20Data%20Definition.pdf)

**Interpretation:** retain Sen2Cor for exposed surfaces and as the operational reference. Inspect aerosol fallback provenance over water or vegetation-poor scenes; its AOT map is not necessarily an independently retrieved fine-scale aerosol measurement. Historical aquatic comparisons cannot quantify the effect of the September 2026 changes.

### ACOLITE

The developer API returned release **20260421.0**. A main-branch snapshot was also inspected and hashed; it is not assumed identical to released binaries. ACOLITE offers Python source and distributed binaries with MSI support. Required atmospheric LUTs are retrieved separately on demand, so cache them before offline work. [Developer repository](https://github.com/acolite/acolite), [release](https://github.com/acolite/acolite/releases/tag/20260421.0)

**Dark Spectrum Fitting (DSF)** infers path reflectance from dark observations across bands and selects aerosol-model/AOT combinations using LUTs. Darkness need not occur at the same pixel in every band. It assumes adequate near-dark observations and sufficiently uniform atmosphere within each estimation region. Tiling permits spatial variation but makes estimator, band and neighborhood choices consequential. The 2019 MSI/Landsat formulation used continental and maritime aerosol models and evaluated optional glint correction; that finite model family does not guarantee dust accuracy. [@Vanhellemont2019, §2]

The inspected defaults specify tiled AOT estimation and **disable residual-glint and generic adjacency correction**. Exponential extrapolation, DSF, and **TOA–surface DSF (TSDSF) + RAdCor** are different configurations. RAdCor uses atmospheric spatial kernels, while TSDSF accounts for neighborhood contributions in aerosol estimation. Those capabilities must not be credited to ordinary DSF output. [Settings](https://github.com/acolite/acolite/blob/main/config/defaults.txt), [RAdCor ATBD](https://github.com/acolite/radcor_atbd)

Castagna and Vanhellemont evaluated TSDSF + RAdCor over small Belgian inland waters with Landsat and MSI. Improvements depended on wavelength; this is not evidence of superiority over every band or habitat. They recommend adequate surrounding image area and caution with partially cloudy scenes. Adjacency-aware retrieval is therefore a useful shoreline sensitivity treatment, but cannot recover a genuinely mixed pixel as pure water. [@Castagna2025, §§4–5]

Image-based aerosol retrieval does not remove gas, pressure, interface or wind assumptions. Log gas correction and glint separately. Optional land/cloud masks and terrain/shadow tools are distinct from atmospheric correction; no configuration automatically includes every module. No general whitecap-removal guarantee was established. Over exposed surfaces, water-specific residual-glint treatment may be inappropriate.

Scientific outputs include dimensionless `rhos` and requested Rrs products, normally in NetCDF. The developer states the aquatic convention `ρs = π Rrs`; it must not be applied indiscriminately to other processors’ products. **Interpretation:** ACOLITE provides useful within-processor experiments on dark spectra, glint and adjacency, with a corresponding need to archive effective settings and valid coverage.

### POLYMER

The inspected changelog identifies **v4.17 (12 November 2025)** and a coexisting **v5 preview** framework. A preview must not silently substitute for a specified v4 experiment. Source availability is governed by **POLYMER licence v2.0**: free use is restricted to noncommercial scientific purposes; commercial use requires contacting HYGEOS. This review neither accepts terms nor determines the laboratory’s use classification. [Changelog](https://github.com/hygeos/polymer/blob/master/CHANGELOG.TXT), [terms](https://github.com/hygeos/polymer/blob/master/LICENCE.TXT)

POLYMER applies physical atmospheric precorrections and jointly fits a water-reflectance model and smooth spectral residual atmospheric/glint terms. It does not infer the entire atmosphere from a near-black spectrum as DSF does, or execute a trained inverse mapping as C2RCC does. Its original paper concerns MERIS, so that source alone cannot validate MSI. Detailed statements here rely on inspected documentation and comparison descriptions. [@Steinmetz2011; @Warren2019; HYGEOS overview](https://hygeos.com/en/polymer/)

The inspected MSI reader supports A/B/C, handles radiometric offsets and retains L1C granule/product metadata. Its default resolution is **60 m**; choose and record finer support explicitly. Ancillary routes include NASA files or embedded ECMWF information, with configurable land masks and elevation. The reader’s default alone does not impose a land mask. Successful execution over unmasked land does not establish validity of a water model there. [MSI reader](https://github.com/hygeos/polymer/blob/master/polymer/level1_msi.py)

The v4 route uses Python/Cython, compiled components, static auxiliary files, meteorology and optional multiprocessing. Experimental complex-water settings and optional uncertainty propagation are documented; neither is a generic default or an independent validation. Assess water-model mismatch, precorrection error, contamination and optimization failures using flags and residuals. Explicit spatial adjacency correction equivalent to RAdCor was not established: smooth spectral fitting does not demonstrate correct reconstruction of neighborhood radiance. [README](https://github.com/hygeos/polymer), [ancillary code](https://github.com/hygeos/polymer/blob/master/polymer/ancillary.py)

**Interpretation:** retain POLYMER as an aquatic contrast under glint. Exposed sediment, vegetation, and shallow-bottom spectra may violate its surface model. Preserve water-reflectance normalization and BRDF settings; plausible spectra or successful optimization do not establish correct bottom/water/aerosol attribution.

### MAJA

CESBIO describes **4.10.0** support for CAMS **49r1** and Sentinel-2C and subsequent **4.11.0/4.12.0** changes primarily associated with Trishna. This review pins the documented 4.x behavior; a newer GitLab release was not verified because the active repository returned an access challenge. MAJA is documented as open source under Apache terms since 4.2; the archived CNES project identifies Apache-2.0. [CESBIO](https://www.cesbio.cnrs.fr/maja/), [CNES archive](https://github.com/CNES/MAJA)

MAJA combines multispectral aerosol constraints with repeated observations. Temporal constraints require sufficient surface stability over useful reference pixels; spectral constraints help when temporal information is weak. The foundational study evaluated FormoSat-2 and Landsat time series, so it is methodological evidence rather than direct MSI coastal validation. Operational MAJA adds cloud/shadow screening and atmospheric/surface processing. Aerosol properties can use optional CAMS information or a configured model. [@Hagolle2015MAJA, Methods and Conclusions; @Doxani2023, Table 1]

**One-scene execution is possible but does not test the intended temporal advantage.** CESBIO documents `init` mode using multispectral criteria when only one L1C is supplied and discourages it as standard usage. `startmaja` normally builds backward initialization followed by forward nominal processing. Its documented default uses **eight L1C products** for backward processing. Valid previous L2A state can support restart, subject to temporal-gap rules. Eight arbitrary scenes do not guarantee usable initialization. [Startmaja](https://www.cesbio.cnrs.fr/maja/running-maja-with-start_maja/)

Required inputs include intact geometry/metadata, sensor-specific **GIPP** parameters/LUTs and a formatted terrain model. CAMS is optional in the wrapper but potentially important when aerosol composition differs from the continental model. Match CAMS release/date to LUTs. Cache terrain, masks, GIPP and atmospheric inputs; retain the workplan. Adjacency/terrain operations are version/configuration sensitive: CESBIO reports an adjacency-filter implementation fix in 4.9.3. [Terrain utility](https://www.cesbio.cnrs.fr/maja/the-dtmcreation-tool/), [release information](https://www.cesbio.cnrs.fr/maja/)

Outputs are land reflectances, atmospheric/geophysical information and quality bitmasks. Surface and terrain-corrected variants must remain distinct; bitmasks are not single class labels. A water mask does not establish an aquatic retrieval, and dedicated sunglint/whitecap correction was not established. **Interpretation:** retain MAJA for exposed-surface time series and test whether changing inundation undermines reference-pixel stability. Report `init` separately from temporal processing.

### Are the selected pairs redundant?

Sen2Cor/MAJA overlap most in target quantity and land constraints. Keeping both tests whether temporal information changes stability, coverage and exposed-surface consistency relative to a single-scene reference. They are not independent tests of every assumption: both may suffer from inadequate aerosol models or usable surface constraints.

ACOLITE/POLYMER share an aquatic objective and some precorrections but impose different spectral constraints. A neighborhood dark spectrum is not equivalent to fitting a constrained water spectrum. Shared radiometric, gas, glint and aerosol errors may remain. C2RCC adds a trained inversion while retaining physical priors. Processor spread measures method sensitivity, not a calibrated uncertainty interval or a set of independent ensemble members.

## Alternatives and fifth recommendation

### C2RCC and its MSI networks: preferred fifth

C2RCC trains networks on coupled water–atmosphere simulations for atmospheric inversion and water optical-property retrieval. Its assumptions reside in atmospheric simulations, bio-optical parameter ranges/covariances and geometry; machine learning does not remove them. The SNAP specification describes gas/pressure handling and out-of-range/out-of-scope flags. [Specification](https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.opt.opttbx.c2rcc/c2rcc/C2RCCAlgorithmSpecification.html)

The community lists MSI **C2RCC-Nets, C2X-Nets, and C2X-COMPLEX-Nets**. Their domains differ; wider concentration ranges do not prove higher accuracy. The 2026 synthesis identifies shallow-bottom reflectance and strong glint among conditions outside its model. Much of that paper’s quantitative validation is for OLCI and cannot simply be transferred to MSI. Use MSI comparisons and record the exact network. [Network inventory](https://c2rcc.org/neural-nets/), [@Muller2026, §§2–4]

SNAP lists **14.0.0** installers and an **8 October 2026 announcement of 14.0.2 updates**. The Optical Toolbox source exposes `c2rcc.msi`, network choices, meteorological sources/defaults, flags and reflectance options. The inspected default is water-leaving reflectance (`outputAsRrs=false`); normalized and directional products differ. Water output bands in the inspected MSI algorithm are **B1–B7 and B8A**, not a full land VNIR–SWIR product. A source snapshot is not evidence of the exact module bundled in a particular installer. [Downloads](https://step.esa.int/main/download/snap-download/), [update](https://step.esa.int/main/snap-14-0-2-update-is-now-available/), [source](https://github.com/senbox-org/optical-toolbox/tree/master/opttbx-c2rcc)

**Decision:** C2RCC combines inversion diversity, public access, batch automation and an MSI validation history. Its costs are a water-only model domain and unresolved accuracy under bottom/glint/shoreline contamination. Register the standard network as a starting treatment and other networks as sensitivity tests; choose using independent validation, not post hoc favorable output.

### iCOR: conditional water/shoreline fallback

iCOR uses MODTRAN5 LUTs, image-based aerosol estimation and **SIMEC** adjacency correction over water. Its unified land–water workflow is attractive at boundaries. The foundational paper ignores direct sun glint and assumes low wind so foam/whitecap radiance can be neglected. SIMEC does not eliminate those assumptions. Field/AERONET-OC evidence and inland red-edge/NIR improvements support testing, without establishing universal superiority. [@DeKeukelaere2018, Methods and Validation]

VITO currently offers free basic SNAP plugins for MSI and other sensors, with standalone/operational use described. Its form requires contact details and sensor selection. No form was submitted or terms accepted. Current package version, exact license, source status, platforms and recent-baseline compatibility remain unverified. Free download is not equivalent to unrestricted open source. [VITO](https://remotesensing.vito.be/services/icor), [access form](https://remotesensing.vito.be/icor-download)

**Decision:** first conditional fallback for water/shoreline priorities, once access and compatibility pass. Its LUT/image-aerosol architecture overlaps the land references more than C2RCC does, while RAdCor already supplies an adjacency sensitivity treatment.

### SIAC: a land-focused alternative

SIAC combines Bayesian atmospheric estimation, CAMS priors, MODIS MCD43 surface information, spatial constraints and 6S-derived emulators, with propagated land-reflectance uncertainty. Its AERONET/RadCalNet and land validations do not validate aquatic Rrs. Coarse priors and changing tidal exposure need separate investigation. [@Yin2022SIAC, §§2–4]

Current documentation gives MSI Python/container routes, GDAL/LightGBM dependencies, DEM/atmosphere mirrors and a before/after observation window for MCD43. Its documented default acquisition route uses Google Earth Engine registration/authentication, with a non-GEE option. Latency, cached coverage and changing services affect reproducibility. The README labels the license GPLv3, while `LICENSE.md` contains **AGPLv3**; conservatively use the license file and resolve the inconsistency before redistribution. No account or terms were accepted. [SIAC](https://github.com/MarcYin/SIAC), [license](https://github.com/MarcYin/SIAC/blob/master/LICENSE.md)

**Decision:** favor SIAC if exposed vegetation/sediment and uncertainty characterization become the principal objective. It provides different priors from Sen2Cor/MAJA, but is not an equivalent aquatic fallback. The documented lack of terrain correction and absence of a demonstrated shoreline adjacency correction limit substitution.

### OC-SMART and exclusions

OC-SMART’s paper documents coupled atmosphere–ocean simulations, machine-learning retrievals, MSI support and Python/SNAP distribution. It overlaps C2RCC’s inversion family. The paper was obtained from an institutional site, but its software website failed access. Current terms, package/version, baseline support and distribution remain unresolved. Published availability is not proof of present deployability. Retain as reserve, not preferred fifth. [Fan et al.](https://doi.org/10.1016/j.rse.2020.112236)

A **6S/6SV engine or wrapper** is not an operational MSI processor without atmospheric retrieval, gas/aerosol inputs, spectral/geometry handling, masks and validation. A custom workflow adds development scope. **FLAASH/ATCOR** could add parameterization comparisons, but current paid access, license and MSI workflow were not established; purchases are outside scope. Exclusion here concerns present feasibility, not scientific quality.

{{< include tables/candidate_decision.md >}}

The qualitative matrix avoids unsupported numerical scoring. Aquatic relevance, distinct inversion, access and automation favor C2RCC. If both C2RCC compatibility and iCOR access fail, acknowledge that SIAC changes the comparison toward land or defer the aquatic fifth. No selected processor has been silently replaced.

## Practical local implementation

### Platforms, licenses and required inputs

The PI’s OS, architecture, RAM, cores, disk and account availability are unknown. A supported 64-bit Linux workstation offers the broadest common route. Windows has native Sen2Cor, ACOLITE and SNAP routes; MAJA needs a supported Linux route. SNAP lists Intel and ARM macOS installers, but that does not prove native ARM support for external processors. Check compiled POLYMER dependencies and MAJA binary architecture explicitly. No GPU requirement was identified for the reviewed routes.

{{< include tables/local_requirements.md >}}

**M** means mandatory for the specified route, **O** optional, and **R** recommended. Optional inputs can still materially change results. A fallback default and a measurement-constrained retrieval must remain distinct in the provenance.

| Input | Status and source | Offline/timing implication |
|---|---|---|
| L1C SAFE with metadata/angles | M for five; Copernicus Data Space Ecosystem, registered access where required | Keep original packaging, spacecraft, baseline, time and checksums. L2A is an output/reference, not interchangeable input. |
| LUTs/networks/static model files | M; ESA package, ACOLITE LUT repository, HYGEOS auxiliary package, MAJA GIPP collection, SNAP networks | Cache and hash exact versions; first-run downloads are not an offline workflow. |
| CAMS meteorology/aerosols | Sen2Cor fallback; MAJA O; SIAC M prior in its described method; embedded L1C where supported or ECMWF/Copernicus Atmosphere Data Store/mirrors | Check forecast/reanalysis type, date coverage, LUT compatibility and credentials. No current latency was measured. |
| Pressure/ozone/wind | Physical values M, but source/default route varies; embedded ECMWF or NASA ancillary in POLYMER, SNAP defaults/files, ACOLITE settings/ancillary | Record actual source and age. An external download is not mandatory for every supported route. |
| DEM and surface context | MAJA formatted terrain M; Sen2Cor R for core-like behavior; masks/elevation elsewhere configurable | Supported SRTM/Copernicus DEM and ESA CCI/GSW routes. Cache coverage. A static water mask may misrepresent tides. |
| MCD43 and emulators | SIAC method M; documented GEE/non-GEE acquisition and model assets | Wider temporal window and service access matter; not required by C2RCC or the selected four. |

These routes are documented in the [Sen2Cor manual](https://step.esa.int/thirdparties/sen2cor/2.13.0/docs/OMPC.TPZ.SUM.004%20-%20i1r0%20-%20Sen2Cor%202.13.02%20Configuration%20and%20User%20Manual.pdf), [ACOLITE](https://github.com/acolite/acolite), [POLYMER ancillary code](https://github.com/hygeos/polymer/blob/master/polymer/ancillary.py), [startmaja](https://www.cesbio.cnrs.fr/maja/running-maja-with-start_maja/), and [SIAC](https://github.com/MarcYin/SIAC). Authentication, service coverage and reachability remain operational checks, not tested processing capabilities. Sen2Cor documents a separate authenticated CDSE Copernicus DEM downloader.

### Resources without invented benchmarks

Sen2Cor’s current manual (§2.5) repeats a **4 GB available-memory** guideline for 10 m, with a historical example peaking around **3.5 GB** on an older 8 GB MacBook. This is neither a current macOS support statement nor a budget for concurrent processors. No comparable contemporary per-tile resource minimum was verified for every other processor.

**Planning estimate, not a minimum:** begin with one tile/job at a time, approximately **16–32 GB RAM**, several cores and substantial local SSD scratch, then measure peak memory/storage before adding concurrency. MAJA’s initialization/series increases total storage and scheduling. POLYMER multiprocessing, SNAP JVM heap/cache, ACOLITE kernels, output resolution and exports affect demand. No runtime or memory benchmark was conducted.

Reserve space for immutable inputs, auxiliaries, working files, repeated outputs and logs rather than compressed imagery alone. Do not transfer a published runtime from another computer/sensor/resolution to the PI’s machine. Later personalized guidance needs OS/version and architecture, RAM/cores, free SSD, supported Linux/container access and required accounts.

### Installation and execution outlines: documented, not executed

These outlines explain operation; they do not authorize installation or system changes. Use pinned releases or a separately approved locked environment. Upstream examples may conflict with repository dependency rules: do not install global Python packages, missing system libraries, or create a second project environment simply to follow an example.

1. **Sen2Cor:** obtain the platform-specific 2.13.02 standalone package, verify checksum and bundled terms, configure GIPP and DEM/CCI paths, and inspect help. The documented family is `L2A_Process <L1C.SAFE> --resolution 20`; select output destination/resolution explicitly. Save effective settings, auxiliary usage, quality metadata and logs before batching. No native macOS package is listed for this release.
2. **ACOLITE:** choose release binary or pinned source/dependencies; cache LUTs; prepare a minimal settings file with input, output, ROI, method and requested products. The launcher supports `python launch_acolite.py --cli --settings=settings.txt`. Save resolved settings; distinguish DSF, glint and TSDSF + RAdCor treatments. Preserve enough surrounding context for adjacency.
3. **POLYMER:** establish use eligibility, follow pinned v4.17 environment/build instructions and retrieve auxiliary files. Configure cache directories in the task environment. Use documented `run_atm_corr(Level1_MSI(...), Level2(...))`, explicitly selecting resolution, metadata context, ancillary route and datasets; `polymer_cli.py <level1> <level2>` is also documented. Record v4/v5, compiled dependencies, optional coastal settings and multiprocessing. Inspect fit/flags.
4. **MAJA:** choose supported binary and matching GIPP/LUT/CAMS collection; prepare `folders.txt`, terrain and useful L1C series. The wrapper supports `startmaja -f folders.txt -t <tile> -s <site> -d <start> -e <end>` and optional `--cams`. Inspect backward/forward workplan and restart state; process tiles independently but preserve within-tile time order. Check that cloud-rejected outputs contain rasters rather than metadata only.
5. **C2RCC:** choose SNAP Optical Toolbox and record module/update/network state. Inspect `gpt c2rcc.msi -h`. Save a graph that reads L1C, resamples necessary bands to declared support, specifies network/auxiliaries/masks, runs `c2rcc.msi` and writes a scientific format. Batch the saved XML with `gpt graph.xml`. The operator name is source-verified; check parameter names in the installed module. No complete untested graph is presented as validated.

Sources for interfaces are the linked official manuals, [ACOLITE launcher documentation](https://github.com/acolite/acolite), [POLYMER README](https://github.com/hygeos/polymer), [startmaja](https://www.cesbio.cnrs.fr/maja/running-maja-with-start_maja/), and [C2RCC operator](https://github.com/senbox-org/optical-toolbox/blob/master/opttbx-c2rcc/src/main/java/eu/esa/opt/c2rcc/msi/C2rccMsiOperator.java). Actual executable/scene compatibility remains a future smoke test.

Keep a scene ledger of successes, failures, auxiliary availability, valid coverage, hashes and restart reasons. Distinguish missing metadata/offsets, LUTs, DEM, credentials, cloud rejection, memory failures and out-of-domain results. Rerun to a new configuration directory; retain unsuccessful coverage rather than silently replacing it with fallback output.

## Comparability and scientific evidence

### Harmonize quantities before algorithms

{{< include tables/output_definitions.md >}}

Above-water remote-sensing reflectance is `Rrs = Lw / Ed` in **sr⁻¹**. Water-leaving reflectance is dimensionless; `ρw = π Rrs` requires matching radiance/irradiance, directional and normalization definitions. Atmospheric correction does not automatically remove interface reflection, whitecaps or bottom contributions. Dividing a land HDRF/BRF by π does not make it an aquatic Rrs measurement.

Keep native and normalized outputs separate and maintain a conversion ledger. Preserve offsets/scales, fill values, masks, geometry, units and spectral responses. Recent L1C offsets must be applied exactly once. A 10 m output using 20/60 m bands is not independent 10 m information. Aggregate to justified common support matching the field footprint; do not sharpen coarse spectra and count interpolated pixels as replicates. C2RCC water outputs cannot supply missing SWIR vegetation bands. Separate resampling artifacts, atmospheric adjacency and genuine mixed pixels.

### Consensus, disagreements and evidence limits

**Consensus:** aquatic performance depends on water type, wavelength, atmosphere/surface assumptions and valid-pixel selection. ACIX-Aqua found differences between freshwater community matchups and mainly coastal AERONET-OC observations. Recommendations depended on optical water type and application, supporting conditional selection and independent field validation. [@Pahlevan2021, §§3–7]

**Apparent disagreement often has methodological causes.** Warren et al. concern older MSI implementations with different coastal/inland matchup windows; their ACOLITE implementation used exponential extrapolation, not the later DSF algorithm. Renosh et al.’s Gironde comparison favored ACOLITE DSF and iCOR for MSI but used ACOLITE-corrected Landsat as an indirect reference because coincident field reflectance was lacking. That demonstrates consistency conditional on the reference correction, not independent radiometric superiority. [@Warren2019; @Renosh2020Estuaries, §5]

**Recent changes alter treatments.** RAdCor’s Belgian small-water evidence does not validate Mauritanian shallow coasts or exposed vegetation. C2RCC’s recent OLCI-focused evaluation cannot be transferred wholesale to MSI. MAJA aerosol/adjacency and Sen2Cor 2026 changes make processor-name-only comparisons inadequate. Pin versions and configurations rather than discarding older evidence or treating it as current validation. [@Castagna2025; @Muller2026; release sources above]

**Land evidence is complementary.** ACIX-II Land and SIAC validate land/atmospheric quantities, not aquatic reflectance under changing tidal exposure. Aquatic validation likewise does not validate exposed vegetation or sediment. No verified Banc d’Arguin/exposed-intertidal validation was established here; this gap is not proof of failure. [@Doxani2023; @Yin2022SIAC]

### Direct exposed-intertidal evidence from the existing project library

The earlier CTR-39 project review contained relevant exposed-surface literature. Its citation keys are preserved here, its local PDFs were reused only after matching their recorded SHA-256 hashes, and relevant passages were re-inspected. Its review acceptance does not approve this new five-processor synthesis.

| Study | Evidence relevant to the present scope | Limit on inference |
|---|---|---|
| Zoffoli et al. [@Zoffoli2020, §§2.3.1,3.3.1 and Fig.5] | Compared Sen2Cor-corrected spectra with field spectra including exposed seagrass, bare sediment and mixed substrates at Bourgneuf Bay. | Limited radiometric-validation scenes; seagrass application, not a common processor ranking. |
| Daggers et al. [@Daggers2020, satellite preprocessing] | Used Sen2Cor followed by empirical relative red/NIR calibration for intertidal microphytobenthos mapping. | Combined calibration prevents attributing temporal consistency to Sen2Cor alone. |
| Jacobs et al. [@Jacobs2021, satellite processing and Discussion] | Used Sen2Cor plus angular correction for mudflat pigment/reflectance analysis; biological migration affected measurement comparability. | Temperate biological endpoint and sampling timing; not an isolated atmospheric-correction validation. |
| Granadeiro et al. [@Granadeiro2021, §§2.2–2.5 and Discussion] | Used ACOLITE DSF surface reflectance with subsequent relative calibration for exposure/topography mapping in Bijagós; investigated spatial tidal lags. | Exposure-map success is not absolute exposed-sediment radiometric accuracy; a useful West African application analogue, not Banc d’Arguin evidence. |
| Thuy et al. [@Thuy2022, §§II–IV] | Used field-based empirical calibration and sediment wetting/drying observations in the Red River Delta to relate spectra to moisture/grain size. | Local calibration and sediment domain; its claim of superior empirical calibration is not demonstrated by a cross-processor experiment in that paper. |
| Colin et al. [@Colin2023, §§2–4] | Assessed MAJA land reflectance and repeated a comparison with adjacency/terrain corrections disabled to match the reference definition. | Developer assessment and land stations; does not validate rapidly changing tidal flats. |

These studies strengthen the rationale for Sen2Cor/MAJA land-reference treatments and the need to retain exposure, moisture, angular effects and biological cover as real surface properties. They do not justify applying C2RCC or POLYMER’s aquatic models directly to exposed vegetation/sediment. They also explain why relative normalization must use justified stable targets rather than forcing changing intertidal pixels to match a previous date. No Banc d’Arguin performance estimate is inferred.

### Future comparison design; not conducted

Use common L1C scenes spanning relevant geometry, atmosphere and tide. Preserve spacecraft, time, baseline, packaging, metadata and hashes, plus executable/settings, LUT/network hashes, auxiliaries and MAJA history. Prespecify primary configurations and sensitivity variants before examining performance. Do not choose a favorable processor/configuration per pixel retrospectively.

| Stratum | Evaluation target | Additional controls |
|---|---|---|
| Water, optically deep where possible | Harmonized water reflectance versus independent radiometry | Optical water type, aerosol, glint/wind, timing, sensor uncertainty |
| Exposed sediment | Surface reflectance versus measured surface spectra | Wetness/exposure duration, geometry, illumination, footprint |
| Exposed vegetation | Surface spectra and relevant indices | Canopy state, inundation, red-edge support, BRDF, footprint |
| Mixed/shallow shoreline | Validity and contamination sensitivity | Subpixel cover, tide, bottom, masks, boundary distance; no pure-endmember assumption |

Use independent, stratum-appropriate references; a processor’s atmospheric prior must not be its sole atmospheric truth. Convolve field spectra with sensor responses, standardize matchup windows/footprints, and report reference uncertainty. Distinguish water-column spectra from bottom-influenced signals. Exposed-surface measurements need matching exposure, wetness and geometry. Timing/tidal mismatch is representativeness error, not automatically correction error.

Report coverage/failure rates over all eligible observations, then accuracy on common-valid matchups and each processor’s available observations as separate populations. Use signed bias, absolute error, RMSE, spectral shape and uncertainty where appropriate; correlation alone is insufficient. Percentage error is unstable near zero reflectance. Account for repeated/spatially dependent observations; resampled pixels are not independent field replicates.

Prespecify shoreline-distance, aerosol and glint strata. Retain flags; compare native and common masks. Strict common masking can hide difficult conditions, making availability an outcome. Preserve scene context for adjacency. Tide/resampling can shift boundaries, and correction cannot reverse physical changes in surface state. Agreement may reflect shared error and disagreement method sensitivity; neither alone identifies accuracy or a calibrated uncertainty distribution.

## Explicit answers

1. **Approaches:** Sen2Cor uses vegetation/ancillary constraints and LUTs; ACOLITE provides dark-spectrum and alternative adjacency configurations; POLYMER jointly fits water/atmospheric spectra; MAJA combines spectral and temporal constraints.
2. **Overlap:** shared physics is not redundancy. Sen2Cor/MAJA overlap most in land targets; ACOLITE/POLYMER overlap in aquatic purpose and some precorrections. Inversion constraints differ, while shared errors remain possible.
3. **Retaining similar processors:** useful for testing temporal information and dark-spectrum versus joint-spectral constraints; the processors are not statistically independent ensemble members.
4. **Alternatives:** C2RCC adds a trained aquatic inverse mapping and public SNAP automation; iCOR adds a cross-domain adjacency route subject to access; SIAC adds Bayesian land priors/uncertainty; OC-SMART current deployability remains unresolved.
5. **Surface domains:** test ACOLITE/POLYMER/C2RCC over water within model limits, and Sen2Cor/MAJA over exposed surfaces. ACOLITE general-surface outputs warrant testing without assuming equivalent land validation. Shallow, mixed and changing-exposure pixels need their own assessment.
6. **Five:** **Sen2Cor + ACOLITE + POLYMER + MAJA + C2RCC**. Costs are heterogeneous outputs and MAJA’s series. **iCOR** is conditional aquatic fallback; **SIAC** is the conditional land-priority alternative with reduced aquatic diversity. No PI-selected processor is replaced.

## Reproducibility and review status

The investigation was copied from `analysis/_template/` in isolated branch `ctr-64-processor-review`, based on `869b759`. The default branch was fetched for handoff. Concurrent work is preserved. No final manuscript, raw dataset, safeguard or lockfile is edited.

Existing CTR-39 project literature and keys were inspected and reused where relevant. The acquisition scripts retrieve metadata/public documents; the table builder produces bibliography/index, matrices and manifests; validation checks citation/DOI uniqueness, PDF identity, file consistency and hashes. Render with the investigation configuration through `scripts/render-analysis.sh`; never regenerate root `index.qmd`. Machine-readable tables/logs accompany the HTML.

The project reference index/synthesis are under `literature/`. Root `library.bib` readiness returned `requires_pre_task_sync`; verified additions are supplied as `library_additions.bib` pending Charles/Ada synchronization. This is **not a completed root bibliography update**. Local PDFs are ignored and excluded from the transfer archive; links/access records permit lawful retrieval.

**Internal scientific review:** pending independent reviewer. Author checks are not independent review. **PI scientific approval:** pending; no authenticated revision-bound approval. **Manuscript integration, merge and publication:** not authorized. The recommendation is ready for critical review, not approved scientific findings. Completion requires independent review and the bibliography synchronization gate.

## Evidence appendices

### Software source snapshots

These inspected source commits are distinct from binary releases. Mutable official links in the narrative are supported by locally hashed snapshots; the actual later installation must record its own module/version.

{{< include tables/software_snapshots.md >}}

### Claim-to-source audit

{{< include tables/claim_evidence.md >}}

### Access and evidence gaps

{{< include tables/access_gaps.md >}}

The accompanying archive contains the CSV method, requirements, candidate, output-definition, reference, claim, source-manifest and search tables, bibliography additions, Quarto sources, and validation scripts. Full texts are excluded; the source manifest supplies their legitimate retrieval links.

## References

::: {#refs}
:::
