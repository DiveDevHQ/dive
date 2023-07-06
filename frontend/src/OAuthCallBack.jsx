import React, { useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { callbackWithOAuth2 } from './api';


export default function OAuthCallBack() {
    const navigate = useNavigate();
    let { app } = useParams();
    const [searchParams, setSearchParams] = useSearchParams();
    var code = searchParams.get("code");
    useEffect(() => {
        callbackWithOAuth2(app, code).then(d => {

            navigate(
             {
                 pathname: `/`,
             }
         ); 
       });
    }, []);
    return (<>

    </>);
}