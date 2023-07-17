import React, { useEffect, useState } from 'react';
import { authWithPublicData, getConfig } from '../api';

export default function Example() {
    const app = 'example';
 

    function connect() {
        authWithPublicData(app).then(data => {
            window.open(data.redirect, "_self");
        })
    }

    return (<>
        <div className='row mt-3'>
            <div className='col-6'>
                <label>
                Connect with public datasources 
                </label>
            </div>

        </div>
        <br />
        <button type="button" className="btn btn-grey" onClick={() => connect()} >Connect</button>


    </>)
}