// Simple add function for demonstration
function add(a, b) {
  return a + b;
}

describe('Basic arithmetic', () => {
  test('adds 2 + 2 to equal 4', () => {
    expect(2 + 2).toBe(4);
  });
});

test('adds 1 + 2 to equal 3', () => {
  expect(1 + 2).toBe(3);
});

describe('add', () => {
  test('adds 2 + 3 to equal 5', () => {
    expect(add(2, 3)).toBe(5);
  });
});
