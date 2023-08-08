import React, { useEffect } from 'react';

import Hubspot from '../integrations/Hubspot';
import Salesforce from '../integrations/Salesforce';
import Example from '../integrations/Example';
 
export default function Integration({ name, account_id}) {
  

    return (
        <div>
            {name && name === 'hubspot' && (
                <div><Hubspot account_id={account_id}/> </div>
                
 
            )}
            {name && name === 'salesforce' && (
                 <div><Salesforce account_id={account_id}/> </div>
                
            )}
            {name && name === 'example' && (
                 <div><Example account_id={account_id}/> </div>
                
            )}
        </div>
    );
}
