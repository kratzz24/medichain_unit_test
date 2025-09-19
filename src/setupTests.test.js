describe('setupTests.js environment', () => {
  test('TextEncoder and TextDecoder are defined', () => {
    expect(global.TextEncoder).toBeDefined();
    expect(global.TextDecoder).toBeDefined();
  });

  test('ReadableStream is defined', () => {
    expect(global.ReadableStream).toBeDefined();
  });

  test('fetch is mocked', () => {
    expect(global.fetch).toBeDefined();
    expect(jest.isMockFunction(global.fetch)).toBe(true);
  });

  test('localStorage is mocked', () => {
    expect(global.localStorage).toBeDefined();
    expect(typeof global.localStorage.getItem).toBe('function');
    expect(jest.isMockFunction(global.localStorage.getItem)).toBe(true);
  });

  test('sessionStorage is mocked', () => {
    expect(global.sessionStorage).toBeDefined();
    expect(typeof global.sessionStorage.getItem).toBe('function');
    expect(jest.isMockFunction(global.sessionStorage.getItem)).toBe(true);
  });

  test('window.navigator is mocked', () => {
    expect(window.navigator.userAgent).toBe('Jest');
    expect(window.navigator.platform).toBe('Node.js');
  });

  test('IntersectionObserver is mocked', () => {
    expect(global.IntersectionObserver).toBeDefined();
    const observer = new global.IntersectionObserver();
    expect(observer.observe()).toBeNull();
    expect(observer.disconnect()).toBeNull();
    expect(observer.unobserve()).toBeNull();
  });
});
