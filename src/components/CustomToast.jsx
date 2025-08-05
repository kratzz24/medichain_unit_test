import React from 'react';
import './CustomToast.css';

// Simple icon components (no external dependencies)
const CheckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 6L9 17l-5-5"/>
  </svg>
);

const AlertIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

const InfoIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4"/>
    <path d="M12 8h.01"/>
  </svg>
);

// Custom toast components
const ToastSuccess = ({ message }) => (
  <div className="custom-toast custom-toast-success">
    <CheckIcon />
    <span>{message}</span>
  </div>
);

const ToastError = ({ message }) => (
  <div className="custom-toast custom-toast-error">
    <AlertIcon />
    <span>{message}</span>
  </div>
);

const ToastInfo = ({ message }) => (
  <div className="custom-toast custom-toast-info">
    <InfoIcon />
    <span>{message}</span>
  </div>
);

// Simple toast implementation without external libraries
let toastContainer = null;
let toastIdCounter = 0;

const createToastContainer = () => {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 9999;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
};

const showToastElement = (element, duration = 3000) => {
  const container = createToastContainer();
  const toastId = `toast-${++toastIdCounter}`;
  
  const toastWrapper = document.createElement('div');
  toastWrapper.id = toastId;
  toastWrapper.style.cssText = `
    margin-bottom: 0.5rem;
    pointer-events: auto;
    animation: slideInToast 0.3s ease-out;
  `;
  
  // Add slide-in animation styles
  if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
      @keyframes slideInToast {
        from {
          opacity: 0;
          transform: translateX(100%);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      @keyframes slideOutToast {
        from {
          opacity: 1;
          transform: translateX(0);
        }
        to {
          opacity: 0;
          transform: translateX(100%);
        }
      }
    `;
    document.head.appendChild(style);
  }
  
  // Render React element to DOM
  const tempDiv = document.createElement('div');
  const reactRoot = React.createElement('div', {}, element);
  
  // Simple render without ReactDOM
  tempDiv.innerHTML = `
    <div class="${element.props.className}">
      ${element.props.children.map(child => {
        if (typeof child === 'string') return child;
        if (child.type === CheckIcon) return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>';
        if (child.type === AlertIcon) return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
        if (child.type === InfoIcon) return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>';
        return child.props ? child.props.children : '';
      }).join('')}
    </div>
  `;
  
  toastWrapper.appendChild(tempDiv.firstChild);
  container.appendChild(toastWrapper);
  
  // Auto remove after duration
  setTimeout(() => {
    if (toastWrapper && toastWrapper.parentNode) {
      toastWrapper.style.animation = 'slideOutToast 0.3s ease-in';
      setTimeout(() => {
        if (toastWrapper && toastWrapper.parentNode) {
          toastWrapper.parentNode.removeChild(toastWrapper);
        }
      }, 300);
    }
  }, duration);
  
  return toastId;
};

// Simplified toast functions
export const showToast = {
  success: (message) => {
    const toastElement = React.createElement(ToastSuccess, { message });
    showToastElement(toastElement, 3000);
  },
  
  error: (message) => {
    const toastElement = React.createElement(ToastError, { message });
    showToastElement(toastElement, 4000);
  },
  
  info: (message) => {
    const toastElement = React.createElement(ToastInfo, { message });
    showToastElement(toastElement, 3000);
  }
};

// Alternative simple implementation
export const simpleToast = {
  success: (message) => {
    console.log('✅ SUCCESS:', message);
    alert(`✅ ${message}`);
  },
  
  error: (message) => {
    console.log('❌ ERROR:', message);
    alert(`❌ ${message}`);
  },
  
  info: (message) => {
    console.log('ℹ️ INFO:', message);
    alert(`ℹ️ ${message}`);
  }
};

export default { showToast, simpleToast };
