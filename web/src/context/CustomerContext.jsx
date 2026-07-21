import React, { createContext, useContext, useState } from 'react';

const CustomerContext = createContext({
  activeCustomerId: 'usr_abc',
  customerProfile: null,
  selectCustomer: () => {}
});

export function CustomerProvider({ children }) {
  const [activeCustomerId, setActiveCustomerId] = useState('usr_abc');
  const [customerProfile, setCustomerProfile] = useState({
    id: 'usr_abc',
    name: 'Rajesh Kumar',
    primaryAccount: 'ACC_ABC_123',
    riskScore: 94,
    riskGrade: 'CRITICAL',
    status: 'COMPROMISED',
    location: 'Mumbai, IN',
    balance: '₹1,450,000.00'
  });

  const selectCustomer = (customerId) => {
    setActiveCustomerId(customerId);
    setCustomerProfile(prev => ({ ...prev, id: customerId }));
  };

  return (
    <CustomerContext.Provider value={{ activeCustomerId, customerProfile, selectCustomer }}>
      {children}
    </CustomerContext.Provider>
  );
}

export function useCustomer() {
  return useContext(CustomerContext);
}
