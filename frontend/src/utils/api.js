const getHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
};

export const apiGet = async (path) => {
  try {
    const res = await fetch(`/api${path}`, {
      headers: getHeaders(),
    });
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
      return null;
    }
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'API request failed');
    }
    return await res.json();
  } catch (error) {
    console.error('API GET error:', error);
    throw error;
  }
};

export const apiPost = async (path, data) => {
  try {
    const res = await fetch(`/api${path}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
      return null;
    }
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'API request failed');
    }
    return await res.json();
  } catch (error) {
    console.error('API POST error:', error);
    throw error;
  }
};

export const apiPatch = async (path, data) => {
  try {
    const res = await fetch(`/api${path}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
      return null;
    }
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'API request failed');
    }
    return await res.json();
  } catch (error) {
    console.error('API PATCH error:', error);
    throw error;
  }
};

export const apiDelete = async (path) => {
  try {
    const res = await fetch(`/api${path}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
      return null;
    }
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'API request failed');
    }
    return true;
  } catch (error) {
    console.error('API DELETE error:', error);
    throw error;
  }
};
