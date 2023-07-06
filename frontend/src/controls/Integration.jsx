import React, { useEffect } from 'react';

import Hubspot from '../integrations/Hubspot';
import Salesforce from '../integrations/Salesforce';
 
export default function Integration({ name }) {
  

    return (
        <div>
            {name && name === 'hubspot' && (
                <div><Hubspot /> </div>
                
 
            )}
            {name && name === 'salesforce' && (
                 <div><Salesforce /> </div>
                
 
            )}

        </div>
    );
}
