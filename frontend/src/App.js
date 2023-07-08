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
import { getApps, getConnectors, clearData, syncData } from './api';

function App() {
  const [page, setPage] = useState(1);
  const [apps, setApps] = useState([]);
  const [connectors, setConnectors] = useState([]);


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
    });
  }

  useEffect(() => {

    loadConnectors();
    loadApps();

  }, []);


  function runSyncData(app, instance_id) {
    syncData(app, instance_id).then(data => {
      loadApps();
    });
  }
  function clearSyncData(app, instance_id) {
    clearData(app, instance_id).then(data => {
      loadApps();
    });
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
              </div>
            </div>
          </div>

        </nav>
      </div>
      <div className='main-content'>

        {page && page === 1 && (
          <div><h2>Your Apps</h2>
            {
              apps && apps.length > 0 && (
                <table className="table table-striped">
                  <thead  >
                    <tr>

                      <th scope="col">Instance Id</th>
                      <th scope="col">App</th>
                      <th scope="col">Status</th>
                      <th scope="col">Sync</th>
                      <th scope="col">Clear</th>
                    </tr>
                  </thead>
                  <tbody>


                    {apps && apps.map(a => (

                      <tr key={a.instance_id}>
                        <td> <span> {a.instance_id} </span></td>
                        <td> <span> {a.app} </span></td>
                        <td> <span> {a.sync_status} </span></td>
                        <td>    <button type="button" className="btn btn-blue-short ml-5"  onClick={() => runSyncData(a.app, a.instance_id)} >Sync now</button>
                        </td>
                        <td>       <button type="button" className="btn btn-blue-short ml-5" simple-title="Reindex data" onClick={() => clearSyncData(a.app, a.instance_id)} >Clear data</button>
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

