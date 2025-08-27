Kravspesifikasjon: Internt Lenkekart-verktøy
Dokumentversjon:	1.0
Dato:	27. august 2024
Status:	Publisert
Forfatter:	Marcus Jenshaug (Lead-utvikler)
Dokumentoversikt
Innledning og Formål
Omfang og Målgruppe
Konfigurasjon og Kjøring
Funksjonelle Krav
Crawl og Datainnsamling
Link-graf og Analyse
Interaktiv Rapport
Sitemap-generering
Ikke-funksjonelle Krav
Datamodeller
Teknisk Arkitektur og Rammeverk
Leveranser
Akseptansekriterier
1. Innledning og Formål
Dette dokumentet beskriver kravene for et verktøy som automatisk kartlegger og analyserer interne lenker på et nettsted. Målet er å produsere en interaktiv, profesjonell og delbar HTML-rapport som gir innsikt i nettstedets lenkestruktur. Rapporten skal være et verdifullt verktøy for interessenter innen SEO, produktutvikling og UX.

2. Omfang og Målgruppe
Hovedmålgruppe: SEO-spesialister, produktledere, UX-designere, innholdsstrateger og utviklere.
I Omfang (In-Scope):
Crawling av ett enkelt domene (med valgfri inkludering av subdomener).
Analyse av intern lenkestruktur.
Generering av en selvstendig, lokal HTML-rapport.
Generering av sitemap.xml og sitemap.html.
Utenfor Omfang (Out-of-Scope):
Crawling av eksterne lenker utover å telle dem.
Analyse av innholdskvalitet (utover metadata).
Kontinuerlig overvåkning (verktøyet kjøres on-demand).
3. Konfigurasjon og Kjøring
Verktøyet skal kunne konfigureres via en config.yml-fil og kjøres fra kommandolinjen (CLI).

3.1. Kjøringseksempler (CLI)
# 1. Crawl et domene basert på konfigurasjon
linkmap crawl --config config.yml

# 2. Generer rapport fra en fullført crawl
linkmap report --input crawl.db --out ./report --compute-reciprocity true

# 3. Generer sitemaps (XML og HTML)
linkmap sitemap --input crawl.db --out ./report --xml --html --segment-size 45000
3.2. Konfigurasjonsparametre
Verktøyet skal støtte følgende parametre i config.yml:

