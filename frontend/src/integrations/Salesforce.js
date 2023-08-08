
import React, { useEffect, useState } from 'react';
import { authWithOAuth2, getConfig } from '../api';

export default function Salesforce({account_id}) {

  const app='salesforce';
  const [instanceType, setInstanceType] = useState(0);
  const [clientId, setClientId] = useState();
  const [config, setConfig] = useState();
  const [clientSecret, setClientSecret] = useState();
 
  useEffect(() => {
 
    getConfig(app).then(data => {
      setConfig(data);
  
    });
  }, []);

  
  function openAuthApiDoc(){
    window.open('https://docs.diveapi.co/#connect-multiple-instances', "_blank");
  }

  function connect(){
    authWithOAuth2(app,clientId,clientSecret,'',account_id).then(data=>{
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
<p>
To get "client id" and "client secret", please create a Salesforce developer account <a
            href="https://developer.salesforce.com/signup" target="_blank">here</a>, and create a "connected app" under "App Manager". Enable OAuth settings. For OAUTH scopes, select "Manage user data via APIs (api)" or whatever meets your needs, make sure to also select "Perform requests at any time (refresh_token, offline_access)".
</p>
<p>If you can not find "App Manager", check your permissions <a
            href="https://help.salesforce.com/s/articleView?id=000384657&type=1" target="_blank">here</a>. 
</p>

   
 <br/>
    <h4>Connect</h4>
    {(instanceType===0 || instanceType===1) &&( <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(1)} >Connect my instance</button>
   )}
   {(instanceType===0 || instanceType===2) && ( <button type="button" className="btn btn-grey" onClick={() => setInstanceType(2)}  >Connect my customers' instances</button>
   )}
    <br /> <br />
    {instanceType === 1 && (
      <div>
      
        <span className='red-text'>Add</span>  "http://localhost:3000/oauth-callback/salesforce" to redirect_uri field in your developer account.
    
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

        <button type="button" className="btn btn-grey mr-3" onClick={() => connect()} >Connect</button>
        <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(0)} >Cancel</button>
      </div>
    )}
    {instanceType === 2 && (
      <div>
        <span className='red-text'>Add</span>  your custom app callback url (i.e. https://example.com/callback) to redirect_uri field in your developer account.
        <br /> <br />
      
        <button type="button" className="btn btn-grey mr-3" onClick={() => openAuthApiDoc()} >Connect API</button>
        <button type="button" className="btn btn-grey mr-3" onClick={() => setInstanceType(0)} >Cancel</button>

         
      </div>

    )}
  </>

  );

}
