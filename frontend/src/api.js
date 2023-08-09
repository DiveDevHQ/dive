import axios from 'axios';

const serviceUrl = process.env.REACT_APP_API_URL? process.env.REACT_APP_API_URL:"http://localhost:8000"

export function getConnectors() {

    return axios
        .get(`${serviceUrl}/integrations/connectors`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getApps(account_id) {
    return axios
        .get(`${serviceUrl}/apps/${account_id}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getConfig(app) {
    return axios
        .get(`${serviceUrl}/integrations/config/${app}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getTemplates(app, module, account_id) {
    return axios
        .get(`${serviceUrl}/templates/${app}/${module}/${account_id}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}

export function getObjTypes(app, account_id) {
    return axios
        .get(`${serviceUrl}/templates/${app}/${account_id}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}


export function getSchemas(app, module) {
    return axios
        .get(`${serviceUrl}/schemas/${app}/${module}`)
        .then(res => res.data)
        .catch(err => console.log(err));

}


export function authWithOAuth2(app, client_id, client_secret, object_scopes, account_id) {
  
    const auth = { 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': window.location.protocol + '//' + window.location.host + '/oauth-callback/' + app, 'object_scopes': object_scopes, 'connector_id': app, 'account_id':account_id };
    return axios.post(`${serviceUrl}/api/authorize/${app}`, auth)
        .then(res => res.data);

}

export function authWithApiKey(app, api_key,account_id) {
    const auth = { 'redirect_uri': window.location.protocol + '//' + window.location.host , 'api_key': api_key, 'connector_id': app, 'account_id':account_id };
    return axios.post(`${serviceUrl}/api/authorize/${app}`, auth)
        .then(res => res.data);

}

export function authWithPublicData(app,account_id) {
   
    const auth = { 'redirect_uri': window.location.protocol + '//' + window.location.host , 'connector_id': app, 'account_id':account_id };
    return axios.post(`${serviceUrl}/api/authorize/${app}`, auth)
        .then(res => res.data);

}

export function callbackWithOAuth2(app, code) {
    const callback = { 'code': code,  'connector_id': app };
    return axios.post(`${serviceUrl}/api/callback`, callback)
        .then(res => res.data);

}

export function addTemplate(app, module, obj_type, schema, account_id,chunking_type) {
    const template = { 'app': app, 'module': module, 'obj_type': obj_type, 'schema': schema,'account_id':account_id,'chunking_type': chunking_type  };
    return axios.post(`${serviceUrl}/template`, template)
        .then(res => res.data);
}


export function deleteTemplate(template_id) {

    return axios.delete(`${serviceUrl}/template/${template_id}`)
        .then(res => res.data);
}


export function updateTemplate(template_id, chunking_type) {
    const template = { 'chunking_type': chunking_type };
    return axios.patch(`${serviceUrl}/template/${template_id}`, template)
        .then(res => res.data);
}


export function syncConnectorData(app, account_id, connector_id) {

    return axios.put(`${serviceUrl}/sync/${app}/${account_id}/${connector_id}`)
        .then(res => res.data);
}

export function syncAccountData(account_id) {

    return axios.put(`${serviceUrl}/sync/${account_id}`)
        .then(res => res.data);
}

export function clearData(app, account_id,connector_id) {

    return axios.put(`${serviceUrl}/clear/${app}/${account_id}/${connector_id}`)
        .then(res => res.data);
}

export function queryData(account_id, connector_id,query_text, top_k,instruction,query_type) {

    return axios.get(`${serviceUrl}/api/v1/documents/search?query_text=${query_text}&account_id=${account_id}&connector_id=${connector_id}&top_k=${top_k}&instruction=${instruction}&query_type=${query_type}`)
        .then(res => res.data);
}

export function setupVector() {

    return axios.get(`${serviceUrl}/setup/vector`)
        .then(res => res.data);
}
