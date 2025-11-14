import React from 'react';
import { logout } from '../../services/auth';

const Header = ({ user, setUser }) => {
  const handleLogout = () => {
    logout();
    setUser(null);
  };

  return (
    <header className="header">
      <div className="header-content">
        <h1>Trợ lý sự kiện</h1>
        <div className="user-info">
          <span>Xin chào, {user?.username}</span>
          <button onClick={handleLogout} className="btn-logout">
            Đăng xuất
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;