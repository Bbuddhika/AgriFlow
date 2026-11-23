import { loadCatalog, type ProduceType } from "@/features/produce/catalog";

export const dynamic = "force-dynamic";

export default async function Home() {
  let catalog: ProduceType[] = [];
  let unavailable = false;
  try { catalog = await loadCatalog(); } catch { unavailable = true; }

  return <>
    <a className="skip" href="#main">Skip to content</a>
    <header className="header">
      <a className="brand" href="/" aria-label="Dambulla AgriFlow home"><span className="brand-mark">a<span>↗</span></span><span>agriflow<small>DAMBULLA</small></span></a>
      <nav aria-label="Main navigation"><a href="#produce">Produce catalog</a><a href="#journey">How it works</a></nav>
      <span className="phase">Foundation preview</span>
    </header>
    <main id="main">
      <section className="hero">
        <div className="hero-copy"><p className="eyebrow">ROOTED IN DAMBULLA. BUILT FOR MARKET DAY.</p><h1>Good produce.<br/>Better connections.</h1><p className="intro">One place to bring farmers, buyers and market operations together. From the first harvest to the final receipt.</p><a className="button" href="#produce">Explore the catalog <span aria-hidden="true">↗</span></a><div className="hero-foot"><span className="dot"/> Designed for Sri Lanka’s wholesale market</div></div>
        <div className="harvest-art" role="img" aria-label="Abstract illustration of produce crates in forest green, tomato red and warm yellow"><div className="art-label">THE NEXT MARKET DAY<br/><strong>starts with a connection.</strong></div><div className="crate crate-one"><i/><i/><i/></div><div className="crate crate-two"><b/><b/><b/></div><div className="leaf leaf-one"/><div className="leaf leaf-two"/><div className="art-bottom">GROWN WITH CARE <span>06° → 08° N</span></div></div>
      </section>
      <section id="produce" className="catalog-section"><div className="section-heading"><div><p className="eyebrow">KNOW WHAT’S GROWING</p><h2>The produce catalog</h2></div><span className={unavailable ? "status offline" : "status"}>{unavailable ? "Connection unavailable" : "Connected to catalog"}</span></div><p className="muted">Browse supported produce types. Live listings, available quantities and prices will appear as market workflows are implemented.</p>
        {unavailable ? <div className="notice" role="status"><h3>The catalog is taking a moment.</h3><p>We couldn’t reach the market service. Please refresh to try again.</p><a href="/">Try again →</a></div> : catalog.length === 0 ? <div className="notice">No produce types are available yet.</div> : <div className="produce-grid">{catalog.map((item, index) => <article className="produce-card" key={item.id}><div className={`produce-symbol tone-${index % 3}`} aria-hidden="true">{item.name.slice(0, 1)}<span>✳</span></div><div><small>{item.code}</small><h3>{item.name}</h3><p>Measured in {item.unit}</p></div></article>)}</div>}
      </section>
      <section id="journey" className="journey"><div><p className="eyebrow">ONE CONNECTED JOURNEY</p><h2>From field<br/>to a fairer market day.</h2><p className="muted">Workflows planned for farmers, buyers and administrators.</p></div><ol><li><span>01</span><div><h3>Register the harvest</h3><p>Farmers publish lots with asking prices and arrange a market visit.</p></div></li><li><span>02</span><div><h3>Make a connection</h3><p>Buyers offer a price. Farmer acceptance creates a timed reservation.</p></div></li><li><span>03</span><div><h3>Inspect, confirm, settle</h3><p>Administrators coordinate inspection and payment records, with participant approvals.</p></div></li></ol></section>
    </main><footer><span className="footer-brand">agriflow / Dambulla</span><p>Application foundation · Trading, accounts and payments are not yet enabled.</p><a href="#main">Back to top ↑</a></footer>
  </>;
}
