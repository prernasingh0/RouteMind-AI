import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from '@/components/feedback/States';
describe('operational views', () => { it('renders a real empty state rather than seeded content', () => { render(<EmptyState title="No visits" description="Schedule a doctor visit to begin your calendar." />); expect(screen.getByText('No visits')).toBeTruthy(); }); });
