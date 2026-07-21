import React, { createContext, useContext, useState } from 'react';

const NotificationContext = createContext({
  notifications: [],
  unreadCount: 0,
  addNotification: () => {},
  markAllAsRead: () => {}
});

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Critical Alert', message: 'Impossible travel login detected for usr_abc', time: '10:00:00', read: false },
    { id: 2, title: 'Mule Ring Alert', message: 'ACC_MULE_NEW matched cluster_alpha', time: '10:00:40', read: false },
    { id: 3, title: 'TLS Posture Warning', message: 'ECDHE cipher flagged HNDL risk', time: '09:50:00', read: true }
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const addNotification = (notif) => {
    setNotifications(prev => [{ id: Date.now(), read: false, time: new Date().toLocaleTimeString(), ...notif }, ...prev]);
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  return (
    <NotificationContext.Provider value={{ notifications, unreadCount, addNotification, markAllAsRead }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  return useContext(NotificationContext);
}
