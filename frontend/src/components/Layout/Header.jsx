import React, { useState } from 'react';
import { logout } from '../../services/auth';
import ConfirmationModal from '../Common/ConfirmationModal';
import { useToast } from '../Common/ToastProvider';
import SearchBar from '../Common/SearchBar';

const Header = ({ user, setUser }) => {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const { showToast } = useToast();

  const handleLogout = () => {
    setConfirmOpen(true);
  };

  const confirmLogout = () => {
    logout();
    setUser(null);
    setConfirmOpen(false);
    showToast({ type: 'success', message: 'Bạn đã đăng xuất thành công' });
  };

  return (
    <>
      <header className="header">
        <div className="header-content">
          <h1>Trợ lý lịch trình</h1>
          <div style={{ marginLeft: '1rem', flex: 1 }}>
            <SearchBar />
          </div>
          <div className="user-info">
            <div>Xin chào,{user?.username} </div>
            <button onClick={handleLogout} className="btn-logout">
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      <ConfirmationModal
        isOpen={confirmOpen}
        title="Xác nhận đăng xuất"
        message="Bạn có chắc muốn đăng xuất khỏi tài khoản không?"
        onConfirm={confirmLogout}
        onCancel={() => setConfirmOpen(false)}
        confirmLabel="Đăng xuất"
        cancelLabel="Hủy"
      />
    </>
  );
};

export default Header;