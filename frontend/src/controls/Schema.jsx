import React, { useEffect, useState } from 'react';
import { addTemplate, deleteTemplate, getSchemas, getTemplates } from '../api';
import Plus from '../icons/Plus';
import Minus from '../icons/Minus';
import EditIcon from '../icons/EditIcon';
import RemoveIcon from '../icons/RemoveIcon';

export default function Schema({ config }) {
    const [schemas, setSchemas] = useState();
    const [templates, setTemplates] = useState();
    const [showSchemas, setShowSchemas] = useState([]);

    function loadSchemaTemplates() {
        for (var i = 0; i < config['modules'].length; i++) {
            var app = config['name'];
            var module = config['modules'][i];

            getTemplates(app, module).then(data => {
                var _templates = templates ? templates : [];
                var obj_types = []
                for (var j = 0; j < data.length; j++) {
                    _templates.push(data[j]);
                    obj_types.push(data[j].obj_type)
                }

                setTemplates(_templates);

                getSchemas(app, module).then(cdata => {

                    var _schemas = schemas ? schemas : [];
                    for (var z = 0; z < cdata.length; z++) {
                        if (obj_types.indexOf(cdata[z].obj_type) === -1) {
                            _schemas.push(cdata[z]);
                        }
                    }

                    setSchemas(_schemas);
                })
            })
        }
    }



    useEffect(() => {


        loadSchemaTemplates();

    }, []);

    function applyShowSchema(name) {
        var _showSchemas = showSchemas;
        if (!showSchemas) {
            _showSchemas = [];
        }
        var index = showSchemas.indexOf(name);

        if (index === -1) {
            _showSchemas.push(name);
            setShowSchemas([..._showSchemas]);
        }
        else {
            _showSchemas.splice(index, 1);
            setShowSchemas([..._showSchemas]);
        }
    }

    function checkShowSchema(name) {
        return showSchemas.indexOf(name) > -1;
    }

    function addSchema(item) {
        addTemplate(item.app, item.module, item.obj_type, item.schema).then(data => {

            var _templates = templates ? templates : [];
            _templates.push(data);

            setTemplates([..._templates]);
        });
        var _schemas = schemas;
        var index = _schemas.findIndex(f => f.obj_type === item.obj_type);
        if (index > -1) {
            _schemas.splice(index, 1);
            setSchemas([..._schemas]);
        }

    }

    function deleteSchema(template_id) {
        deleteTemplate(template_id);
        var _templates = templates
        var index = _templates.findIndex(f => f.template_id === template_id);
        if (index > -1) {
            _templates.splice(index, 1);
            setTemplates([..._templates]);
        }

    }

    return (
        <div>
            {templates && templates.length > 0 && (<fieldset>
                <legend>Your data schema for index:</legend>
                {templates && templates.map(a => (

                    <div key={a.template_id}>
                        <span>{a.obj_type}</span>
                        <span className="ml-5 svg-icon-sm svg-text cursor-pointer" simple-title='Edit schema' onClick={() => applyShowSchema(a.template_id)}>
                            <EditIcon />
                        </span>

                        <span className="ml-5 svg-icon-sm svg-text cursor-pointer" simple-title='Delete schema' onClick={() => deleteSchema(a.template_id)}>
                            <RemoveIcon />
                        </span>
                        {checkShowSchema(a.template_id) &&
                            (<pre className='json-copy mt-3'>{JSON.stringify(a.schema, null, 2)}</pre>)}

                        <br /><br />
                    </div>

                ))}
            </fieldset>
            )}


            <fieldset>
                <legend>Available data schema</legend>

                {schemas && schemas.map(a => (

                    <div key={a.obj_type}>
                        <span>{a.obj_type}</span>
                        {checkShowSchema(a.obj_type) ?
                            <span className="ml-5 svg-icon-sm svg-text cursor-pointer" simple-title='Hide schema' onClick={() => applyShowSchema(a.obj_type)}>
                                <Minus />
                            </span>
                            : <span className="ml-5 svg-icon-sm svg-text cursor-pointer" simple-title='Show schema' onClick={() => applyShowSchema(a.obj_type)}>
                                <Plus />
                            </span>}

                        <button type="button" className="btn btn-blue ml-5" onClick={() => addSchema(a)} >Add Schema</button>
                        {checkShowSchema(a.obj_type) &&
                            (<pre className='json-copy mt-3'>{JSON.stringify(a.schema, null, 2)}</pre>)}

                        <br /><br />
                    </div>

                ))}
            </fieldset>


        </div>
    );
}
