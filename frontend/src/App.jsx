// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [unmapped, setUnmapped] = useState([]);
  const [payers, setPayers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch unmapped rows
    axios.get('http://localhost:5000/api/unmapped', { withCredentials: false })
      .then(response => {
        console.log('Unmapped data:', response.data);
        setUnmapped(response.data);
      })
      .catch(error => {
        console.error('Error fetching unmapped:', error);
        setError('Failed to load unmapped payers');
      });

    // Fetch payers
    axios.get('http://localhost:5000/api/payers', { withCredentials: false })
      .then(response => {
        console.log('Payers data:', response.data);
        setPayers(response.data);
      })
      .catch(error => {
        console.error('Error fetching payers:', error);
        setError('Failed to load payers');
      });
  }, []);

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

  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Dental Payer Mapping</h1>
      
      <h2>Unmapped Payers ({unmapped.length})</h2>
      {unmapped.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Payer Name</th>
              <th>Payer ID</th>
              <th>Source</th>
              <th>State</th>
              <th>Map To</th>
            </tr>
          </thead>
          <tbody>
            {unmapped.map(item => (
              <tr key={item.detail_id}>
                <td>{item.payer_name}</td>
                <td>{item.payer_id}</td>
                <td>{item.source}</td>
                <td>{item.state}</td>
                <td>
                  <select onChange={(e) => handleMapPayer(item.detail_id, e.target.value)}>
                    <option value="">Select Payer</option>
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
      )}

      <h2>Update Pretty Names</h2>
      {payers.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Payer ID</th>
              <th>Payer Name</th>
              <th>Pretty Name</th>
            </tr>
          </thead>
          <tbody>
            {payers.map(payer => (
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
  );
}

export default App;