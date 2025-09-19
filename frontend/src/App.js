import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

function App() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/items/');
      setItems(response.data);
    } catch (error) {
      console.error('Error fetching items:', error);
    } finally {
      setLoading(false);
    }
  };

  const createItem = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await axios.post('/api/v1/items/', newItem);
      setNewItem({ title: '', description: '' });
      fetchItems();
    } catch (error) {
      console.error('Error creating item:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (itemId) => {
    try {
      setLoading(true);
      await axios.delete(`/api/v1/items/${itemId}`);
      fetchItems();
    } catch (error) {
      console.error('Error deleting item:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>FastAPI DocumentDB Application</h1>
        
        <div className="form">
          <h2>Add New Item</h2>
          <form onSubmit={createItem}>
            <input
              type="text"
              placeholder="Title"
              value={newItem.title}
              onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Description"
              value={newItem.description}
              onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Item'}
            </button>
          </form>
        </div>

        <div>
          <h2>Items</h2>
          {loading && <p>Loading...</p>}
          <ul className="item-list">
            {items.map((item) => (
              <li key={item.id} className="item">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <button onClick={() => deleteItem(item.id)}>Delete</button>
              </li>
            ))}
          </ul>
          {items.length === 0 && !loading && (
            <p>No items found. Add some items to get started!</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;