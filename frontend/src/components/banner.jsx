import './styles/components.css'

const Banner = () => {
    return (
        <div className="banner">
            <div className="banner-title" onClick={() => window.location.reload()}>
            <h3>Sandoz Tender Summarizer</h3>
            </div>
            <a href="https://www.sandozfarma.es/" target="_blank">
            <img src={`./sandoz-logo.png`} className="logo" alt="Sandoz Logo" />
            </a>
        </div>
    );
  };

  export default Banner;