Parameter	Type	Default	Beskrivelse
start_url	string	(Påkrevd)	Rot-URL for crawling.
include_subdomains	bool	false	Hvorvidt subdomener skal inkluderes i crawlen.
max_pages	int	20000	Maksimalt antall sider som skal crawles.
max_depth	int	12	Maksimal klikkdybde fra start_url.
concurrency	int	8	Antall parallelle forespørsler.
render_js	bool	true	Om en headless-browser skal brukes for å rendere JavaScript.
respect_robots	bool	true	Om robots.txt-regler skal respekteres.
crawl_delay_ms	int	300	Forsinkelse mellom forespørsler for å redusere serverbelastning.
allowed_paths	list	["/"]	Liste av URL-prefikser (regex) som skal inkluderes.
blocked_paths	list	[]	Liste av URL-prefikser (regex) som skal ekskluderes.
auth	object	null	Valgfrie HTTP-headere/cookies for autentisering.
language	string	nb-NO	Språk for UI-tekster i rapporten. Støtter en-US.
mask_query_params	list	[]	Query-parametre som skal maskeres i rapporten (f.eks. "token").
4. Funksjonelle Krav
4.1. Crawl og Datainnsamling
URL-håndtering: Normaliser URLer (skjema, trailing slash, sortering av query-parametre, fjerning av fragment).
Lenkefølging: Følg <a>-lenker som peker til samme eTLD+1 (eller subdomener hvis include_subdomains=true).
Sitemap.xml: Hent og flett URLer fra sitemap.xml (hvis tilgjengelig) med organisk oppdagede URLer.
Respekt for direktiver: Håndter robots.txt, rel="nofollow", og meta name="robots" (noindex, nofollow) når aktivert.
JavaScript-rendering: Bruk en headless-browser (f.eks. Playwright) for å oppdage klient-genererte lenker når render_js=true.
Datainnsamling per side: For hver unike kanoniske URL skal følgende data lagres:
Statuskode (200, 301, 404, etc.).
Content-Type.
Canonical URL (<link rel="canonical">).
Meta robots-direktiver.
Tittel (<title>).
H1 (<h1>).
Språk (lang-attributt).
Lastetid (TTFB og total).
Sidestørrelse (bytes).
Persistens: Data skal lagres strømmende til en lokal database (f.eks. SQLite) eller filbasert format (Parquet/NDJSON) for å håndtere store nettsteder og muliggjøre gjenopptakelse av avbrutte crawls.
4.2. Link-graf og Analyse
Graf-konstruksjon: Bygg en rettet graf der noder er sider og kanter er interne lenker.
Node-metrikker: For hver node (side) skal følgende beregnes:
in_degree (antall innkommende lenker).
out_degree (antall utgående lenker).
PageRank eller lignende autoritetsscore.
klikkdybde fra start_url.
orphan_status (en side er orphan hvis den har 0 innkommende lenker, men finnes i sitemap/er oppdaget).
reciprocity_ratio (% av naboer som lenker tilbake).
Kant-attributter: Hver kant (lenke) skal ha attributter som source_url, target_url, anchor_text, rel, is_bidirectional.
Gjensidighet (Reciprocity): En kant A→B skal markeres som gjensidig (is_bidirectional=true) hvis kanten B→A også eksisterer.
Identifisering av nøkkelsegmenter: Systemet skal automatisk identifisere og flagge:
Orphan pages: Sider i sitemap uten innlenker, og sider med innlenker som ikke er i sitemap.
Deep pages: Sider med klikkdybde > 3 (konfigurerbart).
Redirect chains/loops: Omdirigeringskjeder og -løkker.
Broken links: Lenker som peker til sider med 4xx/5xx-status eller timeout.
Canonical-konflikter: Flere sider som peker til samme kanoniske URL.
One-way funnels: Sider med høy out_degree og lav in_degree.
Critical connectors: Sider med høy "betweenness centrality".
Klustering:
Automatisk gruppering av sider basert på URL-mønstre (f.eks. /blog/, /produkter/).
Valgfri community detection (f.eks. Louvain) for å avdekke tematiske klynger.
4.3. Interaktiv Rapport
Rapporten skal være en selvstendig, statisk HTML-applikasjon (/report-mappe) som kan åpnes lokalt.

