import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { VehicleCard } from './VehicleCard';
const vehicle = { id:'1', make:'Tata', model:'Nexon', category:'SUV', price:1450000, quantity:3, year:2026, fuel:'Petrol', color:'Blue' };
describe('Vehicle card', () => {
  it('disables purchase when stock is zero', () => {
    render(<VehicleCard car={{...vehicle,quantity:0}} onPurchase={vi.fn()} />);
    expect(screen.getByRole('button', {name:/out of stock/i})).toBeDisabled();
  });
  it('opens purchase with the selected vehicle', () => {
    const buy=vi.fn(); render(<VehicleCard car={vehicle} onPurchase={buy} />);
    fireEvent.click(screen.getByRole('button', {name:/purchase/i}));
    expect(buy).toHaveBeenCalledWith(vehicle);
  });
  it('only shows inventory controls for administrators', () => {
    const {rerender}=render(<VehicleCard car={vehicle} onPurchase={vi.fn()} />);
    expect(screen.queryByRole('button', {name:/edit/i})).not.toBeInTheDocument();
    rerender(<VehicleCard car={vehicle} admin onPurchase={vi.fn()} onEdit={vi.fn()} onRestock={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByRole('button', {name:/edit/i})).toBeEnabled();
    expect(screen.getByRole('button', {name:/restock/i})).toBeEnabled();
    expect(screen.getByRole('button', {name:/delete/i})).toBeEnabled();
  });
});
