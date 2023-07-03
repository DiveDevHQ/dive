import logo from './logo.svg';
import './App.css';
import React, { useEffect, useReducer, useState } from 'react';
import Logo from './assets/images/logo.png';
import axios from 'axios';
import Badge from './control/Badge';

function App() {
  const [page, setPage] = useState(1);
  const [apps, setApps] = useState([]);
  const [connectors, setConnectors] = useState([]);
  const API_URL = "http://localhost:8000"

  useEffect(() => {
    function loadConnectors() {
      axios
        .get(API_URL + "/integrations/connectors")
        .then(res => { setConnectors(res.data); })
        .catch(err => console.log(err));
    }


    function loadApps() {
      axios
        .get(API_URL + "/apps")
        .then(res => {
          setApps(res.data);

          if (res.data.length == 0) {
            setPage(2);
          }
        })
        .catch(err => console.log(err));
    }

    loadConnectors();
    loadApps();

  }, []);



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
                  <span className={page == 1 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Your Apps</span>
                </a>
                <a onClick={() =>
                  setPage(2)
                } className="nav__link">
                  <i className='bx bx-compass nav__icon' ></i>
                  <span className={page == 2 ? "nav__name cursor-pointer active-menu" : "nav__name cursor-pointer inactive-menu"}>Connectors</span>
                </a>



              </div>
            </div>
          </div>

        </nav>
      </div>
      <div className='main-content'>

        {page && page == 1 && (
          <div><h2>Your Apps</h2>
            {
              apps && apps.length > 0 && (
                <table className="table table-striped">
                  <thead  >
                    <tr>

                      <th scope="col">Instance Id</th>
                      <th scope="col">App</th>
                      <th scope="col">Status</th>
                    </tr>
                  </thead>
                  <tbody>


                    {apps && apps.map(a => (

                      <tr key={a.instance_id}>
                        <td> <span> {a.instance_id} </span></td>
                        <td> <span> {a.app} </span></td>
                        <td> <span> {a.sync_status} </span></td>

                      </tr>


                    ))}
                  </tbody>

                </table>
              )
            }
            {apps && apps.map(c => (
              <div className='connector-block'>

                <div className='row'>
                  <div className='col-3'></div>
                </div>
              </div>
            ))}
          </div>)}
        {page && page == 2 && (
          <div> <h2>Connectors</h2>

            <div className='d-flex flex-1 flex-wrap-wrap'>
              {connectors && connectors.map(c => (
                <div className='connector-block'>

                  <Badge
                    value={c.name} capitalize={true} /> <br />
                  <button type="button" className="btn btn-grey" onClick={() => window.open(API_URL + "/integrations/connect/" + c.name)} >Connect</button>

                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;

