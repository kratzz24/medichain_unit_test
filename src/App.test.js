import { render, screen } from '@testing-library/react';
import App from './App';

beforeAll(() => {
  jest.spyOn(console, 'warn').mockImplementation((message) => {
    if (
      message.includes('React Router Future Flag Warning') ||
      message.includes('Relative route resolution within Splat routes')
    ) {
      return;
    }
    console.warn(message);
  });
});

test('renders MediChain app', () => {
  render(<App />);
  const linkElements = screen.getAllByText(/MEDICHAIN/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
