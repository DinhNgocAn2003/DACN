import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';

const Layout = ({ user, setUser }) => {
  return (
    <div className="layout">
      <Header user={user} setUser={setUser} />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;