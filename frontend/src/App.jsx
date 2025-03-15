// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

const toPascalCase = (str) => {
  if (!str) return '';
  return str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join('');
};

function App() {
  const [unmapped, setUnmapped] = useState([]);
  const [payers, setPayers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [allGroups, setAllGroups] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true); // Add loading state
  
  const [unmappedPage, setUnmappedPage] = useState(1);
  const [payersPage, setPayersPage] = useState(1);
  const [unmappedTotal, setUnmappedTotal] = useState(0);
  const [payersTotal, setPayersTotal] = useState(0);
  const perPage = 10;

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch unmapped
        const unmappedRes = await axios.get(`http://localhost:5000/api/unmapped?page=${unmappedPage}&per_page=${perPage}`);
        console.log('Unmapped:', unmappedRes.data);
        setUnmapped(unmappedRes.data.unmapped || []);
        setUnmappedTotal(unmappedRes.data.total || 0);

        // Fetch payers
        const payersRes = await axios.get(`http://localhost:5000/api/payers?page=${payersPage}&per_page=${perPage}`);
        console.log('Payers:', payersRes.data);
        setPayers(payersRes.data.payers || []);
        setPayersTotal(payersRes.data.total || 0);

        // Fetch groups (nested)
        const groupsRes = await axios.get('http://localhost:5000/api/groups?per_page=1000');
        console.log('Groups:', groupsRes.data);
        setGroups(groupsRes.data.groups || []);

        // Flatten groups for dropdowns
        const flattenGroups = (groupList, acc = []) => {
          groupList.forEach(group => {
            acc.push({ group_id: group.group_id, group_name: group.group_name });
            if (group.children && group.children.length > 0) flattenGroups(group.children, acc);
          });
          return acc;
        };
        const flatGroups = flattenGroups(groupsRes.data.groups);
        setAllGroups(flatGroups.sort((a, b) => a.group_name.localeCompare(b.group_name)));

        setLoading(false);
      } catch (error) {
        console.error('Fetch Error:', error.message, error.response?.data);
        setError(`Failed to load data: ${error.message}`);
        setLoading(false);
      }
    };
    fetchData();
  }, [unmappedPage, payersPage]);

  const handleMapPayer = (detailId, payerId) => {
    axios.post('http://localhost:5000/api/map_payer', { detail_id: detailId, payer_id: payerId })
      .then(() => {
        setUnmapped(unmapped.filter(item => item.detail_id !== detailId));
        setUnmappedTotal(unmappedTotal - 1);
        alert('Payer mapped successfully!');
      })
      .catch(error => console.error('Error mapping payer:', error));
  };

  const handleUpdatePrettyName = (payerId, prettyName) => {
    axios.post('http://localhost:5000/api/update_pretty_name', { payer_id: payerId, pretty_name: prettyName })
      .then(() => {
        setPayers(payers.map(p => p.payer_id === payerId ? { ...p, pretty_name: prettyName } : p));
        alert('Pretty name updated!');
      })
      .catch(error => console.error('Error updating pretty name:', error));
  };

  const handleUpdateGroup = (payerId, groupId) => {
    if (groupId === 'NEW_GROUP') return;

    axios.post('http://localhost:5000/api/update_group', { payer_id: payerId, group_id: groupId })
      .then(() => {
        setPayers(payers.map(p => p.payer_id === payerId ? { ...p, group_id: groupId } : p));
        if (!allGroups.find(g => g.group_id === groupId)) {
          axios.get('http://localhost:5000/api/groups?per_page=1000')
            .then(response => {
              const flattenGroups = (groupList, acc = []) => {
                groupList.forEach(group => {
                  acc.push({ group_id: group.group_id, group_name: group.group_name });
                  if (group.children && group.children.length > 0) flattenGroups(group.children, acc);
                });
                return acc;
              };
              setAllGroups(flattenGroups(response.data.groups).sort((a, b) => a.group_name.localeCompare(b.group_name)));
            });
        }
        alert('Group updated!');
      })
      .catch(error => console.error('Error updating group:', error));
  };

  const handleNewGroup = (payerId, newGroupId) => {
    if (!newGroupId) return;
    const formattedGroupId = toPascalCase(newGroupId);
    axios.post('http://localhost:5000/api/update_group', { payer_id: payerId, group_id: formattedGroupId })
      .then(() => {
        setPayers(payers.map(p => p.payer_id === payerId ? { ...p, group_id: formattedGroupId } : p));
        const newGroup = { group_id: formattedGroupId, group_name: formattedGroupId };
        const updatedGroups = [...allGroups, newGroup].sort((a, b) => a.group_name.localeCompare(b.group_name));
        setAllGroups(updatedGroups);
        alert('New group added and assigned!');
      })
      .catch(error => console.error('Error adding new group:', error));
  };

  const groupedPayers = payers.reduce((acc, payer) => {
    const groupId = payer.group_id || 'UNASSIGNED';
    if (!acc[groupId]) acc[groupId] = [];
    acc[groupId].push(payer);
    return acc;
  }, {});

  const renderGroup = (group, level = 0) => {
    const groupPayers = groupedPayers[group.group_id] || [];
    return (
      <div key={group.group_id} style={{ marginLeft: `${level * 20}px`, marginBottom: '20px' }}>
        <h3>{toPascalCase(group.group_name)} ({groupPayers.length})</h3>
        {groupPayers.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Group</th>
              </tr>
            </thead>
            <tbody>
              {groupPayers.map(payer => (
                <tr key={payer.payer_id}>
                  <td>{payer.payer_id}</td>
                  <td>{toPascalCase(payer.payer_name)}</td>
                  <td>
                    <select
                      value={payer.group_id || ''}
                      onChange={(e) => handleUpdateGroup(payer.payer_id, e.target.value)}
                    >
                      <option value="">Select Group</option>
                      {allGroups.map(g => (
                        <option key={g.group_id} value={g.group_id}>
                          {toPascalCase(g.group_name)}
                        </option>
                      ))}
                      <option value="NEW_GROUP">New Group...</option>
                    </select>
                    {payer.group_id === 'NEW_GROUP' && (
                      <input
                        type="text"
                        placeholder="Enter new group ID"
                        onBlur={(e) => handleNewGroup(payer.payer_id, e.target.value)}
                      />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {group.children && group.children.map(child => renderGroup(child, level + 1))}
      </div>
    );
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div>
      <h1>Dental Payer Management</h1>
      <div className="container">
        <div className="pane">
          <h2>Unmapped Payers ({unmappedTotal})</h2>
          {unmapped.length === 0 ? (
            <p>No unmapped payers</p>
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
                      <td>{toPascalCase(item.payer_name)}</td>
                      <td>{item.payer_id}</td>
                      <td>
                        <select onChange={(e) => handleMapPayer(item.detail_id, e.target.value)}>
                          <option value="">Select</option>
                          {payers.map(payer => (
                            <option key={payer.payer_id} value={payer.payer_id}>
                              {toPascalCase(payer.pretty_name || payer.payer_name)}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ marginTop: '10px' }}>
                <button onClick={() => setUnmappedPage(unmappedPage - 1)} disabled={unmappedPage === 1}>Previous</button>
                <span> Page {unmappedPage} of {Math.ceil(unmappedTotal / perPage)} </span>
                <button onClick={() => setUnmappedPage(unmappedPage + 1)} disabled={unmappedPage >= Math.ceil(unmappedTotal / perPage)}>Next</button>
              </div>
            </>
          )}
        </div>

        <div className="pane">
          <h2>Pretty Names ({payersTotal})</h2>
          {payers.length === 0 ? (
            <p>No payers</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Pretty Name</th>
                  </tr>
                </thead>
                <tbody>
                  {payers.map(payer => (
                    <tr key={payer.payer_id}>
                      <td>{payer.payer_id}</td>
                      <td>{toPascalCase(payer.payer_name)}</td>
                      <td>
                        <input
                          type="text"
                          defaultValue={toPascalCase(payer.pretty_name)}
                          onBlur={(e) => handleUpdatePrettyName(payer.payer_id, e.target.value)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ marginTop: '10px' }}>
                <button onClick={() => setPayersPage(payersPage - 1)} disabled={payersPage === 1}>Previous</button>
                <span> Page {payersPage} of {Math.ceil(payersTotal / perPage)} </span>
                <button onClick={() => setPayersPage(payersPage + 1)} disabled={payersPage >= Math.ceil(payersTotal / perPage)}>Next</button>
              </div>
            </>
          )}
        </div>

        <div className="pane">
          <h2>Payer Hierarchies ({payersTotal})</h2>
          {payers.length === 0 || groups.length === 0 ? (
            <p>No groups or payers</p>
          ) : (
            <>
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {groups.map(group => renderGroup(group))}
                {groupedPayers['UNASSIGNED'] && (
                  <div style={{ marginBottom: '20px' }}>
                    <h3>UNASSIGNED ({groupedPayers['UNASSIGNED'].length})</h3>
                    <table>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Name</th>
                          <th>Group</th>
                        </tr>
                      </thead>
                      <tbody>
                        {groupedPayers['UNASSIGNED'].map(payer => (
                          <tr key={payer.payer_id}>
                            <td>{payer.payer_id}</td>
                            <td>{toPascalCase(payer.payer_name)}</td>
                            <td>
                              <select
                                value={payer.group_id || ''}
                                onChange={(e) => handleUpdateGroup(payer.payer_id, e.target.value)}
                              >
                                <option value="">Select Group</option>
                                {allGroups.map(g => (
                                  <option key={g.group_id} value={g.group_id}>
                                    {toPascalCase(g.group_name)}
                                  </option>
                                ))}
                                <option value="NEW_GROUP">New Group...</option>
                              </select>
                              {payer.group_id === 'NEW_GROUP' && (
                                <input
                                  type="text"
                                  placeholder="Enter new group ID"
                                  onBlur={(e) => handleNewGroup(payer.payer_id, e.target.value)}
                                />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
              <div style={{ marginTop: '10px' }}>
                <button onClick={() => setPayersPage(payersPage - 1)} disabled={payersPage === 1}>Previous</button>
                <span> Page {payersPage} of {Math.ceil(payersTotal / perPage)} </span>
                <button onClick={() => setPayersPage(payersPage + 1)} disabled={payersPage >= Math.ceil(payersTotal / perPage)}>Next</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;