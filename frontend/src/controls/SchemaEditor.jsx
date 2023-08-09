
import React, { useEffect, useState } from 'react';
import SelectCtrl from '../controls/SelectCtrl';
import { updateTemplate } from '../api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ChunkingTypes } from '../references';
import InfoIcon from '../icons/InfoIcon';

export default function SchemaEditor({ item }) {

    const [chunkSize, setChunkSize] = useState();
    const [chunkOverlap, setChunkOverlap] = useState();

    const [chukingType, setChunkingType] = useState();

    function handleChunkingTypeChange(id, text, value) {
        setChunkingType(value);
    }

    useEffect(() => {

        if (item && item.chunking_type && item.chunking_type.chunking_type) {

            setChunkingType(item.chunking_type.chunking_type);
        }

        if (item && item.chunking_type && item.chunking_type.chunking_type === 'custom') {

            setChunkSize(item.chunking_type.chunk_size);
            setChunkOverlap(item.chunking_type.chunk_overlap);
        }


    }, []);

    function saveChunkingType(templateId) {

        var chunkingTypeObj = { 'chunking_type': chukingType };
        if (chukingType === 'custom') {
            chunkingTypeObj.chunk_size = chunkSize ? chunkSize : 256;
            chunkingTypeObj.chunk_overlap = chunkOverlap ? chunkOverlap : 20;
        }

        updateTemplate(templateId, chunkingTypeObj).then(data => {
            handleNotification('Saved');
        });
    }

    function handleNotification(actionType) {
        toast.info(CustomToastWithLink(actionType),
            { position: toast.POSITION.TOP_CENTER, autoClose: false, type: "success" });

    }

    const CustomToastWithLink = (text) => (
        <div>
            {text}
        </div>
    );

    return (
        <div>

            <div className='row'>

                <div className='col-4'>
                    Chunking type:
                    <SelectCtrl dataSource={ChunkingTypes} onSelectChange={handleChunkingTypeChange} label={"Select chunking type"} selectedValue={item.chunking_type ? item.chunking_type.chunking_type : 'document'} />
                </div>

                <div className='col-3'>
                    {(chukingType === 'custom') && (<> <span className="svg-icon-sm svg-text cursor-pointer" simple-title='Suggested chunk size is between 256 and 512' >
                        <InfoIcon />
                    </span>Chunk size: <input className='form-control-short' value={chunkSize || "256"} onChange={e => setChunkSize(e.target.value)}
                        type="text" /></>)}
                </div>
                <div className='col-3'>
                    {(chukingType === 'custom') && (<>Chunk overlap: <input className='form-control-short' value={chunkOverlap || ""} onChange={e => setChunkOverlap(e.target.value)}
                        type="text" /></>)}
                </div>
                <div className='col-2'>
                    <button type="button" className="btn btn-blue" onClick={() => saveChunkingType(item.template_id)} >Save</button>
                </div>

            </div>


            <pre className='json-copy mt-3'>{JSON.stringify(item.schema, null, 2)}</pre>
            <br /><br />
            <ToastContainer />
        </div>
    )
}