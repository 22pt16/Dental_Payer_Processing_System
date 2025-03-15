import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

function App() {
  const [unmapped, setUnmapped] = useState([]);
  const [payers, setPayers] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 10;

  useEffect(() => {
    axios.get(`http://localhost:5000/api/unmapped?page=${page}&per_page=${perPage}`)
      .then(response => {
        setUnmapped(response.data.unmapped);
        setTotal(response.data.total);
      })
      .catch(error => setError('Failed to load unmapped payers'));

    axios.get('http://localhost:5000/api/payers')
      .then(response => setPayers(response.data))
      .catch(error => setError('Failed to load payers'));
  }, [page]);

  const handleMapPayer = (detailId, payerId) => {
    axios.post('http://localhost:5000/api/map_payer', { detail_id: detailId, payer_id: payerId })
      .then(() => {
        setUnmapped(unmapped.filter(item => item.detail_id !== detailId));
        alert('Payer mapped successfully!');
      })
      .catch(error => console.error('Error mapping payer:', error));
  };

  const handleUpdatePrettyName = (payerId, prettyName) => {
    axios.post('http://localhost:5000/api/update_pretty_name', { payer_id: payerId, pretty_name: prettyName })
      .then(() => alert('Pretty name updated!'))
      .catch(error => console.error('Error updating pretty name:', error));
  };

  const handleUpdateGroup = (payerId, groupId) => {
    console.log(`Update ${payerId} to group ${groupId}`);
  };

  if (error) return <div style={{ color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div>
      <h1>Dental Payer Management</h1>
      <div className="container">
        <div className="pane">
          <h2>Unmapped Payers ({total})</h2>
          {unmapped.length === 0 ? (
            <p>Loading...</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>ID</th>
                    <th>Map To</th>
                  </tr>
                </thead>
                <tbody>
                  {unmapped.map(item => (
                    <tr key={item.detail_id}>
                      <td>{item.payer_name}</td>
                      <td>{item.payer_id}</td>
                      <td>
                        <select onChange={(e) => handleMapPayer(item.detail_id, e.target.value)}>
                          <option value="">Select</option>
                          {payers.map(payer => (
                            <option key={payer.payer_id} value={payer.payer_id}>
                              {payer.pretty_name || payer.payer_name}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ marginTop: '10px' }}>
                <button onClick={() => setPage(page - 1)} disabled={page === 1}>Previous</button>
                <span> Page {page} of {Math.ceil(total / perPage)} </span>
                <button onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / perPage)}>Next</button>
              </div>
            </>
          )}
        </div>

        <div className="pane">
          <h2>Pretty Names</h2>
          {payers.length === 0 ? (
            <p>Loading...</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Pretty Name</th>
                </tr>
              </thead>
              <tbody>
                {payers.slice(0, 10).map(payer => (
                  <tr key={payer.payer_id}>
                    <td>{payer.payer_id}</td>
                    <td>{payer.payer_name}</td>
                    <td>
                      <input
                        type="text"
                        defaultValue={payer.pretty_name}
                        onBlur={(e) => handleUpdatePrettyName(payer.payer_id, e.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="pane">
          <h2>Payer Hierarchies</h2>
          {payers.length === 0 ? (
            <p>Loading...</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Group</th>
                  </tr>
                </thead>
                <tbody>
                  {payers.slice(0, 10).map(payer => (
                    <tr key={payer.payer_id}>
                      <td>{payer.payer_id}</td>
                      <td>{payer.payer_name}</td>
                      <td>
                        <input
                          type="text"
                          defaultValue={payer.group_id}
                          onBlur={(e) => handleUpdateGroup(payer.payer_id, e.target.value)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p style={{ fontSize: '12px', color: '#666' }}>Hierarchy not fully implemented—edit manually.</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;