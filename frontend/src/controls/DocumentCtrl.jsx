
import React, { useEffect, useState } from 'react';

import { getObjTypes, clearData, syncConnectorData } from '../api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ChunkingTypes } from '../references';
import InfoIcon from '../icons/InfoIcon';
import { PulseLoader } from 'react-spinners';

export default function DocumentCtrl({ app, account_id, connector_id, onSchemaEdit }) {
    const [objTypes, setObjTypes] = useState();
    const [error, setError] = useState();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        getObjTypes(app, account_id).then(data => {
            var _objTypes = [];
            for (var i = 0; i < data.length; i++) {
                _objTypes.push(data[i]['obj_type']);
            }
            setObjTypes([..._objTypes]);
        })
    }, []);

    function handleNotification(actionType) {
        toast.info(CustomToastWithLink(actionType),
            { position: toast.POSITION.TOP_CENTER, autoClose: false, type: "success" });

    }

    const CustomToastWithLink = (text) => (
        <div>
            {text}
        </div>
    );

    function handleReloadData() {
        if (error){
            getObjTypes(app, account_id).then(data => {
                var _objTypes = [];
                for (var i = 0; i < data.length; i++) {
                    _objTypes.push(data[i]['obj_type']);
                }
                setObjTypes([..._objTypes]);
                if (_objTypes.length===0){
                    setError('Please add data source.');
                    return;
                }
                setError('');
                reloadData();
            })
        }
        else{
            if (!objTypes || objTypes.length===0){
                setError('Please add data source.');
                return;
            }
            setError('');
            reloadData();
        }
      

    }

    function reloadData(){
        setLoading(true);
        if (app === 'example') {
            clearData(app, account_id, connector_id).then(data => {

                syncConnectorData(app, account_id, connector_id).then(data => {
                    setLoading(false);
                });
            });
        }
        else{
            syncConnectorData(app, account_id, connector_id).then(data => {
                setLoading(false);
            });
        }

    }



    return (
        <div>

            <div className='row'>

                <div className='col-3'>
                    <span> {app} </span>
                </div>
                <div className='col-3'>
                    {objTypes && objTypes.map(a => (

                        <div key={a}  >
                            <span>{a}</span>
                        </div>
                    ))}
               
                    <span className='red-text'>{error}</span>
                </div>

                <div className='col-2'>
                    <button type="button" className="btn btn-blue-short ml-5" onClick={() => handleReloadData()} >Reload</button>
                </div>
                <div className='col-2'>
                    <button type="button" className="btn btn-blue-short ml-5" onClick={() => onSchemaEdit(app)} >Edit</button>
                </div>
                <div className='col-2'>

                    <PulseLoader color="#2598d6" loading={loading} />

                </div>

            </div>


            <br /><br />
            <ToastContainer />
        </div>
    )
}