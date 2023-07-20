import logo from './logo.svg';
import './App.css';
import React, { useEffect, useReducer, useState } from 'react';
import Logo from './assets/images/logo.png';
import axios from 'axios';
import Badge from './controls/Badge';
import Modal from 'react-modal';
import Integration from './controls/Integration';
import Schema from './controls/Schema';
import XIcon from './icons/XIcon';
import InfoIcon from './icons/InfoIcon';
import SelectCtrl from './controls/SelectCtrl';

import { getApps, getConnectors, clearData, syncData, queryData } from './api';

function App() {
  const [page, setPage] = useState(1);
  const [apps, setApps] = useState([]);
  const [connectors, setConnectors] = useState([]);
  const [accountIds, setAccountIds] = useState([]);
  const [connectIds, setConnectIds] = useState([]);
  const [selectAccountId, setSelectAccountId] = useState();
  const [chunkSize, setChunkSize] = useState(2);
  const [selectConnectorId, setSelectConnectorId] = useState();
  const [queryResult, setQueryResult] = useState();
  const [queryText, setQueryText] = useState();
  const [error, setError] = useState();

  function loadConnectors() {
    getConnectors().then(data => {
      setConnectors(data)
    });
  }


  function loadApps() {
    getApps().then(data => {
      setApps(data);
      if (data.length === 0) {
        setPage(2);
      }
      else {
        var _connectIds = [];
        var _accountIds = [];
        for (var i = 0; i < data.length; i++) {
          _connectIds.push(
            { 'label': data[i].connector_id, 'value': data[i].connector_id }
          );

          const accountIndex = _accountIds.findIndex(
            item => item.value === data[i].account_id
          );
          if (accountIndex === -1) {

            _accountIds.push(
              { 'label': data[i].account_id, 'value': data[i].account_id });
          }
        }
        setConnectIds([..._connectIds]);
        setAccountIds([..._accountIds]);
      }
    });
  }

  useEffect(() => {

    loadConnectors();
    loadApps();

  }, []);


  function runSyncData(app, connector_id) {
    syncData(app, connector_id).then(data => {
      loadApps();
    });
  }
  function clearSyncData(app, connector_id) {
    clearData(app, connector_id).then(data => {
      loadApps();
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

    handleOpenModal('schema', app, "Schema " + app.name, modalStyle);
  }

  function closeModal() {
    setModalIsOpen(false);

  }

  function handleSelectAccountChange(id, text, value) {
    setSelectAccountId(value);

  }

  function handleSelectConnectorChange(id, text, value) {
    setSelectConnectorId(value);

  }

  function refreshApps(){
    loadApps();
  }

  function queryDocuments() {
    setError('');
    if (!selectAccountId && !selectConnectorId) {
      setError('Please select either accountId, or connectorId to search.');
      return;
    }

    if (!queryText) {
      setError('Please enter query text to search.');
      return;
    }
    if (!chunkSize) {
      setError('Please enter chunk size between 2 to 10.');
      return;
    }

    var _chunkSize = parseInt(chunkSize);
    if (_chunkSize >= 2  && _chunkSize <= 10) {

    }
    else{
      setError('Please enter chunk size between 2 to 10.');
      return;
    }


    queryData(selectAccountId ? selectAccountId : "", selectConnectorId ? selectConnectorId : "", queryText, chunkSize ? chunkSize : "").then(data => {

      setQueryResult(data);

    }).catch(function (error) {
      if (error.response) {
        setQueryResult(error.response.data);
      }

    });


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
                  setPage(1)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 1 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Your Apps</span>
                </a>
                <a onClick={() =>
                  setPage(2)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 2 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Connectors</span>
                </a>
                <a onClick={() =>
                  setPage(3)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page === 3 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Search</span>
                </a>
              </div>
            </div>
          </div>

        </nav>
      </div>
      <div className='main-content'>

        {page && page === 1 && (
          <div><h2>Your Apps</h2>
          <button type="button" className="btn btn-grey fr" onClick={() => refreshApps()} >Refresh</button>
            {
              apps && apps.length > 0 && (
                <table className="table table-striped">
                  <thead  >
                    <tr>
                      <th scope="col">Account Id</th>
                      <th scope="col">Connector Id</th>
                      <th scope="col">App</th>
                      <th scope="col">Status</th>
                      <th scope="col">Sync</th>
                      <th scope="col">Clear</th>
                    </tr>
                  </thead>
                  <tbody>


                    {apps && apps.map(a => (

                      <tr key={a.connector_id}>
                        <td> <span> {a.account_id} </span></td>
                        <td> <span> {a.connector_id} </span></td>
                        <td> <span> {a.app} </span></td>
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
            <button type="button" className="btn btn-grey" onClick={() => openSearchApiDoc()} >Open API Doc</button><br />
            <br />
            <div className='row'>
              <div className='col-4'>     <SelectCtrl dataSource={accountIds} onSelectChange={handleSelectAccountChange} label={"Select accountId"} selectedValue={selectAccountId} />

              </div>

              <div className='col-4'>     <SelectCtrl dataSource={connectIds} onSelectChange={handleSelectConnectorChange} label={"Select connectorId"} selectedValue={selectConnectorId} />
              </div>
              <div className='col-4'>
                <span className="svg-icon-sm svg-text cursor-pointer" simple-title='Top K chunks from the result, K between 2 to 10' >
                  <InfoIcon />
                </span> Chunk size:<input className='form-control-short' value={chunkSize || ""} onChange={e => setChunkSize(e.target.value)}
                  type="text" />

              </div>
            </div>
            <br />
            <h4>Search query</h4>
            <br />
            <textarea rows="5" cols="50" value={queryText || ""} onChange={e => setQueryText(e.target.value)}></textarea>
            <br />
            <div className='red-text'>{error}</div>
            <br />
            <button type="button" className="btn btn-grey mr-3" onClick={() => queryDocuments()} >Search</button>
            <br />
            {queryResult && (<pre className='json-copy mt-3'>{JSON.stringify(queryResult, null, 2)}</pre>)}

          </div>
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
            <Integration name={modalParam}></Integration>
          </div>

        )}
        {modalType == 'schema' && modalParam && (
          <div >
            <Schema config={modalParam}></Schema>
          </div>

        )}
      </Modal>

    </div>
  );
}

export default App;

