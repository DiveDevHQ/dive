import axios from 'axios';

const serviceUrl = process.env.REACT_APP_API_URL? process.env.REACT_APP_API_URL:"http://localhost:8000"

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

export function getTemplates(app, module) {
    return axios
        .get(`${serviceUrl}/templates/${app}/${module}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getSchemas(app, module) {
    return axios
        .get(`${serviceUrl}/schemas/${app}/${module}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}


export function authWithOAuth2(app, client_id, client_secret, object_scopes) {
    const auth = { 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': window.location.protocol + '//' + window.location.host + '/oauth-callback/' + app, 'object_scopes': object_scopes, 'connector_id': app };
    return axios.post(`${serviceUrl}/api/authorize/${app}`, auth)
        .then(res => res.data);

}

export function callbackWithOAuth2(app, code) {
    const callback = { 'code': code, 'connector_id': app };
    return axios.post(`${serviceUrl}/api/callback`, callback)
        .then(res => res.data);

}

export function addTemplate(app, module, obj_type, schema) {
    const template = { 'app': app, 'module': module, 'obj_type': obj_type, 'schema': schema };
    return axios.post(`${serviceUrl}/template`, template)
        .then(res => res.data);
}


export function deleteTemplate(template_id) {

    return axios.delete(`${serviceUrl}/template/${template_id}`)
        .then(res => res.data);
}



export function syncData(app, connector_id) {

    return axios.put(`${serviceUrl}/sync/${app}/${connector_id}`)
        .then(res => res.data);
}


export function clearData(app, connector_id) {

    return axios.put(`${serviceUrl}/clear/${app}/${connector_id}`)
        .then(res => res.data);
}
