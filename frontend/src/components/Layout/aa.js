function Menu({ isOpen, onClose }) {
  const [expandedSections, setExpandedSections] = useState({
    customFeeds: true,
    network: true,
    bookmarks: true,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <div className={`menu-container ${isOpen ? "open" : ""}`}>
      <div className="menu-header">
        <h3>Menu</h3>
        <button
          onClick={onClose}
          className="close-btn"
          aria-label="Close sidebar"
        >
          <FiX />
        </button>
      </div>

      <nav className="menu-nav">
        <ul>
          <li className="active">
            <a href="#" className="menu-item">
              <FiHome className="menu-icon" />
              <span>For You</span>
            </a>
          </li>
          <li>
            <a href="#" className="menu-item">
              <FiUsers className="menu-icon" />
              <span>Following</span>
            </a>
          </li>
          <li>
            <a href="#" className="menu-item">
              <FiCompass className="menu-icon" />
              <span>Explore</span>
            </a>
          </li>
          <li>
            <a href="#" className="menu-item">
              <FiClock className="menu-icon" />
              <span>History</span>
            </a>
          </li>
        </ul>

        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("customFeeds")}
          >
            <span>Custom feeds</span>
            {expandedSections.customFeeds ? (
              <FiChevronDown />
            ) : (
              <FiChevronRight />
            )}
          </div>
          {expandedSections.customFeeds && (
            <ul>
              <li>
                <a href="#" className="menu-item">
                  <FiPlus className="menu-icon" />
                  <span>Custom feed</span>
                </a>
              </li>
            </ul>
          )}
        </div>

        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("network")}
          >
            <span>Network</span>
            {expandedSections.network ? <FiChevronDown /> : <FiChevronRight />}
          </div>
          {expandedSections.network && (
            <ul>
              <li>
                <a href="#" className="menu-item">
                  <FiUsers className="menu-icon" />
                  <span>Find Squads</span>
                </a>
              </li>
              <li>
                <a href="#" className="menu-item">
                  <FiPlus className="menu-icon" />
                  <span>New Squad</span>
                </a>
              </li>
            </ul>
          )}
        </div>

        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("bookmarks")}
          >
            <span>Bookmarks</span>
            {expandedSections.bookmarks ? (
              <FiChevronDown />
            ) : (
              <FiChevronRight />
            )}
          </div>
          {expandedSections.bookmarks && (
            <ul>
              <li>
                <a href="#" className="menu-item">
                  <FiBookmark className="menu-icon" />
                  <span>Presidential briefings</span>
                </a>
              </li>
              <li>
                <a href="#" className="menu-item">
                  <FiStar className="menu-icon" />
                  <span>Quick saves</span>
                </a>
              </li>
              <li>
                <a href="#" className="menu-item">
                  <FiSave className="menu-icon" />
                  <span>Read it later</span>
                </a>
              </li>
            </ul>
          )}
        </div>
      </nav>
    </div>
  );
}

function Nav({ onMenuToggle, isMenuOpen }) {
  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      document.querySelector(".search-input").focus();
    }
  };

  React.useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <nav className="main-nav">
      <div className="nav-container">
        <div className="nav-left">
          <button
            className="menu-toggle"
            onClick={onMenuToggle}
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          >
            ☰
          </button>
          <h1 className="logo">daily.dev</h1>
        </div>

        <div className="search-container">
          <div className="search-bar">
            <FiSearch className="search-icon" />
            <input type="text" className="search-input" placeholder="Search" />
            <span className="search-shortcut">Ctrl + K</span>
          </div>
        </div>
      </div>
    </nav>
  );
}



