import React, { useEffect, useRef, useState } from 'react';
import axios from "axios";
import * as pbi from 'powerbi-client';
import './visuals.css';

interface VisualsProps {}

const Visuals: React.FC<VisualsProps> = () => {
  const powerBiRef = useRef<HTMLDivElement>(null);
  const [embedConfig, setEmbedConfig] = useState<{
    embedUrl: string,
    embedReportId: string,
    embedToken: string,
  } | null>(null);
  const [filterPaneEnabled, setFilterPaneEnabled] = useState(true);
  const [navContentPaneEnabled, setNavContentPaneEnabled] = useState(true);

  useEffect(() => {
    // Fetch embed config on component mount
    const fetchEmbedConfig = async () => {
      try {
        const response = await axios.get('getembedinfo');
        console.log(response)
        const data = await response.data;
        if (data.tokenExpiry && data.reportConfig && data.accessToken) {
          let embedConfig = {
            embedUrl: data.reportConfig[0].embedUrl,
            embedReportId: data.reportConfig[0].reportId,
            embedToken: data.accessToken,
          }
          setEmbedConfig(embedConfig);
        } else {
          console.error('Failed to fetch embed config:', data.error);
        }
      } catch (error) {
        console.error('Network error:', error);
      }
    };
    
    fetchEmbedConfig();
  }, []);

  useEffect(() => {
    if (!embedConfig) {
      return;
    }

    const config: pbi.IEmbedConfiguration = {
      type: 'report',
      tokenType: pbi.models.TokenType.Embed,
      accessToken: embedConfig.embedToken,
      permissions: pbi.models.Permissions.All,
      embedUrl: embedConfig.embedUrl,
      id: embedConfig.embedReportId,
      settings: {
        filterPaneEnabled: filterPaneEnabled,
        navContentPaneEnabled: navContentPaneEnabled,
      },
    };

    const powerbi = new pbi.service.Service(
      pbi.factories.hpmFactory,
      pbi.factories.wpmpFactory,
      pbi.factories.routerFactory
    );

    if (powerBiRef && powerBiRef.current) {
      const powerBiContainer = powerbi.embed(powerBiRef.current, config);

      // Clean up on unmount
      return () => {
        if (powerBiRef.current) {
          powerbi.reset(powerBiRef.current);
        }
      };
    }
  }, [embedConfig, filterPaneEnabled, navContentPaneEnabled]);

  return (
    <div className='Visuals'>
      <div ref={powerBiRef} style={{ height: '100%', width: '100%' }} />
      <div style={{ marginTop: '20px' }}>
        <label>
          Filter Pane:
          <input
            type="checkbox"
            checked={filterPaneEnabled}
            onChange={() => setFilterPaneEnabled(prev => !prev)}
          />
        </label>
        <label style={{ marginLeft: '20px' }}>
          Navigation Pane:
          <input
            type="checkbox"
            checked={navContentPaneEnabled}
            onChange={() => setNavContentPaneEnabled(prev => !prev)}
          />
        </label>
      </div>
    </div>
  );
};

export default Visuals;
