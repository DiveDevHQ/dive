import axios from 'axios';

const serviceUrl = "http://localhost:8000"

export function getConnectors() {
    return axios
        .get(`${serviceUrl}/integrations/connectors`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getApps() {
    return axios
        .get(`${serviceUrl}/apps`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getConfig(app) {
    return axios
        .get(`${serviceUrl}/integrations/config/${app}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function authWithOAuth2(app, client_id, client_secret, object_scopes) {
   
    const auth = { 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': window.location.protocol + '//' + window.location.host + '/oauth-callback/' + app, 'object_scopes': object_scopes, 'instance_id':app };
    return axios.post(`${serviceUrl}/api/authorize/${app}`, auth)
        .then(res => res.data);

}

export function callbackWithOAuth2(app,code) {
    const callback = { 'code': code, 'instance_id':app };
 
    return axios.post(`${serviceUrl}/api/callback`, callback)
        .then(res => res.data);

}
