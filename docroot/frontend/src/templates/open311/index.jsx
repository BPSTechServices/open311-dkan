import React from "react";
import { Announcement } from "@civicactions/data-catalog-components";
import Layout from '../../components/Layout';
import config from "../../assets/config";
import { version, dependencies } from '../../../package.json';
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

const Open311 = () => (
    <Layout title="Open311">
      <div className={`dc-page ${config.container}`}>
        {/*<h1>Open311</h1>*/}
        <div className="dc-page-content row">
          {/*<div className="col-md-9 col-sm-12">*/}
          {/*  <p>Portland 311 supports the Open311 API standard.</p>*/}
          {/*</div>*/}
          {/*<div className="col-md-3 col-sm-12">*/}
          {/*  <Announcement variation="info" heading="Note">*/}
          {/*    <p>Update this about page before publishing.</p>*/}
          {/*  </Announcement>*/}
          {/*</div>*/}
          <div className="col-md-9 col-sm-12">
            <SwaggerUI url="https://127.0.0.1:5000/swagger.json"/>
          </div>
        </div>
        <h2>App version:</h2>
        <div className="dc-page-content row">
          <div className="col-12">
            <p>data-catalog-app: {version}</p>
            <p>data-catalog-components: {dependencies["@civicactions/data-catalog-components"]}</p>
          </div>
        </div>
      </div>
    </Layout>
);

export default Open311;
