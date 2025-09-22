import { render, screen } from '@testing-library/react';
import App from './App';
import { UNSAFE_enableFutureFlag } from 'react-router';

// Enable future flags to suppress warnings
UNSAFE_enableFutureFlag('v7_startTransition');
UNSAFE_enableFutureFlag('v7_relativeSplatPath');

test('renders MediChain app', () => {
  render(<App />);
  const linkElements = screen.getAllByText(/MEDICHAIN/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
