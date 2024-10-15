import React from "react";
import Helmet from "react-helmet";
import { Link } from 'react-router-dom';
import { Header, NavBar, Footer } from "@civicactions/data-catalog-components";
import config from "../../assets/config.json";
import links from "../../assets/menu.json";
import sealLogo from "../../seal.png";

const Layout = ({
  children,
  title,
  description
}) => {
  return (
    <div className="App">
      <Helmet
        // title={`${title} - DKAN Demo`}
        title={`City of Portland`}
        description={description}
        generator="DKAN 2 (https://github.com/GetDKAN/dkan)"
        defer={false}
        htmlAttributes={{
          "lang": "en"
        }}
      />
      <Header logo={sealLogo} site={config.site} slogan={config.slogan} customClasses={config.container} />
      <NavBar
        navItems={[links.main.map(item => (
          <Link to={item.url}>
            {item.label}
          </Link>
        )),
          <a href="/user/login">Login</a>
        ]}
        customClasses={config.container}
      />
      <main>
        {children}
      </main>
      <Footer links={links} customClasses={config.container} />
    </div>
  );
};

export default Layout;