Fanestruktur: Rapporten skal ha minst to hovedfaner: "Sitemap (tre)" og "Lenkekart (rettet)". Klikk på en node i den ene visningen skal fremheve den i den andre.
Oversiktsside (Dashboard):
KPI-kort: Totalt antall sider, gj.sn. klikkdybde, % dype sider, antall brutte lenker, antall orphans, andel gjensidige lenker.
Topplister: Topp 10 hub-sider (flest utlenker) og autoritetssider (høyest PageRank).
Nettverksgraf-visualisering (fane: Lenkekart):
Teknologi: Cytoscape.js eller Sigma.js.
Interaktivitet: Zoom, pan, dra noder, fremhev noder/kanter ved hover.
Visualisering av retning og gjensidighet:
Alle kanter har pilspiss mot målet.
Enveislenker: Tynnere, stiplet linje.
Gjensidige lenker: Tykkere, heltrukket linje.
Node-styling: Størrelse basert på in_degree/PageRank, farge basert på klynge/URL-seksjon.
Detaljpanel: Klikk på en node åpner et panel med all metadata (URL, tittel, status, dybde, lenker inn/ut, reciprocity_ratio etc.).
Filtre: Søkefelt, filtre for dybde, statuskode, klynge, content-type, og avkrysningsboks for "Vis kun gjensidige lenker".
Hierarkisk trevisning (fane: Sitemap):
Viser nettstedets struktur basert på URL-stier.
Skal være søkbar og kunne ekspanderes/kollapses.
Tabellvisninger:
Dedikerte tabeller for "Brutte lenker", "Orphan pages", "Dype sider", "Omdirigeringer".
Alle tabeller skal være sorterbare, filtrerbare og kunne eksporteres til CSV/Excel.
Eksport:
Hele grafen som graph.json (noder/kanter).
Grafen i GEXF/GraphML-format for import i Gephi.
Utsnitt av graf-visualiseringen som PNG/SVG.
Rapporter for spesifikke funn som CSV.
4.4. Sitemap-generering
XML Sitemap:
Generer sitemap.xml som følger standard spesifikasjon.
Skal automatisk lage en sitemap_index.xml og segmenterte filer (sitemap-1.xml, etc.) hvis antall URLer overstiger 50 000 eller filstørrelsen overstiger 50MB.
Ekskluder sider med noindex, status ulik 200, eller sider blokkert av robots.txt.
HTML Sitemap:
Generer en menneskelesbar sitemap.html som en hierarkisk trestruktur.
Inkluder søk og filtrering.
5. Ikke-funksjonelle Krav
Ytelse og Skalerbarhet:
Rapportens nettverksgraf skal laste på < 3 sekunder for grafer med opptil 3 000 noder.
For større grafer (> 3 000 noder) skal en "Level-of-Detail" (LOD) mekanisme brukes, der noder aggregeres og kan "drilles ned" i.
Crawling og analyse skal være minneeffektivt ved å bruke strømmende skriving/lesing.
Sikkerhet og Etisk Crawling:
Respekter robots.txt og crawl-delay som standard.
Masker sensitive query-parametre (f.eks. token, auth) i rapporten.
Ingen data skal lastes opp til tredjeparter.
Tilgjengelighet (a11y): Rapporten skal støtte tastaturnavigasjon og bruke ARIA-etiketter for å være tilgjengelig for skjermlesere.
Dokumentasjon: Prosjektet skal ha en README.md med hurtigstart-guide, konfigurasjonseksempler og en seksjon for kjente begrensninger/feilsøking.
Testbarhet:
Enhetstester for kritiske moduler (URL-normalisering, parsing).
Integrasjonstester mot et lokalt test-nettsted som inkluderer statiske sider, JS-genererte lenker, redirects og robots.txt.
6. Datamodeller
6.1. Nodes (Sider)
{
  "url": "https://example.com/side-a",
  "canonical": "https://example.com/side-a",
  "status": 200,
  "content_type": "text/html",
  "title": "Side A",
  "h1": "Velkommen til Side A",
  "language": "nb-NO",
  "depth": 1,
  "in_degree": 10,
  "out_degree": 5,
  "pagerank": 0.0015,
  "load_ms": 250,
  "size_bytes": 15000,
  "cluster": "Produkter",
  "reciprocity_ratio": 0.4
}
6.2. Edges (Lenker)
{
  "source_url": "https://example.com/side-b",
  "target_url": "https://example.com/side-a",
  "anchor_text": "Gå til side A",
  "rel": "dofollow",
  "is_bidirectional": true,
  "edge_weight": 2,
  "discovered_via": "html"
}
7. Teknisk Arkitektur og Rammeverk
Crawler: Node.js (med Playwright) eller Python (med Playwright/Requests-HTML).
Datapersistens: SQLite for strukturert data, NDJSON for kanter.
Analyse: Python (med Pandas + NetworkX) eller Node.js (med Graphology).
Rapportgenerator: Statisk HTML-mal (f.eks. EJS/Handlebars) som fylles med data.
Frontend-visualisering: Cytoscape.js eller Sigma.js. Tabeller og UI med lettvekts-rammeverk (f.eks. Lit, Svelte) eller Vanilla JS.
Containerisering: En Dockerfile skal inkluderes for reproduiserbar kjøring.
8. Leveranser
Kjørbar CLI-applikasjon (linkmap).
Et Docker-image for enkel distribusjon.
En statisk rapportmappe (/report) som inneholder index.html, graph.json, CSS/JS-ressurser, og eksporterte CSV-filer.
Eksempelfil for konfigurasjon (config.example.yml).
Kildekode med MIT-lisens.
Test-suite og et lokalt test-nettsted.
9. Akseptansekriterier
linkmap crawl fullfører uten feil mot et testdomene og produserer en databasefil.
linkmap report genererer en interaktiv rapport der alle moduler (graf, tabeller, KPIer) laster og viser relevant data.
linkmap sitemap produserer sitemap.xml som validerer mot standarden, og segmenterer korrekt ved >50k URLer.
I nettverksgrafen er gjensidige og ensidige lenker visuelt distinkte (f.eks. heltrukket vs. stiplet).
Filtre i rapporten (spesielt "Vis kun gjensidige lenker") fungerer som forventet.
Eksport til CSV, PNG, SVG, og GEXF produserer gyldige og lesbare filer.
Regler i robots.txt respekteres når respect_robots=true.
Dokumentasjonen er tilstrekkelig for at en ny bruker kan installere, konfigurere og kjøre en analyse.
Rapporten laster raskt (< 3s) og er responsiv selv med tusenvis av noder, takket være LOD-implementering.
