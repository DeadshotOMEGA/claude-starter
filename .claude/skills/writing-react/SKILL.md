---
name: writing-react
description: Modern React patterns with hooks, context, and component architecture. Use when building React components, managing state, or optimizing React performance.
---

# Writing React Components

## Component Architecture

### Hooks-based Components
```tsx
interface Props {
  title: string;
  onAction?: (id: string) => void;
}

export const MyComponent: React.FC<Props> = ({ title, onAction }) => {
  const [state, setState] = useState(false);

  return <div>{title}</div>;
};
```

### Composition Over Props Drilling
```tsx
// Use context or compound components to avoid deep prop passing
const FeatureContext = createContext<FeatureAPI | null>(null);

export const Provider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <FeatureContext.Provider value={api}>
    {children}
  </FeatureContext.Provider>
);
```

## State Management

### Local Component State
- `useState` for simple, isolated state
- Multiple `useState` calls for independent concerns
- Lift state up only when needed by siblings

### Complex State Logic
```tsx
const [state, dispatch] = useReducer(reducer, initialState);
```

### Shared State
- **Context API**: Small apps, moderate data, non-performance-critical
- **Zustand**: Simpler Redux alternative, lightweight
- **Redux**: Complex domain logic, time-travel debugging required
- **External stores**: Tanstack Query for server state

### Context Best Practice
```tsx
// Create separate contexts for updates vs. values
const ValueContext = createContext(initialValue);
const UpdateContext = createContext<UpdateFunctions | null>(null);
```

## Performance Patterns

### Memoization
```tsx
// Memoize expensive components
const Item = React.memo(({ id, data }: Props) => {
  return <div>{data.name}</div>;
}, (prev, next) => prev.id === next.id && prev.data === next.data);

// Memoize computations
const sorted = useMemo(() => items.sort(...), [items]);

// Memoize callbacks (only if passed to memoized children)
const handleClick = useCallback(() => { ... }, [dependency]);
```

### Code Splitting & Lazy Loading
```tsx
const HeavyComponent = lazy(() => import('./Heavy'));

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

### Avoid Unnecessary Renders
- Keep component tree shallow
- Extract static content outside JSX
- Use key prop correctly in lists (stable IDs, not indices)
- Split large components into smaller, focused ones

## Props Interface Conventions

```tsx
// Extend HTML attributes when applicable
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

// Use discriminated unions for variant patterns
type MessageProps =
  | { type: 'success'; message: string }
  | { type: 'error'; error: Error };
```

## Key Patterns

- **Component-first**: Reusable, composable, single responsibility
- **Mobile-first**: Responsive design approach
- **Performance budgets**: Sub-3s load times, lazy load non-critical features
- **Type safety**: Explicit prop types, no `any`
- **Semantic HTML**: Proper elements, ARIA labels for accessibility
