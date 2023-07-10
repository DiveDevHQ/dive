import React, { useEffect, useState } from 'react';
import { authWithApiKey, getConfig } from '../api';

export default function Example() {
    const app = 'example';
    const [apiKey, setApiKey] = useState('12345');

    function connect() {
        authWithApiKey(app, apiKey).then(data => {
            window.open(data.redirect, "_self");
        })
    }

    return (<>
        <div className='row mt-3'>
            <div className='col-6'>
                <label>
                    <span className='red-text'>*</span>Api Key:  <input className='form-control-long' value={apiKey || ""} onChange={e => setApiKey(e.target.value)}
                        type="text" />
                </label>
            </div>

        </div>
        <br />
        <button type="button" className="btn btn-grey" onClick={() => connect()} >Connect</button>


    </>)
}