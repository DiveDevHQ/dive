
import React, { useEffect, useState } from 'react';
import { authWithOAuth2, getConfig } from '../api';

export default function Hubspot({account_id}) {

  const app='hubspot';
  const [instanceType, setInstanceType] = useState(0);
  const [clientId, setClientId] = useState();
  const [config, setConfig] = useState();
  const [clientSecret, setClientSecret] = useState();
  const [selectScopes, setSelectScopes] = useState([]);
  const [scopeString, setScopeString] = useState();


  const permissionTypes = Object.freeze([
    { name: 'Contacts', value: 1, scope: 'crm.schemas.contacts.read crm.objects.contacts.read crm.objects.contacts.write', selected: true },
    { name: 'Companies', value: 2, scope: 'crm.schemas.companies.read crm.objects.companies.read crm.objects.companies.write', selected: true },
    { name: 'Deals', value: 3, scope: 'crm.schemas.deals.read crm.objects.deals.read crm.objects.deals.write', selected: true },
    { name: 'Engagements', value: 4, scope: 'sales-email-read files', selected: true }
  ]);


  useEffect(() => {

    if (permissionTypes) {
      var _selectScopes = [];
      for (var i = 0; i < permissionTypes.length; i++) {
        if (_selectScopes.indexOf(permissionTypes[i].value) === -1 && permissionTypes[i].selected) {
          var scope = permissionTypes[i].value;
          _selectScopes.push(scope);
        }
      }
      setSelectScopes(_selectScopes);
    }

    getConfig(app).then(data => {
      setConfig(data);
  
    });
  }, []);

  function handleScopeSelect(scopeValue) {

    if (selectScopes.indexOf(scopeValue) === -1) {

      setSelectScopes(current => [scopeValue, ...current]);
    }
    else {
      const optionIndex = selectScopes.findIndex(
        item => item === scopeValue
      );
      var _selectScopes = selectScopes;
      _selectScopes.splice(optionIndex, 1);
      setSelectScopes([..._selectScopes])
    }
  }

  function getScopeChecked(scopeValue) {
    if (selectScopes.indexOf(scopeValue) > -1) {
      return true;
    }
    return false;
  }

  function generateScopeString(){
    var scope=getScopeString();
    setScopeString(scope);
  }

  function getScopeString(){
    var separator=config['scope_params']['scope_separator'];
    var scopes=config['scope_params']['default_scopes'].split(separator);
    for (var i = 0; i < permissionTypes.length; i++) {
      if (selectScopes.indexOf(permissionTypes[i].value) >-1) {
        var _scopes= permissionTypes[i].scope.split(separator);
        for (var j=0;j<_scopes.length;j++){
          scopes.push(_scopes[j]);
         }
      }
    }
    return scopes.join(separator);
  }

  function openAuthApiDoc(){
    window.open('https://docs.diveapi.co/#connect-multiple-instances', "_blank");
  }

  function connect(){
    authWithOAuth2(app,clientId,clientSecret,getScopeString(),account_id).then(data=>{
      window.open(data.redirect, "_self");
    })
  }

  return (<>

    <h4>Prerequisite</h4>
    <div>
      You need to have the following data ready:
    </div>
    <ul>
      <li>Client Id</li>
      <li>Client Secret</li>
    </ul>

    To get "client id" and "client secret", please create a HubSpot developer account: <a
      href="https://developers.hubspot.com/docs/api/overview" target="_blank">here</a>. <br /><br />

    <h4>Connect</h4>
    {(instanceType===0 || instanceType===1) &&( <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(1)} >Connect my instance</button>
   )}
   {(instanceType===0 || instanceType===2) && ( <button type="button" className="btn btn-grey" onClick={() => setInstanceType(2)}  >Connect my customers' instances</button>
   )}
    <br /> <br />
    {instanceType === 1 && (
      <div>
       
        <span className='red-text'>Add</span>  "http://localhost:3000/oauth-callback/hubspot" to redirect_uri field in your developer account.
 
        <div className='row mt-3'>
          <div className='col-6'>
            <label>
              <span className='red-text'>*</span>Client Id:  <input className='form-control-long' value={clientId || ""} onChange={e => setClientId(e.target.value)}
                type="text" />
            </label>
          </div>
          <div className='col-6'>
            <label>
              <span className='red-text'>*</span>Client Secret:  <input className='form-control-long' value={clientSecret || ""} onChange={e => setClientSecret(e.target.value)}
                type="text" />
            </label>
          </div>
        </div>
        <br />
        <h4>Object permissions</h4>
        <div>
          {permissionTypes.map(type => (
            
              <div key={type.name}>
                <input type="checkbox" onClick={() => handleScopeSelect(type.value)} onChange={e => { }} checked={getScopeChecked(type.value)} className='cursor-pointer check-bar' value={type.scope} />
                &nbsp;
                {type.name}</div>
           

          ))}
        </div>
        <br />

        <button type="button" className="btn btn-grey mr-3" onClick={() => connect()} >Connect</button>
        <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(0)} >Cancel</button>
      </div>
    )}
    {instanceType === 2 && (
      <div>
        <span className='red-text'>Add</span>  your custom app callback url (i.e. https://example.com/callback) to redirect_uri field in your developer account.
        <br /> <br />
        <h4>Object permissions</h4>
        <div>
          {permissionTypes.map(type => (
            
              <div key={type.name}>
                <input type="checkbox" onClick={() => handleScopeSelect(type.value)} onChange={e => { }} checked={getScopeChecked(type.value)} value={type.scope} className='cursor-pointer check-bar' />
                &nbsp;
                {type.name}</div>
           

          ))}
        </div><br />
        <button type="button" className="btn btn-grey mr-3" onClick={() => generateScopeString()} >Generate scopes string</button>
        <button type="button" className="btn btn-grey mr-3" onClick={() => openAuthApiDoc()} >Connect API</button>
        <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(0)} >Cancel</button>

            {scopeString && (
              <div className='text-copy mt-2'>{scopeString}</div>
            )}
      </div>

    )}
  </>

  );

}
