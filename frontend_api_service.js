/**
 * api.js — API service layer for Mehal Lab Inventory System
 * 
 * Drop this file into your React project (e.g., src/api.js)
 * and import it into your components.
 * 
 * Usage:
 *   import api from './api';
 *   const { access_token } = await api.login('Mehal', 'mehal123');
 *   const inventory = await api.getInventory({ search: 'antibody' });
 */

const BASE_URL = 'http://localhost:8000/api';

// ─── Token Management ───
let authToken = null;

export function setToken(token) {
  authToken = token;
  localStorage.setItem('mehal_lab_token', token);
}

export function getToken() {
  if (!authToken) {
    authToken = localStorage.getItem('mehal_lab_token');
  }
  return authToken;
}

export function clearToken() {
  authToken = null;
  localStorage.removeItem('mehal_lab_token');
}

// ─── Base Fetch Wrapper ───
async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.location.reload(); // Force re-login
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle CSV downloads (non-JSON responses)
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('text/csv')) {
    return response.blob();
  }

  return response.json();
}


// ═══════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════
const api = {
  /** Login and receive JWT token */
  async login(username, password) {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    setToken(data.access_token);
    return data;
  },

  /** Get current user info */
  async getMe() {
    return apiFetch('/auth/me');
  },

  /** Logout (client-side) */
  logout() {
    clearToken();
  },


  // ═══════════════════════════════════════════
  // INVENTORY
  // ═══════════════════════════════════════════

  /**
   * List/search inventory
   * @param {Object} params - { search, inventory_type, sort_by, sort_dir, page, per_page }
   */
  async getInventory(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.set('search', params.search);
    if (params.inventory_type) query.set('inventory_type', params.inventory_type);
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.sort_dir) query.set('sort_dir', params.sort_dir);
    if (params.page) query.set('page', params.page);
    if (params.per_page) query.set('per_page', params.per_page);
    return apiFetch(`/inventory?${query.toString()}`);
  },

  /** Get single item */
  async getItem(itemId) {
    return apiFetch(`/inventory/item/${itemId}`);
  },

  /** Add new item */
  async addItem(itemData) {
    return apiFetch('/inventory', {
      method: 'POST',
      body: JSON.stringify(itemData),
    });
  },

  /** Update item */
  async updateItem(itemId, itemData) {
    return apiFetch(`/inventory/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(itemData),
    });
  },

  /** Delete item (soft delete) */
  async deleteItem(itemId) {
    return apiFetch(`/inventory/${itemId}`, {
      method: 'DELETE',
    });
  },

  /** Use/withdraw from item */
  async useItem(itemId, amount, purpose = '') {
    return apiFetch(`/inventory/${itemId}/use`, {
      method: 'POST',
      body: JSON.stringify({ amount, purpose }),
    });
  },

  /** Check for duplicate before adding */
  async checkDuplicate(catalogNumber, name, excludeId = null) {
    const query = new URLSearchParams();
    if (catalogNumber) query.set('catalog_number', catalogNumber);
    if (name) query.set('name', name);
    if (excludeId) query.set('exclude_id', excludeId);
    return apiFetch(`/inventory/check-duplicate?${query.toString()}`);
  },


  // ═══════════════════════════════════════════
  // ALERTS & STATS
  // ═══════════════════════════════════════════

  /** Get low stock + expired alerts */
  async getAlerts() {
    return apiFetch('/inventory/alerts');
  },

  /** Get dashboard statistics */
  async getStats() {
    return apiFetch('/inventory/stats');
  },


  // ═══════════════════════════════════════════
  // CATALOG (auto-populate)
  // ═══════════════════════════════════════════

  /** Look up catalog number for auto-fill */
  async lookupCatalog(catalogNumber) {
    return apiFetch(`/inventory/catalog/${encodeURIComponent(catalogNumber)}`);
  },


  // ═══════════════════════════════════════════
  // ACTIVITY LOG
  // ═══════════════════════════════════════════

  /** Get activity log */
  async getActivity(limit = 50, actionType = null) {
    const query = new URLSearchParams({ limit });
    if (actionType) query.set('action_type', actionType);
    return apiFetch(`/activity?${query.toString()}`);
  },


  // ═══════════════════════════════════════════
  // EXPORT
  // ═══════════════════════════════════════════

  /** Export inventory as CSV (returns Blob) */
  async exportCSV() {
    const blob = await apiFetch('/inventory/export/csv');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mehal_lab_inventory_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },
};

export default api;


// ═══════════════════════════════════════════
// EXAMPLE: How to refactor the React component
// ═══════════════════════════════════════════
//
// In LabInventorySystem.jsx, replace the in-memory state with API calls:
//
// 1. LOGIN:
//    Replace:  const user = USERS_DB.find(...)
//    With:     const data = await api.login(username, password);
//              const user = await api.getMe();
//
// 2. LOAD INVENTORY:
//    useEffect(() => {
//      api.getInventory({ search, inventory_type: typeFilter.join(','), 
//                         sort_by: sortField, sort_dir: sortDir, page: currentPage })
//        .then(data => {
//          setInventory(data.items);
//          setTotalPages(data.total_pages);
//        });
//    }, [search, typeFilter, sortField, sortDir, currentPage]);
//
// 3. ADD ITEM:
//    Replace:  setInventory(prev => [...prev, item])
//    With:     const newItem = await api.addItem(itemData);
//              setInventory(prev => [...prev, newItem]);
//
// 4. CATALOG AUTO-POPULATE:
//    Replace:  const match = CATALOG_DB[val]
//    With:     try {
//                const match = await api.lookupCatalog(val);
//                setForm(prev => ({ ...prev, name: match.name, ... }));
//              } catch { /* not found */ }
//
// 5. DUPLICATE CHECK:
//    Replace:  const existing = inventory.find(...)
//    With:     const result = await api.checkDuplicate(catalogNumber, name);
//              if (result.is_duplicate) setDuplicateWarning(result);
//
// 6. USE/WITHDRAW:
//    Replace:  setInventory(prev => prev.map(...))
//    With:     const updated = await api.useItem(item.id, amount, purpose);
//
// 7. DELETE:
//    Replace:  setInventory(prev => prev.filter(...))
//    With:     await api.deleteItem(item.id);
//
// 8. EXPORT CSV:
//    Replace:  the blob logic
//    With:     await api.exportCSV();
