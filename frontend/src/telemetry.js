import { ApplicationInsights } from '@microsoft/applicationinsights-web';

const connectionString = import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING;

const appInsights = new ApplicationInsights({
  config: {
    connectionString: connectionString,
    enableAutoRouteTracking: true,
    enableCorsCorrelation: true,
    enableRequestHeaderTracking: true,
    enableResponseHeaderTracking: true,
  }
});

if (connectionString) {
  appInsights.loadAppInsights();
  console.log("Application Insights initialized");
} else {
  console.warn("Application Insights Connection String not found. Telemetry disabled.");
}

export { appInsights };
