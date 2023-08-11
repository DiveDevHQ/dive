import logo from './logo.svg';
import './App.css';
import React, { useEffect, useReducer, useState } from 'react';
import Logo from './assets/images/logo.png';
import LogoDark from './assets/images/logo_dark.png';
import axios from 'axios';
import Badge from './controls/Badge';
import Modal from 'react-modal';
import Integration from './controls/Integration';
import Schema from './controls/Schema';
import XIcon from './icons/XIcon';
import InfoIcon from './icons/InfoIcon';
import SelectCtrl from './controls/SelectCtrl';
import DocumentCtrl from './controls/DocumentCtrl';
import FileUpload from './controls/FileUpload'
import { PulseLoader } from 'react-spinners';
import './index.css'

import { createClient } from '@supabase/supabase-js'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa, ThemeMinimal } from '@supabase/auth-ui-shared'
import { getApps, getConnectors, clearData, syncConnectorData, queryData, setupVector, authWithPublicData, syncAccountData, getAccountTemplates } from './api';

const supabase = createClient(process.env.REACT_APP_SUPABASE_CLIENT, process.env.REACT_APP_SUPABASE_ANON_KEY)


function App() {
  const [page, setPage] = useState(4);
  const [apps, setApps] = useState([]);
  const [connectors, setConnectors] = useState([]);
  const [filters, setFilters] = useState([]);
  const [selectAccountId, setSelectAccountId] = useState();
  const [chunkSize, setChunkSize] = useState();
  const [selectedFilter, setSelectedFilter] = useState();
  const [queryResult, setQueryResult] = useState();
  const [queryText, setQueryText] = useState();
  const [error, setError] = useState();
  const [loading, setLoading] = useState(true);
  const [instruction, setInstruction] = useState();
  const [session, setSession] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [message, setMessage] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)

    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })
    setTimeout(() => {
      setInitialized(true);
    }, 500);

    return () => subscription.unsubscribe()
  }, [])



  function setup() {
    setupVector().then(data => {
      setLoading(false);
    });
  }

  function loadConnectors() {
    getConnectors().then(data => {
      setConnectors(data);
      loadApps();
    });
  }


  function loadApps() {

    getApps(session.user.id).then(data => {
   
      setApps(data);
      if (data.length === 0) {
        setPage(4);
      }
      else {

        var _filters = [];
        _filters.unshift({ 'label': 'All documents', 'value': 'account_id|' + session.user.id });

        for (var i = 0; i < data.length; i++) {
          _filters.push(
            { 'label': 'All documents from ' + data[i].connector_id, 'value': 'connector_id|' + data[i].connector_id }
          );
        }
        getAccountTemplates(session.user.id).then(data => {

          for (var i = 0; i < data.length; i++) {
            _filters.push(
              { 'label': data[i]['obj_type'], 'value': 'obj_type|' + data[i]['obj_type'] });
          }
          setFilters([..._filters]);

        })

      }
    });

  }

  useEffect(() => {
    setup();

  }, []);

  useEffect(() => {
    if (session) {
      loadConnectors();
    }

  }, [session]);



  function runSyncData(app, connector_id) {
    setLoading(true);
    syncConnectorData(app, session.user.id, connector_id).then(data => {
      loadApps();
      setLoading(false);
    });
  }
  function clearSyncData(app, connector_id) {
    setLoading(true);
    clearData(app, session.user.id, connector_id).then(data => {
      loadApps();
      setLoading(false);
    });
  }

  function openSearchApiDoc() {
    window.open('https://docs.diveapi.co/#search', "_blank");
  }

  const [modalType, setModalType] = useState()
  const [modalParam, setModalParam] = useState()
  const [modalTitle, setModalTitle] = useState("")


  const [modalStyle, setModalStyle] = useState({
    content: {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
    },

  })

  let subtitle;
  const [modalIsOpen, setModalIsOpen] = React.useState(false);

  function handleOpenModal(type, param, modalTitle, modalStyle) {

    setModalType(type);
    setModalParam(param);
    setModalTitle(modalTitle)
    setModalStyle(modalStyle);
    setModalIsOpen(true);
  }

  function afterOpenModal() {
    // references are now sync'd and can be accessed.
    subtitle.style.color = '#424242';
  }


  function openConnector(name) {

    var modalStyle = {
      content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        height: '700px',
        width: '800px',
        transform: 'translate(-50%, -50%)',
      },
    };
    handleOpenModal('integration', name, "Connect " + name, modalStyle);
  }


  function openFileUploader() {

    var modalStyle = {
      content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        height: '700px',
        width: '800px',
        transform: 'translate(-50%, -50%)',
      },
    };
    handleOpenModal('file', 'file', "File Uploader ", modalStyle);
  }

  function getSchema(name) {
    return connectors.find(
      item => item.name === name
    );

  }

  function hanldeSchemaEdit(app) {
    openSchema(getSchema(app));
  }


  function openSchema(app) {

    var modalStyle = {
      content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        height: '700px',
        width: '800px',
        transform: 'translate(-50%, -50%)',
      },
    };

    handleOpenModal('schema', app, app.name + " settings", modalStyle);
  }

  function closeModal() {
    setModalIsOpen(false);

  }

  function handleSelectAccountChange(id, text, value) {
    setSelectAccountId(value);

  }

  function handleSelectConnectorChange(id, text, value) {
    setSelectedFilter(value);

  }

  function refreshApps() {
    setApps([]);
    loadApps();
  }

  function testDocuments() {
    authWithPublicData('example', session.user.id).then(data => {
      loadApps();
      openSchema(getSchema('example'));
    })
  }

  function queryDocuments(query_type) {
    setError('');


    if (!queryText) {
      setError('Please enter query text to search.');
      return;
    }
   
    if (!selectedFilter) {
      setError('Please select a data source.');
      return;
    }
    /*
    var _chunkSize = parseInt(chunkSize);
    if (_chunkSize >= 2 && _chunkSize <= 10) {

    }
    else {
      setError('Please enter chunk size between 2 to 10.');
      return;
    }*/
    setQueryResult(null);
    setLoading(true);
    var connectorId = '';
    var obj_type = '';
    var filterParts = selectedFilter.split('|');

    if (filterParts[0] == 'account_id') {
      connectorId = '';
    }
    else if (filterParts[0] == 'connector_id') {
      connectorId = filterParts[1];
    }
    else if (filterParts[0] == 'obj_type') {
      obj_type = filterParts[1];
    }



    queryData(session.user.id, connectorId, obj_type,
      queryText, chunkSize ? chunkSize : "", instruction ? instruction : "", query_type?query_type:"").then(data => {
        setQueryResult(data);
        setLoading(false);

      }).catch(function (error) {
        if (error.response) {
          setQueryResult(error.response.data);
          setLoading(false);
        }

      });

  }

  function prepareQueryData() {
    setLoading(true);
    setMessage('Peparing your data, it can take up to 3 mins...');
    syncAccountData(session.user.id).then(
      data => {
        setLoading(false);
        setMessage('');
        setPage(3);
      }
    )

  }



  if (!initialized) {
    return (<></>)
  }

  if (initialized && !session) {
    return (<div>
      <div className='row'>
        <div className='col-6'><div className='login-content' >
          <Auth supabaseClient={supabase} appearance={{ theme: ThemeSupa }} providers={['google']} /></div></div>
        <div className='col-6'> <div className='logo-content'><div className='logo'>
          <div className='logo-image'><img src={LogoDark} width="300px" /></div>
          <div className='logo-text'>LLM Powered Tool For Venture Capitalists</div>
        </div> </div>

        </div>
      </div>
    </div>)
  }

  return (
    <div>
      <div className="nav" id="navbar">
        <nav className="nav__container">
          <div>
            <div className="nav__list">

              <div className="nav__items">
                <img src={Logo} height="40px" width="60px" />

                <h3 className="nav__subtitle">Menu</h3>

                <a onClick={() =>
                  setPage(4)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 4 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Documents</span>
                </a>

                 <a onClick={() =>
                  setPage(1)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 1 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Your Apps</span>
                </a>
              {/*   <a onClick={() =>
                  setPage(2)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 2 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Connectors</span>
                </a>*/}
                <a onClick={() =>
                  setPage(3)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 3 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Playground</span>
                </a>
              </div>
            </div>
          </div>

        </nav>
      </div>
      <div className='main-content'>
        <div className='mb-1'>
          <div className='loading'>

            <PulseLoader color="#2598d6" loading={loading} /> &nbsp;
            <span className='blue-text-large ml-5'>{message}</span>
          </div>




        </div>
        {page && page === 1 && (
          <div><h2>Your Apps</h2>
            <button type="button" className="btn btn-grey fr" onClick={() => refreshApps()} >Refresh</button>
            {
              apps && apps.length > 0 && (
                <table className="table table-striped">
                  <thead  >
                    <tr>
                      {/*   <th scope="col">Account Id</th> */}
                      <th scope="col">Connector Id</th>
                      <th scope="col">App</th>
                      <th scope="col">Data</th>
                      <th scope="col">Status</th>
                      <th scope="col">Sync</th>
                      <th scope="col">Clear</th>
                    </tr>
                  </thead>
                  <tbody>


                    {apps && apps.map(a => (

                      <tr key={a.connector_id}>
                        {/*<td> <span> {a.account_id} </span></td> */}
                        <td> <span> {a.connector_id} </span></td>
                        <td> <span> {a.app} </span></td>
                        <td> <button type="button" className="btn btn-blue-short ml-5" onClick={() => openSchema(getSchema(a.app))} >Data Source</button></td>
                        <td> <span> {a.sync_status} </span></td>
                        <td>    <button type="button" className="btn btn-blue-short ml-5" onClick={() => runSyncData(a.app, a.connector_id)} >Sync now</button>
                        </td>
                        <td>       <button type="button" className="btn btn-blue-short ml-5" simple-title="Reindex data" onClick={() => clearSyncData(a.app, a.connector_id)} >Clear data</button>
                        </td>
                      </tr>


                    ))}
                  </tbody>

                </table>
              )
            }

          </div>)}
        {page && page === 2 && (
          <div> <h2>Connectors</h2>

            <div className='d-flex flex-1 flex-wrap-wrap'>
              {connectors && connectors.map(c => (
                <div className='connector-block' key={c.name}>

                  <Badge
                    value={c.name} capitalize={true} /> <br />
                  <button type="button" className="btn btn-grey" onClick={() => openConnector(c.name)} >Connect</button><br />
                  <button type="button" className="btn btn-blue mt-3" onClick={() => openSchema(c)} >Schema</button>

                </div>
              ))}
            </div>
          </div>
        )}
        {page && page === 3 && (
          <div> <h2>Search</h2>
            {/*<button type="button" className="btn btn-grey" onClick={() => openSearchApiDoc()} >Open API Doc</button><br />*/}
            <br />
            <div className='row'>
              <div className='col-6'>
                <input className='form-control  ml-2' value={queryText || ""} onChange={e => setQueryText(e.target.value)}
                  placeholder='Enter your question'
                  type="text" />
              </div>
              <div className='col-5'>
                <SelectCtrl dataSource={filters} onSelectChange={handleSelectConnectorChange} label={"Select Data Source"} selectedValue={selectedFilter} />
              </div>
              <div className='col-1'>

              <button type="button" className="btn btn-grey mr-5" onClick={() => queryDocuments()} >Search</button>
       
              </div>
            </div>

            <br />

           {/* <div className='row'>
              <div className='col-4'>     <SelectCtrl dataSource={accountIds} onSelectChange={handleSelectAccountChange} label={"Select accountId"} selectedValue={selectAccountId} />

        </div> 

 <div className='col-4'>
                <span className="svg-icon-sm svg-text cursor-pointer" simple-title='Top K chunks from the result, K between 2 to 10' >
                  <InfoIcon />
                </span> Top K:<input className='form-control-short ml-2' value={chunkSize || ""} onChange={e => setChunkSize(e.target.value)}
                  type="text" />
              </div> 
             
            </div>*/}
            <br />


            {/*<div className='row'><div className='col-8'>
              Instructions (optional):  <input className='form-control  ml-2' value={instruction || ""} onChange={e => setInstruction(e.target.value)}
                placeholder='Enter prompt for your question'
                type="text" />
      </div>
              <div className='col-4'>
                <span className='small-grey-text'>e.g. Summerize your response in no more than 5 lines</span>
              </div>
            </div>

            <br />
            <br />
*/}

            <div className='red-text'>{error}</div>
          {/*  <br />
            <button type="button" className="btn btn-grey mr-5" onClick={() => queryDocuments()} >Short Answer</button>
            <button type="button" className="btn btn-grey mr-5" onClick={() => queryDocuments('summary')} >Summary</button>
<br />
            {queryResult && (<pre className='json-copy mt-3'>{JSON.stringify(queryResult, null, 2)}</pre>)}*/}
             {queryResult &&(<span className='query-result'>{queryResult.result}</span>)}


          </div>
        )}

        {page && page === 4 && (
          <>
            <div className='row'>
              <div className='col-4'>
                <button type="button" className="btn btn-grey mr-5" onClick={() => testDocuments()} >Try Test Docs</button>
              </div>
              <div className='col-4'>
                <button type="button" className="btn btn-grey mr-5" onClick={() => openFileUploader()} >Upload Files</button>
              </div>

            </div>
            <div className='mt-5'>
              {
                apps && apps.length > 0 && (
                  <>
                    <h4> Your documents</h4>

                    {apps && apps.map(a => (

                      <div key={a.connector_id} className=' mt-3'>
                        <DocumentCtrl account_id={session.user.id} connector_id={a.connector_id} app={a.app} onSchemaEdit={hanldeSchemaEdit} />

                      </div>
                    ))}
                    <button type="button" className="btn btn-grey mr-5" onClick={() => prepareQueryData()} >Query My Data</button>

                  </>
                )
              }
            </div>
          </>
        )}
      </div>
      <Modal
        isOpen={modalIsOpen}
        onAfterOpen={afterOpenModal}
        onRequestClose={closeModal}
        ariaHideApp={false}
        contentLabel="Modal"
        style={modalStyle}
      >
        <h2 ref={(_subtitle) => (subtitle = _subtitle)}>{modalTitle}
          <span onClick={closeModal} className="svg-icon-sm svg-text cursor-pointer  fr">
            <XIcon /> </span></h2>


        <br />
        {modalType == 'integration' && modalParam && (
          <div >
            <Integration name={modalParam} account_id={session.user.id}></Integration>
          </div>

        )}
        {modalType == 'schema' && modalParam && (
          <div >
            <Schema config={modalParam} account_id={session.user.id}></Schema>
          </div>

        )}

        {modalType == 'file' && modalParam && (
          <div >
            <h4>Deck</h4>
            <FileUpload fileType="deck" account_id={session.user.id} onUploadFile={refreshApps} />
          </div>

        )}

      </Modal>

    </div>
  );
}

export default App;

